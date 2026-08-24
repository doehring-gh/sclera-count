#!/usr/bin/env python3
"""Fill the University consent form template for this study.

The template's identity fields are deliberately not completed. Recording a name
and signature would create the link between participant and data that this study
is designed not to hold, converting anonymous data into personal data. Consent is
taken instead as an on-screen confirmation. Rather than silently deleting those
fields, the form states why they are empty, so the committee sees a decision
rather than an omission.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fill_docx import read_document, write_docx, set_cell, para

ETH = Path(__file__).resolve().parent.parent / "ethics"
SRC = ETH / "2026 ICF Template V2.0.docx"
DST = ETH / "Consent Form - SCLERA-LIVE v1.0.docx"

NOTE = ("NOT COLLECTED — this study is anonymous. Recording a name here would "
        "create a link between the participant and their data that does not "
        "otherwise exist, and would convert anonymous data into personal data. "
        "Consent is recorded instead as an on-screen confirmation before the task "
        "will open, with a timestamp and consent version. This form documents the "
        "statements consented to; it is not signed by the participant.")

IDENT = ("Identification number for this study: the participant's own "
         "self-generated code, for example amber-larch-63, which is known only to "
         "them and is not held in any list.")

# table 2 — taking part
T2 = {
 2: "I confirm that I have read the Participant Information Sheet dated ‹date› "
    "(version V1.0_observers) for the above study. I have had the opportunity to "
    "consider the information, ask questions and have had these answered "
    "satisfactorily.",
 3: "I understand that my participation is voluntary and that I am free to withdraw "
    "at any time without giving any reason, without my rights being affected.",
 4: "I understand that taking part in the study involves viewing small sections of "
    "microscope images on my own device and clicking on each cell I can see to record "
    "whether I think it is alive, dead, or uncertain, and that this takes about 20 to "
    "40 minutes. I understand that some images are repeated on purpose so the study "
    "can measure how consistent I am with myself, and that I must reach a set level of "
    "agreement in a practice round before my counts are included — with unlimited "
    "attempts, no penalty, and no report of my performance to anyone.",
 5: "I agree to take part in the above study, and I am 18 years of age or over.",
}

# table 3 — use of the information
T3 = {
 1: "I understand that the information I provide will be used in scientific "
    "publications, conference presentations, and a plain-language summary made "
    "available online.",
 2: "I understand that relevant sections of my data collected during the study may be "
    "looked at by individuals from the University of Plymouth or regulatory "
    "authorities where it is appropriate to my taking part in this research. I permit "
    "these individuals to have access to my records.",
}

# table 4 — future use and sharing
T4 = {
 1: "I give permission for the anonymous annotation data that I provide to be "
    "deposited in a public data repository so it can be used for future research and "
    "learning.",
 2: "I understand that the anonymous information collected about me will be used to "
    "support other research in the future and may be shared with other researchers.",
 3: "I understand that no information identifying me is collected, that my answers are "
    "labelled only with a code I generate at the start, and that I must keep that code "
    "because it is the only way my data could later be found and deleted — up to "
    "‹withdrawal cut-off date›, after which results are combined for publication and "
    "individual answers can no longer be separated out.",
}


def main():
    if not SRC.exists():
        sys.exit(f"template not found: {SRC}")
    xml = read_document(SRC)

    xml = set_cell(xml, 0, 0, 0, [
        para("Full name of participant (and / or guardian):", bold=True),
        para(NOTE)])
    xml = set_cell(xml, 1, 0, 0, [para(IDENT)])

    for tbl, rows in ((2, T2), (3, T3), (4, T4)):
        for r, text in rows.items():
            xml = set_cell(xml, tbl, r, 0, [para(text)])

    write_docx(SRC, DST, xml)
    print(f"wrote {DST.name}")
    print(f"  {len(T2)+len(T3)+len(T4)} consent statements filled")
    print("  identity fields left empty on purpose, with the reason stated on the form")


if __name__ == "__main__":
    sys.exit(main())
