#!/usr/bin/env python3
"""
fill_docx.py -- fill the University templates in place, rather than producing
look-alike documents.

The templates carry the University header image, fonts, page setup and — for the
risk assessment — the scoring matrix and descriptor tables. Regenerating those
from scratch would lose them, so this edits the original files: it replaces the
text inside specific table cells, and for the prose template it swaps the body
paragraphs while keeping the section properties, header and styles intact.

Everything is done by careful string surgery on word/document.xml. ElementTree
round-tripping is avoided because it rewrites the many namespace prefixes a .docx
carries and readily produces a file Word will not open.
"""
import re
import shutil
import zipfile
from pathlib import Path

W = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'


# ----------------------------------------------------------------- xml helpers
def esc(t):
    return (t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def para(text="", bold=False, size=None, align=None, space_after=120):
    """One <w:p>. **bold** inside text toggles bold runs."""
    ppr = "<w:pPr>"
    if align:
        ppr += f'<w:jc w:val="{align}"/>'
    ppr += f'<w:spacing w:after="{space_after}"/>'
    ppr += "</w:pPr>"

    runs = ""
    for i, chunk in enumerate(re.split(r"\*\*", text)):
        if not chunk:
            continue
        b = bold or (i % 2 == 1)
        rpr = "<w:rPr>"
        if b:
            rpr += "<w:b/>"
        if size:
            rpr += f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>'
        rpr += "</w:rPr>"
        runs += (f"<w:r>{rpr}<w:t xml:space=\"preserve\">{esc(chunk)}</w:t></w:r>")
    return f"<w:p>{ppr}{runs}</w:p>"


def heading(text, size=28):
    return para(text, bold=True, size=size, space_after=160)


def bullet(text):
    ppr = ('<w:pPr><w:ind w:left="360" w:hanging="180"/>'
           '<w:spacing w:after="80"/></w:pPr>')
    runs = ""
    for i, chunk in enumerate(re.split(r"\*\*", "•  " + text)):
        if not chunk:
            continue
        rpr = "<w:rPr><w:b/></w:rPr>" if i % 2 == 1 else ""
        runs += f'<w:r>{rpr}<w:t xml:space="preserve">{esc(chunk)}</w:t></w:r>'
    return f"<w:p>{ppr}{runs}</w:p>"


# --------------------------------------------------------------- table surgery
def spans(xml, tag):
    """Start/end offsets of each top-level <tag>…</tag>, allowing for nesting."""
    out, i = [], 0
    open_re = re.compile(rf"<{tag}(?:\s[^>]*)?>")
    close = f"</{tag}>"
    while True:
        m = open_re.search(xml, i)
        if not m:
            return out
        depth, j = 1, m.end()
        while depth:
            nxt_o = open_re.search(xml, j)
            nxt_c = xml.find(close, j)
            if nxt_c == -1:
                return out
            if nxt_o and nxt_o.start() < nxt_c:
                depth += 1; j = nxt_o.end()
            else:
                depth -= 1; j = nxt_c + len(close)
        out.append((m.start(), j))
        i = j


def set_cell(xml, t_i, r_i, c_i, paragraphs):
    """Replace the contents of one table cell, keeping its <w:tcPr>."""
    tbl = spans(xml, "w:tbl")[t_i]
    tblx = xml[tbl[0]:tbl[1]]
    row = spans(tblx, "w:tr")[r_i]
    rowx = tblx[row[0]:row[1]]
    cell = spans(rowx, "w:tc")[c_i]
    cellx = rowx[cell[0]:cell[1]]

    m = re.search(r"<w:tcPr>.*?</w:tcPr>", cellx, re.S)
    tcpr = m.group(0) if m else ""
    body = "".join(paragraphs) or para("")
    new_cell = f"<w:tc>{tcpr}{body}</w:tc>"

    rowx = rowx[:cell[0]] + new_cell + rowx[cell[1]:]
    tblx = tblx[:row[0]] + rowx + tblx[row[1]:]
    return xml[:tbl[0]] + tblx + xml[tbl[1]:]


def replace_body(xml, paragraphs):
    """Swap every paragraph in the body, keeping <w:sectPr> (page setup, header)."""
    b0 = xml.index("<w:body>") + len("<w:body>")
    b1 = xml.rindex("</w:body>")
    body = xml[b0:b1]
    m = re.search(r"<w:sectPr[\s>].*?</w:sectPr>", body, re.S)
    sect = m.group(0) if m else ""
    return xml[:b0] + "".join(paragraphs) + sect + xml[b1:]


def write_docx(src, dst, new_document_xml):
    shutil.copyfile(src, dst)
    with zipfile.ZipFile(src) as zin:
        items = [(i, zin.read(i.filename)) for i in zin.infolist()]
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for info, data in items:
            if info.filename == "word/document.xml":
                data = new_document_xml.encode("utf-8")
            zout.writestr(info, data)


def read_document(src):
    with zipfile.ZipFile(src) as z:
        return z.read("word/document.xml").decode("utf-8")
