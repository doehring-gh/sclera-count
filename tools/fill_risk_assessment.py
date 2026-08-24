#!/usr/bin/env python3
"""Fill the University risk assessment template with this study's assessment."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fill_docx import read_document, write_docx, set_cell, para

ETH = Path(__file__).resolve().parent.parent / "ethics"
SRC = ETH / "Risk Assessment Form (MASTER COPY PLEASE DOWNLOAD).docx"
DST = ETH / "Risk Assessment - SCLERA-LIVE observer study v1.0.docx"

TBD = "‹to be completed›"

HEADER = {  # (row, cell): text
    (0, 1): "‹ref›", (0, 3): "1.0",
    (1, 1): ("Online observer study. Adult volunteers view small sections of "
             "existing confocal microscope images of porcine scleral tissue in a web "
             "browser on their own device, and click on each cell to record whether it "
             "appears alive, dead, or uncertain. Approximately 20–40 minutes per "
             "participant, undertaken remotely at a time and place of the participant's "
             "choosing. No laboratory work, no fieldwork, no in-person participant "
             "contact, no human tissue, and no new animal tissue collection. Also covers "
             "the researcher-facing computer-based development and analysis work."),
    (3, 1): TBD, (3, 3): "Faculty of Health",
    (4, 1): "‹review in 12 months, or on any material change›",
    (4, 3): "School of Health Professions",
    (5, 1): "Dr Daniela Oehring", (5, 3): TBD,
    (6, 1): TBD, (6, 3): TBD,
}

# hazard, who/how, existing controls, L, S, RS, further action, tL, tS, tRS
HAZARDS = [
    ("Display screen use — eye strain, fatigue, postural discomfort",
     "Participants, from approximately 20–40 minutes of close visual attention to "
     "a screen. Aggravated by small or dim image detail.",
     "Task is designed to be interruptible: progress saves continuously and "
     "participants can stop and resume at any point, so no unbroken session is "
     "required. Images can be zoomed and their brightness and contrast adjusted. The "
     "Participant Information Sheet advises taking breaks as with any screen work. "
     "Participants choose their own device, environment and timing.",
     "2", "1", "2", "None required. Accept.", "2", "1", "2"),

    ("Mild frustration or discouragement from not passing the practice round",
     "Participants, psychologically and only mildly. A set level of agreement with a "
     "reference is required before counts are included, so it is possible not to pass "
     "at the first attempt.",
     "Unlimited attempts with no penalty. The threshold is derived from what the "
     "expert reference panel themselves achieved, so participants are never asked to "
     "outperform the people defining the standard. Feedback is worded as calibration, "
     "not assessment. Participation is anonymous, so no individual's performance is "
     "known to the research team or anyone else, and results are never reported per "
     "individual. The Participant Information Sheet states before consent that not "
     "passing is possible and carries no consequence. Participants may stop at any time.",
     "2", "1", "2",
     "None. Residual risk is below that ordinarily encountered in daily life. Accept.",
     "2", "1", "2"),

    ("Re-identification of a participant by inference from recorded metadata",
     "Participants, through loss of anonymity. No identifying data is collected, but "
     "the application records time spent per image, display settings, interface "
     "language and timestamps. In a small pool, an unusual combination — for "
     "example a session conducted overnight in German — could in principle be "
     "attributed by someone who knew who had been invited.",
     "No name, email address or other identifier is collected at any point. The "
     "application issues a randomly generated code held only by the participant, and "
     "no code-to-identity record exists anywhere. Per-participant metadata will not be "
     "reported or published at that granularity, and timestamps will be coarsened "
     "before any dataset is shared. Recruitment is by open invitation rather than a "
     "fixed, knowable list.",
     "2", "2", "4",
     "Confirm at deposit that the published dataset carries no per-participant timing "
     "and no timestamp finer than daily resolution.",
     "1", "2", "2"),

    ("Participant loses their code and cannot withdraw their data",
     "Participants, through loss of control over their data. Withdrawal depends "
     "entirely on the participant quoting their code, because no link between code and "
     "person exists.",
     "The code is displayed prominently at the start; the task cannot begin until the "
     "participant confirms they have recorded it; generating a new code clears that "
     "confirmation so it cannot be bypassed accidentally; and the code is shown again "
     "on the final screen. The consequence of losing it is stated explicitly in both "
     "the Participant Information Sheet and the consent confirmation, before any data "
     "is collected.",
     "3", "1", "3",
     "None. This is an inherent and disclosed consequence of anonymity; the "
     "alternative — holding a name-to-code key — would be a greater "
     "intrusion. Accept.",
     "3", "1", "3"),

    ("Loss of submitted data, wasting participant time",
     "Participants, through their contribution being lost and their time wasted.",
     "Work saves continuously in the participant's own browser as they go, so an "
     "interruption loses nothing. On completion the participant downloads their "
     "results file and returns it to the researcher, and the application confirms on "
     "screen that the download has been produced. Received files are stored "
     "immediately in University OneDrive for Business, which is institutionally "
     "backed up.",
     "2", "2", "4",
     "Acknowledge receipt of each returned file so a participant knows their "
     "contribution arrived.",
     "1", "2", "2"),

    ("Display screen equipment use by the research team",
     "The research team, from extended computer work during software development, "
     "image processing and analysis — eye strain, postural discomfort, "
     "repetitive strain.",
     "Work is office- or home-based on University-provided equipment within normal "
     "working hours. Standard University DSE assessment completed, workstation set up "
     "accordingly, and regular breaks taken in line with the University Health, Safety "
     "and Wellbeing Policy.",
     "2", "2", "4", "None required. Accept.", "2", "2", "4"),

    ("Lone working",
     "Not applicable. All research activity is computer-based and conducted in normal "
     "University or home working environments. There is no fieldwork, no laboratory "
     "work under this application, no travel, and no in-person contact with "
     "participants.",
     "Not applicable. No aspect of this study requires working alone in an isolated or "
     "hazardous setting.",
     "1", "1", "1", "None.", "1", "1", "1"),

    ("Unauthorised or spurious submissions corrupting the dataset",
     "The research team and the integrity of the research, if someone other than an "
     "invited participant submitted data, or if a participant submitted more than once.",
     "Participants receive an individually issued link. Returned files are matched on "
     "the participant's self-generated code, so a resubmission replaces rather than "
     "duplicates an earlier one. No payment or incentive is offered, removing the "
     "motive for fraudulent participation. The task requires interpreting images, so "
     "automated submission is impractical. Quality is monitored through automatically "
     "recorded data — time per image, practice attempts, and agreement on shared "
     "anchor images. All data is held in University OneDrive under the PI's control; "
     "no third-party platform is used.",
     "2", "2", "4",
     "Reconcile the number of files received against the number of invitations issued "
     "at the close of collection.",
     "1", "2", "2"),
]

ACTIONS = [
    ("3", "Confirm the published dataset carries no per-participant timing or "
          "sub-daily timestamps", "D. Oehring", "Before deposit", ""),
    ("5", "Acknowledge receipt of each returned results file", "D. Oehring",
     "Ongoing during collection", ""),
    ("8", "Reconcile files received against invitations issued", "D. Oehring",
     "Close of collection", ""),
]


def main():
    if not SRC.exists():
        sys.exit(f"template not found: {SRC}")
    xml = read_document(SRC)

    for (r, c), text in HEADER.items():
        xml = set_cell(xml, 0, r, c, [para(text)])

    for i, h in enumerate(HAZARDS):
        row = 2 + i                      # rows 2-9 of the hazard table
        for c, value in enumerate(h):
            xml = set_cell(xml, 1, row, c, [para(value)])

    for i, a in enumerate(ACTIONS):
        for c, value in enumerate(a):
            xml = set_cell(xml, 2, 2 + i, c, [para(value)])

    write_docx(SRC, DST, xml)
    print(f"wrote {DST.name}")
    print(f"  {len(HAZARDS)} hazards, {len(ACTIONS)} actions, highest risk score 4 (Low)")
    print(f"  {sum(1 for v in HEADER.values() if v == TBD)} header fields left for you, "
          f"marked ‹to be completed›")


if __name__ == "__main__":
    sys.exit(main())
