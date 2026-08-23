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

var SUMMARY_SHEET = 'summary';
var MARKERS_SHEET = 'markers';

var SUMMARY_COLS = ['received_utc', 'study', 'rater', 'block', 'mode', 'field', 'square',
  'segment', 'n_total', 'n_cell', 'n_live', 'n_dead', 'n_unsure', 'empty', 'seconds',
  'brightness', 'contrast', 'note', 'app_version', 'started_utc'];

var MARKER_COLS = ['received_utc', 'study', 'rater', 'block', 'mode', 'field', 'square',
  'segment', 'marker', 'label', 'x_tile_px', 'y_tile_px', 'x_field_px', 'y_field_px',
  'marked_utc'];

function doPost(e) {
  var lock = LockService.getScriptLock();
  lock.waitLock(30000);                    // serialise concurrent counters
  try {
    var payload = JSON.parse(e.postData.contents);
    var stamp = new Date().toISOString();

    var nSum = writeRows(SUMMARY_SHEET, SUMMARY_COLS, payload.summary || [], stamp);
    var nMk = writeRows(MARKERS_SHEET, MARKER_COLS, payload.markers || [], stamp);

    return json({ok: true, summary_rows: nSum, marker_rows: nMk});
  } catch (err) {
    return json({ok: false, error: String(err)});
  } finally {
    lock.releaseLock();
  }
}

function doGet() {
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
              r.marker == null ? '' : r.marker].join('')] = true;
  });

  var last = sh.getLastRow();
  if (last > 1) {
    var existing = sh.getRange(2, 1, last - 1, cols.length).getValues();
    var doomed = [];
    for (var i = 0; i < existing.length; i++) {
      var row = existing[i];
      var k = [row[idx.rater], row[idx.block], row[idx.mode], row[idx.segment],
               idx.marker === undefined ? '' : row[idx.marker]].join('');
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
