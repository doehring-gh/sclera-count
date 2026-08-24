#!/usr/bin/env python3
"""
export_consent.py -- write the information-and-consent page out as a document for
the ethics application, taken from the app itself.

    /usr/bin/python3 tools/export_consent.py --out ethics/CONSENT_PAGE_v1.0.html

The committee is shown exactly what participants are shown, because both come
from the same source. Editing the wording in docs/index.html and re-running this
keeps them identical; there is no second copy to forget to update.
"""
import argparse, html, json, re, sys
from pathlib import Path

APP = Path(__file__).resolve().parent.parent / "docs" / "index.html"
TICKS = ["cons.t1", "cons.t2", "cons.t3", "cons.t4", "cons.t5", "cons.t6"]
BLOCKS = [("cons.aboutHead", "cons.about"),
          ("cons.involveHead", "cons.involve"),
          ("cons.moreHead", "cons.full")]


def load_strings(src, lang):
    """Pull one language block out of the app's translation table."""
    i = src.index(f'\n{lang}: {{')
    j = src.index("\n}};", i) if lang == "de" else src.index('\n},\nde: {', i)
    block = src[i:j]
    out = {}
    for m in re.finditer(r'"([A-Za-z0-9._]+)"\s*:\s*"((?:[^"\\]|\\.)*)"', block):
        # json.loads handles the JS string escapes (\" \\ \n) while leaving real
        # UTF-8 alone. unicode_escape does not -- it turns em-dashes and umlauts
        # into mojibake, which is wrong on a document participants have to read.
        out[m.group(1)] = json.loads('"' + m.group(2) + '"')
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", default="1.0")
    p.add_argument("--date", default="[date]")
    p.add_argument("--out", type=Path, default=Path("ethics/CONSENT_PAGE_v1.0.html"))
    args = p.parse_args()

    src = APP.read_text()
    langs = {"en": load_strings(src, "en"), "de": load_strings(src, "de")}
    missing = [k for L in langs.values() for k in TICKS + [b for pair in BLOCKS for b in pair]
               if k not in L]
    if missing:
        sys.exit(f"missing strings in the app: {sorted(set(missing))}")

    parts = ["""<!doctype html><meta charset="utf-8">
<title>Participant information and consent</title>
<style>
 body{font:15px/1.6 Georgia,serif;max-width:44em;margin:2.5em auto;padding:0 1.5em;color:#111}
 h1{font-size:22px} h2{font-size:16px;margin-top:1.8em;text-transform:uppercase;
    letter-spacing:.05em;color:#555} h3{font-size:15px;margin:1.2em 0 .3em}
 .meta{color:#555;font-size:13px;border-bottom:1px solid #ccc;padding-bottom:1em}
 ol{padding-left:1.4em} ol li{margin-bottom:.9em}
 .note{background:#f4f7fb;border-left:3px solid #2f6fed;padding:.9em 1.1em;font-size:14px}
 code{font-family:ui-monospace,Menlo,monospace}
 .lang{page-break-before:always;border-top:2px solid #111;margin-top:3em;padding-top:2em}
 /* printed for the ethics upload: no browser chrome, and headings kept with
    the text that follows them */
 @page{margin:16mm 14mm;size:A4}
 @media print{ body{margin:0;max-width:none;font-size:11pt}
               h1,h2,h3{break-after:avoid} .note{break-inside:avoid} }
</style>"""]

    parts.append(f"""<h1>Participant information and consent</h1>
<p class="meta">Inter- and intra-observer reliability of manual live/dead cell
counting in confocal images of scleral tissue (SCLERA-LIVE)<br>
Consent version <b>{html.escape(args.version)}</b> · {html.escape(args.date)} ·
Principal Investigator: Dr Daniela Oehring</p>

<div class="note"><b>This is the screen participants see before the tool will
open.</b> It is generated from the application source, so the wording here and the
wording on screen cannot differ. Participants must tick every statement
individually before the button that starts the task becomes active; nothing is
recorded until they do. What is stored is that each statement was confirmed, with
a timestamp, the consent version, and the participant's self-generated code —
never their identity.</div>""")

    for lang, label in (("en", "English"), ("de", "Deutsch — German version as shown to participants")):
        L = langs[lang]
        parts.append(f'<div class="lang"><h1>{label}</h1>' if lang != "en" else "")
        parts.append(f"<h2>{html.escape(L['cons.title'])}</h2>")
        for head, body in BLOCKS:
            parts.append(f"<h2>{html.escape(L[head])}</h2>\n{L[body]}")
        parts.append(f"<h2>{html.escape(L['cons.agreeHead'])}</h2><ol>")
        parts.extend(f"<li>{L[k]}</li>" for k in TICKS)
        parts.append("</ol>")
        parts.append(f"<p><b>[ {html.escape(L['cons.go'])} ]</b> &nbsp; "
                     f"[ {html.escape(L['cons.decline'])} ]</p>")
        parts.append(f"<p style='font-size:13px;color:#555'>{html.escape(L['cons.recordNote'])}</p>")
        parts.append(f"<p style='font-size:13px;color:#555'>{html.escape(L['cons.contact'])}</p>")
        if lang != "en":
            parts.append("</div>")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(x for x in parts if x))
    print(f"wrote {args.out}")
    print(f"  {len(TICKS)} consent statements, English and German, "
          f"consent version {args.version}")
    print("  open it in a browser and print to PDF for the ethics upload")


if __name__ == "__main__":
    sys.exit(main())
