#!/usr/bin/env python3
"""Fill the University Participant Information Sheet template for this study.

The template is prose with a University header image and page setup, and its
guidance text is meant to be deleted once replaced. So the body is rebuilt while
the section properties, header, fonts and styles are kept from the original.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fill_docx import read_document, write_docx, replace_body, para, heading, bullet

ETH = Path(__file__).resolve().parent.parent / "ethics"
SRC = ETH / "2026 PIS Template V2.1.docx"
DST = ETH / "Participant Information Sheet - SCLERA-LIVE v1.0.docx"

H = heading
P = para
B = bullet

DOC = [
    H("Information for participants", 32),
    P("**How reliably do people count cells in microscope images?**", size=26),
    P("Study title: Inter- and intra-observer reliability of manual live/dead cell "
      "counting in confocal images of scleral tissue (SCLERA-LIVE)"),
    P("**Version:** V1.0_observers    **Date:** ‹date›    "
      "**Ethics Committee Reference Number:** ‹REACH number›"),
    P("**Researcher team:** Dr Torsten Bossing (Peninsula Medical School), "
      "Dr Emilie Courtecuisse (School of Health Professions), Dr Konstantin Glebov "
      "(Peninsula Medical School), Dr Adam Kyte (School of Engineering, Computing and "
      "Mathematics), Dr Daniela Oehring (School of Health Professions), Dr Niloufar "
      "Zabihi (School of Health Professions), ‹Matt — title, surname, school›, "
      "‹Claudia — title, surname, school› — all University of Plymouth"),
    P("**Principal investigator:** Dr Daniela Oehring"),
    P("Thank you for considering taking part in this study, which will take place "
      "‹approximate dates›. Before you decide, it is important that you understand why "
      "the research is being done and what it would involve for you. Please take time "
      "to read this information and discuss it with others if you wish. If there is "
      "anything that is not clear, or if you would like more information, please ask us."),

    H("What is the research about?"),
    P("Scientists often need to know how many cells in a piece of tissue are alive and "
      "how many are dead. A common way to find out is to stain the tissue with "
      "fluorescent dyes and photograph it with a microscope. Someone then looks at the "
      "images and counts the living and dead cells by eye. That human count is usually "
      "treated as the correct answer, and it is what computer programs written to do "
      "the job automatically are checked against."),
    P("We have reason to think that this “correct answer” is less solid than "
      "it looks. When two experienced colleagues separately counted the same set of "
      "images of scleral tissue (the white outer coat of the eye) from pig eyes, one "
      "concluded that around 12% of the cells were alive and the other around 41%. "
      "They were looking at identical pictures. Because the method they used recorded "
      "only the totals, we cannot even tell whether they were looking at the same cells."),
    P("This study asks a simple question: **how consistently do people actually count "
      "cells in these images?** We want to know how much two people agree, how much "
      "one person agrees with themselves on a second look, and whether the disagreement "
      "is about finding the cells or about deciding whether each one is alive or dead."),
    P("The images are of pig eye tissue obtained as a food-chain by-product from a "
      "local abattoir. No animals were killed for this research, and no human tissue "
      "or patient material of any kind is involved."),
    P("‹If funded: “This research is funded by …”. Delete if unfunded.›"),

    H("Why have I been invited?"),
    P("You have been invited because you are an adult who can view images on a "
      "computer, tablet or phone. **You do not need any expertise in microscopes, "
      "biology or cell counting** — how well people without that background can do "
      "this is part of what we are measuring."),
    P("We are inviting around 20 people to take part in this way. Separately, a small "
      "panel of four to six experienced researchers is producing the reference answers "
      "that everyone else is compared against."),
    P("You have not been invited because of any health condition, and we are not "
      "collecting any information about your health."),

    H("Do I have to take part?"),
    P("It is entirely up to you. You do not have to take part if you do not want to, "
      "and you do not need to give a reason."),
    P("If you decide to take part, you will confirm this on screen at the start of the "
      "task rather than by signing a paper form. This is because the study is "
      "completely anonymous — asking for your signature would mean collecting your "
      "name, which we have deliberately designed the study not to do."),
    P("Choosing not to take part will not disadvantage you in any way. The research "
      "team will not know who took part and who did not."),

    H("What will my involvement be?"),
    P("Everything happens in a web page. Nothing is installed on your device."),
    B("You open a link we send you. The first screen gives you **a code** — something "
      "like amber-larch-63. Please write this down and keep it. It is the only thing "
      "connecting your answers together, and the only way you could later ask us to "
      "remove them."),
    B("You read a short “How to count” page with worked examples. It takes "
      "two or three minutes."),
    B("You do a short **practice round** on a few images, and after each one you are "
      "shown how your answers compare with the reference. This is to help you "
      "calibrate, not to test you."),
    B("You then count your own set of images. Each image is a small square from a "
      "microscope photograph. You click once on each cell you can see and say whether "
      "you think it is alive, dead, or you are not sure. A dot appears where you click "
      "so you do not lose your place."),
    P("**In total this takes about 20 to 40 minutes.** You can stop at any point and "
      "pick up where you left off later by opening the same link on the same device. "
      "You do not have to do it in one sitting."),
    P("Some images are shown to you more than once, deliberately. This is so we can "
      "see how consistent you are with yourself. Please count each one as you find it "
      "rather than trying to remember what you said before."),
    P("There is one thing we will not tell you as you go: how deep inside the tissue "
      "each image was taken. Knowing that an image came from deeper down — and is "
      "therefore expected to be harder — would change how many cells people report, "
      "and it is one of the things we are trying to measure. We will explain this "
      "fully at the end."),
    P("**About the practice round.** You need to reach a set level of agreement with "
      "the reference before your counts go into the study. You can repeat the practice "
      "as many times as you like — there is no limit and no penalty. The level is not "
      "set arbitrarily: it is worked out from what the experienced panel themselves "
      "managed, so you are not being asked to do better than the people setting the "
      "standard. If you do not reach it, nothing happens except that your counts are "
      "not included, and because the study is anonymous, nobody — including us — can "
      "tell who that was."),

    H("How do I withdraw from the study?"),
    P("You can stop at any moment simply by closing the page."),
    P("If you want your data removed after you have submitted it, **email us quoting "
      "your code** and we will delete it. You do not have to give a reason and it will "
      "not affect you in any way."),
    P("Two things you should know about this, because the study is anonymous:"),
    B("**We cannot find your data without the code.** There is no list anywhere "
      "linking codes to people — not held by us, not held by anyone. If you lose the "
      "code we will not be able to identify which answers are yours."),
    B("**There is a cut-off: ‹withdrawal cut-off date›.** Up to that date we can find "
      "and delete your answers. After that, results are combined for publication and "
      "individual contributions can no longer be separated out."),
    P("Both points are why we ask you to write the code down at the start."),

    H("What will my information be used for?"),
    P("Your counts will be combined with everyone else’s to work out how "
      "consistently people count cells in these images. The results will be written up "
      "for a scientific journal and presented at conferences."),

    H("What will happen to the information after the study?"),
    P("The anonymous data — the counts, where you clicked, and how long you spent — "
      "will be kept as part of the research record and deposited in a public data "
      "repository, so that other researchers can check our conclusions and reuse the "
      "reference set. Because the data contains no information that could identify "
      "you, it can be shared openly."),

    H("What are the possible benefits of taking part?"),
    P("There is **no direct personal benefit** to you from taking part. You will not "
      "be paid, and you will not receive your individual results."),
    P("We do not know in advance how the study will turn out — that is why we are "
      "doing it. If it shows that manual counting is less reliable than assumed, that "
      "matters for a great many published studies that rest on it."),

    H("Are there any possible disadvantages or risks of taking part?"),
    P("There are **no physical or psychological risks**. You will be looking at "
      "pictures of stained tissue on a screen and clicking on them. There are no "
      "questions about you, your health, your opinions or your circumstances."),
    P("The only real cost is your time — around 20 to 40 minutes."),
    P("The one thing worth being straightforward about is the practice round: it is "
      "possible not to reach the required standard first time. We have tried to make "
      "this as low-stakes as it genuinely is. There is no limit on attempts, your "
      "performance is never reported to anyone, is not linked to your name because we "
      "do not have your name, and the required level is set by what the expert panel "
      "achieved rather than picked out of the air. Some people may still find it mildly "
      "frustrating, and you are free to stop at any point."),
    P("Looking at a screen for half an hour may cause some eye strain. Please take "
      "breaks as you would with any screen work; the task saves as you go, so stopping "
      "costs you nothing."),

    H("Will I be reimbursed for taking part?"),
    P("No. There is no payment, voucher, prize draw or other incentive. Participation "
      "is voluntary and unpaid. You take part at a time and place of your choosing, so "
      "there are no travel or other expenses."),

    H("Will my taking part and my data be kept confidential? Will it be anonymised?"),
    P("**This study is anonymous, which is stronger than confidential.**"),
    P("We do not ask for your name, your email address, your job, your age, or "
      "anything else that could identify you. The web page gives you a randomly "
      "generated code and that code is the only label attached to your answers. **No "
      "list linking codes to people exists anywhere** — not with the research team, "
      "not with the University, not with anyone. This means your data cannot be traced "
      "back to you even in principle."),
    P("Because of this, the usual arrangements for keeping names separate from data do "
      "not apply: there are no names to keep separate."),
    P("What we do record alongside your counts is: where you clicked, how long you "
      "spent on each image, the brightness and contrast settings you chose, and whether "
      "you used the English or German version. We record these because they affect "
      "counting and we need to account for them."),
    P("One honest caveat. If you are one of a small number of people who took part and "
      "someone knew who had been invited, an unusual pattern — for instance a session "
      "carried out in the middle of the night in German — could in principle be guessed "
      "at. To prevent this we will not publish this detailed information at the level "
      "of individual participants, and we will round timestamps before sharing any data."),
    P("All research data will be stored in the University of Plymouth’s OneDrive "
      "for Business, accessed only from password-protected, encrypted University "
      "computers."),
    P("**Limits to confidentiality:** the task does not ask you to tell us anything "
      "about yourself, so the usual situations in which a researcher might have to pass "
      "on information do not arise here."),
    P("The University of Plymouth sponsors this study, based in the United Kingdom, "
      "and acts as the data controller. This means we are responsible for looking "
      "after your information and using it properly. The University of Plymouth will "
      "keep anonymised research data for a minimum of ten years after the study "
      "concludes, in line with University policy. Because we hold no identifiable "
      "information about you, there is no identifiable information to destroy at the end."),
    P("For more information regarding data confidentiality, you can access the "
      "research participant privacy notice for the University of Plymouth: "
      "https://www.plymouth.ac.uk/research/governance/research-participant-privacy-notice"),
    P("If you have a general question about how the University uses your personal "
      "information, wish to exercise any of your rights, or complain about how you "
      "believe your data is being processed, please contact the University’s Data "
      "Protection Officer: dpo@plymouth.ac.uk"),

    H("What will happen to the results of this study?"),
    P("You will not be identified in any report or publication, because we hold "
      "nothing that could identify you."),
    P("We intend to:"),
    B("publish the findings in a peer-reviewed scientific journal;"),
    B("present them at academic conferences;"),
    B("deposit the anonymous data and the analysis code in a public repository so that "
      "others can check and reuse them;"),
    B("put a plain-language summary at ‹results web address› so that anyone who took "
      "part can read what the study found. Because we cannot contact you, this is how "
      "we will make the results available to you."),

    H("Who do we share your data with?"),
    P("Extracts of your anonymous data may be disclosed in published works posted "
      "online for use by the scientific community. Your data may also be stored "
      "indefinitely on external data repositories and be further processed for "
      "archiving purposes in the public interest or for historical, scientific or "
      "statistical purposes. It may also move with the researcher who collected your "
      "data to another institution in the future."),
    P("Since the data holds nothing that identifies you, this sharing carries no risk "
      "to your privacy."),

    H("What if we find something unexpected?"),
    P("Nothing is measured about you, so there is nothing that could produce an "
      "unexpected finding about your health or anything else. This does not apply to "
      "this study."),

    H("Who has reviewed this study?"),
    P("This study has undergone ethical review following the University of Plymouth "
      "Research Ethics Policy and Procedure. This study has been reviewed and approved "
      "by the Plymouth Internal Ethics Review Committee (PIERC), application number "
      "‹REACH number›."),

    H("Participation in future research"),
    P("We are not collecting contact details, so we cannot and will not contact you "
      "about future research. If you would like to hear about future studies, please "
      "contact Dr Daniela Oehring directly — that request will be kept entirely "
      "separately from this study’s data, and it will not be possible to connect "
      "it to your answers."),

    H("Data Protection Privacy Notice"),
    P("The University of Plymouth Research Privacy Policy can be found at: "
      "https://www.plymouth.ac.uk/research/governance/research-participant-privacy-notice"),
    P("This study does not collect special category personal data."),
    P("To request a copy of the data held about you, please get in touch with "
      "dpo@plymouth.ac.uk. Please note that because this study is anonymous, we hold "
      "no data about you that we could identify and return."),

    H("What if I have a question or complaint?"),
    P("If you have any questions regarding this study, please get in touch with the "
      "researcher, Dr Daniela Oehring, at daniela.oehring@plymouth.ac.uk."),
    P("If you have any concerns or complaints about this study’s ethical conduct, "
      "please contact the Research Ethics Administration, University of Plymouth, "
      "Drake Circus, Plymouth, Devon, PL4 8AA. Email: Research.Ethics@plymouth.ac.uk"),
    P("The University of Plymouth Research Ethics Policy: "
      "https://www.plymouth.ac.uk/research/governance/research-ethics-policy"),
    P("The University of Plymouth Research Data Policy: "
      "https://www.plymouth.ac.uk/research/governance"),
    P("The University of Plymouth Code of Good Research Practice: "
      "https://www.plymouth.ac.uk/research/governance"),
    P("If you are happy to participate in this study, you will be asked to confirm "
      "this on the first screen of the task."),
    P("**Thank you.**"),
]


def main():
    if not SRC.exists():
        sys.exit(f"template not found: {SRC}")
    xml = replace_body(read_document(SRC), DOC)
    write_docx(SRC, DST, xml)
    print(f"wrote {DST.name}")
    print(f"  {len(DOC)} paragraphs; University header, fonts and page setup kept")
    print("  fields left for you are marked with ‹angle brackets›")


if __name__ == "__main__":
    sys.exit(main())
