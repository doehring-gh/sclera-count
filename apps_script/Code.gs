/**
 * SCLERA cell count -- collection endpoint.
 *
 * Receives one counter's results from docs/index.html and writes them into this
 * spreadsheet. Two sheets are maintained:
 *
 *   summary   one row per counted square
 *   markers   one row per clicked nucleus, with its coordinates
 *
 * Rows are upserted on (rater, block, mode, segment, marker), so a counter who
 * sends progress twice, or comes back and finishes later, replaces their earlier
 * rows instead of duplicating them.
 *
 * ------------------------------------------------------------------- security
 * What is and is not exposed:
 *
 *   The SPREADSHEET is private. Nobody but you can open it, and this script has
 *   no read path -- doGet returns a fixed banner whatever it is asked. Counters
 *   never see the data.
 *
 *   The ENDPOINT is public, because the page that posts to it is a public static
 *   site and there is nowhere in it to hide a secret. Without the keys below,
 *   anyone who found the URL could append junk rows. They still could not read
 *   anything.
 *
 * ACCESS_KEYS closes that. Give each counter a link carrying their own key:
 *
 *     https://.../sclera-count/?rater=Matt&key=k7f3q9x2
 *
 * The key travels only in the link you email, never in the published site, so
 * finding the endpoint is no longer enough to write to it. The row is stamped
 * with the name THIS TABLE gives, not the name typed into the app, so one
 * counter cannot submit under another's name.
 *
 * This is access control, not cryptography: a key sits in that person's browser
 * history and works for anyone they forward the link to. It is proportionate to
 * the risk, which is spam rather than disclosure. Archive the deployment when
 * the round is finished (Deploy > Manage deployments > Archive).
 *
 * Leave ACCESS_KEYS empty to accept anything, which keeps already-sent links
 * working. Populate it before a round that matters.
 *
 * ---------------------------------------------------------------- deployment
 *  1. Open the Google Sheet that should collect the counts.
 *  2. Extensions > Apps Script, and paste this file in place of Code.gs.
 *  3. Deploy > New deployment > type "Web app".
 *       Execute as:      Me
 *       Who has access:  Anyone     (required: counters are not signed in)
 *  4. Copy the /exec URL and rebuild the app with it:
 *       /usr/bin/python3 build_segments.py --endpoint 'https://script.google.com/.../exec'
 *
 * Re-deploy as a NEW VERSION after any edit, or the old code keeps serving.
 */

// key -> the counter it belongs to. Empty object = no key required.
var ACCESS_KEYS = {
  // 'k7f3q9x2': 'Matt',
  // 'm2p8w4v6': 'Thorsten',
  // 'r5t1n7c3': 'Konstantin',
  // 'b9h6d2s8': 'Claudia',
};

// A counter cannot plausibly exceed these in one send. Anything larger is junk.
var MAX_SUMMARY_ROWS = 500;
var MAX_MARKER_ROWS = 20000;

var SUMMARY_SHEET = 'summary';
var MARKERS_SHEET = 'markers';

var SUMMARY_COLS = ['received_utc', 'study', 'rater', 'block', 'mode', 'field', 'square',
  'segment', 'rep', 'position', 'n_total', 'n_cell', 'n_live', 'n_dead', 'n_unsure',
  'empty', 'seconds', 'brightness', 'contrast', 'note', 'app_version', 'started_utc',
  'training_attempts', 'training_count_score', 'training_location_score'];

var MARKER_COLS = ['received_utc', 'study', 'rater', 'block', 'mode', 'field', 'square',
  'segment', 'rep', 'marker', 'label', 'x_tile_px', 'y_tile_px', 'x_field_px',
  'y_field_px', 'marked_utc'];

function doPost(e) {
  var lock = LockService.getScriptLock();
  lock.waitLock(30000);                    // serialise concurrent counters
  try {
    var payload = JSON.parse(e.postData.contents);
    var summary = payload.summary || [];
    var markers = payload.markers || [];

    // ---- access check -------------------------------------------------
    var required = Object.keys(ACCESS_KEYS).length > 0;
    var verifiedName = null;
    if (required) {
      var key = String((payload.session && payload.session.key) || payload.key || '');
      if (!key || !ACCESS_KEYS.hasOwnProperty(key)) {
        return json({ok: false, error: 'not authorised'});
      }
      verifiedName = ACCESS_KEYS[key];
    }

    // ---- shape check --------------------------------------------------
    if (summary.length > MAX_SUMMARY_ROWS || markers.length > MAX_MARKER_ROWS) {
      return json({ok: false, error: 'payload too large'});
    }
    if (!summary.length && !markers.length) {
      return json({ok: false, error: 'nothing to write'});
    }
    var bad = summary.concat(markers).some(function (r) {
      return !r || !r.rater || !r.segment;
    });
    if (bad) {
      return json({ok: false, error: 'rows missing rater or segment'});
    }

    // The key decides whose name goes in the sheet, not the typed one -- but ONLY
    // for the named expert panel.
    //
    // In the participant round the rater IS the anonymous code, and there is
    // deliberately no record anywhere linking that code to a person. Writing a
    // name over it would manufacture exactly that link and destroy the anonymity
    // the study is built on, silently and irreversibly. So refuse, and say why.
    var anonymous = (payload.session && payload.session.identity === 'code') ||
                    summary.concat(markers).some(function (r) {
                      return /^[a-z]+-[a-z]+-\d+$/.test(String(r.rater || ''));
                    });
    if (verifiedName && anonymous) {
      return json({ok: false, error: 'refused: access keys identify the counter, ' +
                   'so they must not be used for the anonymous participant round'});
    }
    if (verifiedName) {
      summary.forEach(function (r) { r.rater = verifiedName; });
      markers.forEach(function (r) { r.rater = verifiedName; });
    }

    var stamp = new Date().toISOString();
    var nSum = writeRows(SUMMARY_SHEET, SUMMARY_COLS, summary, stamp);
    var nMk = writeRows(MARKERS_SHEET, MARKER_COLS, markers, stamp);

    return json({ok: true, summary_rows: nSum, marker_rows: nMk});
  } catch (err) {
    return json({ok: false, error: String(err)});
  } finally {
    lock.releaseLock();
  }
}

function doGet() {
  // Deliberately says nothing about the data. There is no read path.
  return json({ok: true, service: 'SCLERA cell count collector'});
}

function json(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
                       .setMimeType(ContentService.MimeType.JSON);
}

function sheetFor(name, cols) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(name);
  if (!sh) {
    sh = ss.insertSheet(name);
    sh.getRange(1, 1, 1, cols.length).setValues([cols]).setFontWeight('bold');
    sh.setFrozenRows(1);
  }
  return sh;
}

/**
 * Replace any rows already stored for the incoming keys, then append.
 * Identity is (rater, block, mode, segment, marker); marker is blank for
 * summary rows, so one square maps to exactly one summary row per counter.
 */
function writeRows(name, cols, rows, stamp) {
  if (!rows.length) return 0;
  var sh = sheetFor(name, cols);
  var idx = {};
  cols.forEach(function (c, i) { idx[c] = i; });

  var incoming = {};
  rows.forEach(function (r) {
    incoming[[r.rater, r.block, r.mode, r.segment,
              r.marker == null ? '' : r.marker].join('')] = true;
  });

  var last = sh.getLastRow();
  if (last > 1) {
    var existing = sh.getRange(2, 1, last - 1, cols.length).getValues();
    var doomed = [];
    for (var i = 0; i < existing.length; i++) {
      var row = existing[i];
      var k = [row[idx.rater], row[idx.block], row[idx.mode], row[idx.segment],
               idx.marker === undefined ? '' : row[idx.marker]].join('');
      if (incoming[k]) doomed.push(i + 2);
    }
    for (var j = doomed.length - 1; j >= 0; j--) sh.deleteRow(doomed[j]);
  }

  var values = rows.map(function (r) {
    return cols.map(function (c) {
      return c === 'received_utc' ? stamp : (r[c] == null ? '' : r[c]);
    });
  });
  sh.getRange(sh.getLastRow() + 1, 1, values.length, cols.length).setValues(values);
  return values.length;
}
