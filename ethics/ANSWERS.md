# PIERC application — proposed answers

For **Inter- and intra-observer reliability of manual live/dead cell counting in
confocal images of scleral tissue (SCLERA-LIVE)**.

Free text is written to paste straight in. Anything I could not know is marked
**[YOU]** — there are 8 of those, listed at the end.

**Read the three decisions in §0 first: they change several answers below.**

---

## 0. Three things to settle before filling this in

**(a) Who are the ~20 counters?** This is the single biggest determinant of your
review pathway.

- *Colleagues, research staff, and academics outside your line management* →
  S07 "None of the above", vulnerability **Minimal**, likely expedited review.
- *Students, or anyone you supervise, teach or manage* → S07 triggers "students
  as participants" **and** "unequal relationships", vulnerability **Moderate**,
  recruitment materials become a mandatory upload, and the pathway gets heavier.

The answers below assume **colleagues, not students, and nobody you supervise**.
If that is wrong, tell me and I will redo the affected answers.

**(b) Google or Microsoft for collecting the data?** The counting app currently
posts to Google Apps Script → Google Sheets. B22's approved list is Jisc, RedCAP,
Microsoft Forms, OneDrive, SharePoint — Google is "Other", and B37 asks for tools
to be on the TIS-approved register or under a Procurement-vetted DPA. **Google
Workspace is very unlikely to be either at a Microsoft institution.**

Three ways out, in my order of preference:

1. **Move collection to a UoP-hosted endpoint** — the app posts JSON to any URL;
   swapping the target is a one-line rebuild. Cleanest answer to B22/B37/A13.
2. **Keep Google and declare it honestly** at B22 "Other", A13 Yes, with the
   mitigation that participant data is anonymous at source so no personal data
   reaches Google. Defensible, but invites a question.
3. **Export-only mode** — no endpoint at all; counters download their file and
   email it to you. Zero third-party processing, but ~20 people must remember to
   send an attachment.

Answers below are written for **option 2** with the text you would need, and I
have noted what changes under option 1.

**(c) Are Matt and Claudia University of Plymouth?** Glebov and Bossing are
(Peninsula Medical School). If Matt and Claudia are external, A05 gains them.

---

## Screening

| Q | Answer |
|---|---|
| **Project short title** | Already entered — correct as is |
| **S01** | select: **Staff (University of Plymouth employee with a substantive contract)** |
| **S02** | select: **Yes** |
| **S03** | tick: **Primary Data** *and* **Secondary Data** |
| **S04** | tick: **Quantitative Methods** only |
| **S05** | select: **Yes** — already answered, ID **4696**, status **Approved** |
| **S06** | tick: **None of the above** |
| **S07** | tick: **None of the above** *(see §0a — changes if students or supervisees)* |
| **S08** | select: **Yes** |
| **S09** | tick the confirmation |
| **S10** | tick: **Lone working is not relevant to this project** |
| **S11** | select: **No** *(unless Ahmed Elsheikh at Liverpool counts as international to your reading — he is UK, so No)* |

**S03 note** — tick both. Primary: the counts, click coordinates and timings you
collect from observers. Secondary: the existing confocal image stacks, which were
acquired previously under the approved animal-tissue work.

**S06 note** — porcine tissue is not human tissue under the Human Tissue Act, so
this stays "None of the above" despite S05 being Yes.

---

## Project identification

**P01 Full official title:**

> Inter- and intra-observer reliability of manual live/dead cell counting in confocal images of scleral tissue

*(Drop the "(SCLERA-LIVE)" acronym here — P01 says no abbreviations. Keep it in
the short title field.)*

**P02** select: **Yes** — linked to the approved animal-tissue application 4696,
and to the wider SCLERA-LIVE imaging programme from which the images derive.

**P03** **[YOU]** — start date, end date, and data-collection start date.

**P04** Title Dr · Daniela · Oehring · daniela.oehring@plymouth.ac.uk ·
Faculty: **Health** (School of Health Professions).

**P05** **[YOU]** — GDPR training completed and still valid (2-year expiry)?

**P06** select: **Yes** — other UoP investigators.
List: Emilie Courtecuisse, Adam Kyte (School of Engineering, Computing and
Mathematics), Niloufar Zabihi, Konstantin Glebov (Peninsula Medical School),
Torsten Bossing (Peninsula Medical School). Add Matt and Claudia if UoP.

---

## Administration

**A01** select: **The University of Plymouth**

**A02** **[YOU]** — funding source. If none, tick **Unfunded**.

**A04** select: **No**

**A05** select: **Yes**. Text:

> Professor Ahmed Elsheikh (School of Engineering, University of Liverpool) is a
> collaborator and co-author on the wider SCLERA-LIVE programme. Members of the
> expert reference panel may include researchers from outside the University who
> contribute annotations and methodological advice, and who will be acknowledged
> or offered co-authorship. Collaboration is limited to shared expertise and to
> fully anonymised annotation data; no personal data relating to participants is
> shared with any external party.

**A06** select: **No**

**A07** select: **No conflicts of interest to declare**

**A08** **[YOU]** — has everyone handling data done the training?

**A09** select: **Yes**

> Personal data is limited to the expert reference panel, who are named
> collaborators contributing an annotation standard and whose identity is
> relevant to the provenance of that standard. The main participant group (~20
> observers) is **anonymous by design**: the application generates a random code
> (for example `amber-larch-63`) which the participant records themselves. No
> name, email address or other identifier is collected from them, and no
> code-to-identity key exists in any form, held by the research team or anyone
> else. Their data is therefore anonymous rather than pseudonymised.

**A10** tick: **None of the above**

**A11 Data Management Plan Summary:**

> **Data Ownership.** The University of Plymouth, with Dr Daniela Oehring as
> Principal Investigator and data steward.
>
> **Data Storage.** Working data and analysis code are held in the PI's
> University OneDrive for Business, which is backed up by the institution.
> Annotation data submitted through the counting application is written to a
> [Microsoft Forms / a Google Sheet — see §0b] accessible only to the PI, and is
> exported to OneDrive for analysis. The confocal image stacks being annotated
> are existing files from the approved animal-tissue work and contain no personal
> data.
>
> **Data Security.** University accounts with multi-factor authentication and
> full-disk encryption on all devices. The collection endpoint accepts writes
> only from links carrying a per-observer access key, so an unknown party who
> discovered the address could not submit data; the endpoint exposes no read path
> and is deactivated once collection closes. Participant data carries no
> identifier beyond the self-held code.
>
> **Data Access.** The PI and named co-investigators. Expert panel members see
> only their own submissions. No third party receives identifiable data.
>
> **Data Retention.** Participant annotation data is anonymous and will be
> retained indefinitely as part of the research record, in line with University
> policy on research data (minimum 10 years). The only identifiable data — the
> names of expert panel members — is retained for the duration of the project and
> any resulting publications, and is not required beyond that point; it is held
> separately from the annotation data and deleted once authorship and
> acknowledgement are finalised.

**A12** **[YOU]** — upload the DMP Online PDF.

**A13** select: **Yes**

> Annotation data is transmitted from the participant's browser to
> [the collection platform] for storage. Under the current configuration this is
> Google Apps Script writing to a Google Sheet controlled by the PI; the data
> transmitted is anonymous, containing only a self-generated code, counts,
> coordinates within an image tile, and timing. The static web application is
> served from GitHub Pages, which hosts the image tiles and code but receives no
> submitted data. No personal data is shared with either provider.

*Under §0b option 1 this becomes a much shorter answer naming only the University
platform.*

**A16** select: **No**

---

## Study description

**B01 Lay summary** (287 words):

> Researchers often measure whether cells in a piece of tissue are alive or dead
> by staining the tissue with fluorescent dyes and photographing it with a
> microscope. Someone then looks at the images and counts the living and dead
> cells. This count is treated as the correct answer — the standard that computer
> methods are tested against.
>
> We have reason to think that standard is shakier than assumed. When two
> experienced colleagues independently counted the same images of scleral tissue
> from pig eyes, one concluded that about 12% of the cells were alive and the
> other about 41%. They were looking at identical pictures. Because the older
> method recorded only totals, we cannot even tell whether they were looking at
> the same cells.
>
> This study asks how reliably people actually count cells in these images. We
> will ask around twenty people to count cells in small sections of microscope
> images using a purpose-built web page. Each click is recorded along with its
> position, so we can compare not just how many cells two people found, but
> whether they found the same ones. Some images are repeated so we can also see
> how consistent each person is with themselves.
>
> A small panel of experienced researchers will first count a shared set of
> images several times over. Their combined answer becomes the reference the
> others are compared against.
>
> Participants need no expertise and take part anonymously: the web page issues
> them a random code rather than asking for a name. Taking part involves about
> twenty to forty minutes at a computer, tablet or phone, and carries no risk
> beyond the time given up.
>
> The results will tell the field how much confidence a single person's cell
> count deserves, and will provide a properly constructed reference for testing
> automated methods.

**Scientific rationale — Background:**

> Fluorescent live/dead staining with confocal microscopy is the standard route
> to spatially resolved cell viability in tissue explants. Converting an image
> stack into a viability percentage requires several decisions, and the resulting
> figure is conventionally validated against manual counts treated as ground
> truth. That convention rests on an untested assumption: that manual counting is
> itself reproducible.
>
> Existing reporting guidance for reliability studies (Kottner et al., 2011,
> *J Clin Epidemiol* 64:96–106) requires both inter- and intra-rater designs and
> explicit reporting of the interval between repeated measurements, and Koo & Li
> (2016, *J Chiropr Med* 15:155–163) set out how intraclass correlation
> coefficients must be selected and reported. Work in a closely comparable
> setting — manual quantification of corneal immune cells in in-vivo confocal
> images — found that observer variability rose with the number of cells in an
> image and that a consensus training step removed systematic inter-observer bias
> (Britten-Jones et al., 2022, *Exp Eye Res* 216:108950). In computational
> pathology, crowdsourced nucleus detection reached expert-comparable agreement,
> but performance fell markedly as image size increased (Irshad et al., 2015,
> *Pac Symp Biocomput* 294–305), indicating that how the counting task is
> presented materially affects the answer.
>
> Our own preliminary data motivates the question directly. Two experienced
> observers counting the same 64 image regions of porcine sclera produced total
> cell counts that agreed closely in aggregate (296 versus 305) but matched
> exactly in only 19 of 64 regions, and their dead-cell counts diverged
> systematically (262 versus 180), implying viabilities of 11.5% and 41.0% from
> identical images. Because the tally-sheet method recorded only totals and not
> positions, it is not possible to determine whether they identified the same
> cells.

**Research questions / hypotheses:**

> 1. How closely do independent observers agree on the number of cells in
>    confocal images of scleral tissue, and on which cells those are?
> 2. Does the disagreement lie in *detection* (whether a cell is present) or in
>    *classification* (whether a detected cell is live or dead)? Our preliminary
>    data suggests classification dominates, and that detection disagreement is
>    unbiased scatter while classification disagreement is systematic.
> 3. How consistent is a single observer with themselves on repeated presentation
>    of the same image? Intra-observer agreement bounds what inter-observer
>    agreement can achieve, so it is required to interpret the latter.
> 4. Does a short consensus training round with feedback improve inter-observer
>    agreement, replicating Britten-Jones et al. (2022) in a different tissue and
>    at the level of individual cell positions rather than totals?
> 5. Does agreement deteriorate with imaging depth?
>
> We hypothesise that inter-observer agreement on cell *positions* is
> substantially lower than agreement on *totals*, that classification carries the
> systematic component, and that agreement falls with imaging depth.

**Anticipated value:**

> The study provides two things the field currently lacks. First, a quantified
> estimate of how much confidence a single manual count deserves, reported
> according to GRRAS with ICC(2,1) and confidence intervals, Bland–Altman
> analysis including tests for proportional bias, object-level detection F1, and
> Cohen's kappa for classification. Second, a consensus reference annotation with
> cell positions and live/dead labels, constructed from multiple experts each
> counting repeatedly, against which automated methods can be evaluated properly
> rather than against one person's opinion.
>
> Findings will be disseminated through peer-reviewed publication (target: a
> microscopy or ophthalmic imaging journal), conference presentation, and
> deposition of the anonymous annotation dataset and analysis code in a public
> repository so that the reference set can be reused.

**B05** select: **No**
**B06** select: **No**

---

## Recruitment

**B07 Population:**

> Adults aged 18 or over who are able to view images on a computer, tablet or
> phone. No prior expertise in microscopy or cell biology is required — the
> reliability of counting by non-specialists is part of what the study measures.
>
> *Inclusion:* adults 18+, adequate vision (corrected acceptable) to view images
> on screen, sufficient English or German to follow the instructions (the
> application is provided in both).
>
> *Exclusion:* individuals under 18; anyone in a supervisory, assessment or line
> management relationship with the research team, to avoid any perception of
> obligation.
>
> A separate expert reference panel of approximately four to six experienced
> researchers in microscopy, cell biology or ocular tissue contributes the
> reference annotation. They act as collaborators contributing methodological
> expertise rather than as participants, and are named and offered acknowledgement
> or co-authorship.

**B08 Sample size:**

> Approximately 20 observers, plus an expert panel of approximately 4–6.
>
> The target is a precision-based rather than power-based justification, which is
> appropriate for a reliability study. With 20 observers and the planned overlap
> design — every image region counted independently by at least three observers,
> plus a set of anchor regions counted by all — the study yields in excess of 150
> pairwise observer comparisons. Simulation of the analysis pipeline indicates
> this gives a confidence interval on ICC(2,1) of roughly ±0.1, sufficient to
> distinguish the conventional reliability bands defined by Koo & Li (2016).
> Approximately 15% of each observer's set is repeated later in their sequence to
> estimate intra-observer agreement.
>
> The expert panel size is set by the consensus rule: with each expert counting
> the shared set three times, a mark enters the reference only if it survives a
> majority of that expert's own passes and is then found by a majority of
> experts. Four experts is the minimum that makes both majorities meaningful.

**B09 Identification and approach:**

> Participants will be recruited by open invitation circulated by email and
> through research-group and departmental communication channels, and by word of
> mouth among colleagues. Recruitment is conducted by the PI. The invitation
> states that participation is voluntary, unpaid, anonymous, and unrelated to any
> assessment, employment or progression decision.
>
> No one in a supervisory, teaching, assessment or line management relationship
> with the research team will be recruited, which removes the principal source of
> power imbalance rather than mitigating it after the fact. No social media
> advertising or targeted online advertising will be used, and no recruitment
> will take place in closed groups.
>
> The invitation describes the task factually — counting cells in microscope
> images — without suggesting that performance reflects ability or expertise, and
> without implying that taking part is expected of anyone.

**B10** Optional for this risk profile. Recommend uploading the invitation email
and the participant-facing instruction pages anyway; both exist.

**B11 Fair and non-coercive recruitment:**

> Power imbalance is addressed by exclusion rather than mitigation: nobody who is
> supervised, taught, assessed or line managed by a member of the research team
> is eligible. Participation is anonymous, so the research team cannot know who
> took part, who declined, or who withdrew, which makes differential treatment
> impossible in practice as well as in principle.
>
> Participation is genuinely voluntary and carries no reward, so there is no
> inducement to take part against one's judgement. Nobody is disadvantaged,
> penalised or excluded from any opportunity by declining.
>
> The task is accessible: it runs in any web browser on a computer, tablet or
> phone with no software installation, is provided in English and German, uses
> keyboard alternatives to mouse actions, and includes adjustable image
> brightness and contrast. Participants may stop at any point and resume later,
> so it does not require an uninterrupted block of time. Recruitment is open to
> all eligible colleagues without regard to any protected characteristic, in line
> with the Equality Act 2010.

**B12 Compensation:**

> No payment, reimbursement, incentive or prize draw is offered. Participation is
> unpaid and voluntary, involving approximately 20–40 minutes at a time and place
> of the participant's choosing, with no travel and no expenses incurred.
>
> Because there is no payment, the questions of partial reimbursement on
> withdrawal and of fraudulent participation for financial gain do not arise.
> Data quality is protected by design rather than by monitoring identity: each
> invitation carries a single-use access key, and submissions are matched on the
> participant's self-generated code so that a returning participant's data
> replaces rather than duplicates their earlier submission.

---

## Consent, withdrawal, deception, risk

**B13 Target population: observers (~20).**

> Consent is obtained online, immediately before the task begins. The participant
> information is presented as the first screen of the application and the task
> cannot start until the participant has actively confirmed that they have read
> it and agree to take part. There is no time pressure: the information is
> reachable at any point from a persistent help control, the link can be opened
> and closed as often as the participant wishes, and no data is recorded until
> they choose to begin.
>
> Consent is taken by the application rather than in person, so no member of the
> research team is present, and there is no opportunity for a participant to feel
> observed in deciding. Participants are competent adults with no anticipated
> issues of capacity. Language is addressed by providing the full information,
> consent text and interface in both English and German.
>
> Because participation is anonymous, the consent record cannot be linked to an
> individual; the confirmation is recorded as an event rather than a signature.
> This is the standard and appropriate arrangement for anonymous online research.

**B13 Target population: expert reference panel (~4–6).**

> Approached individually by email as named collaborators. Consent is by written
> email reply, following an invitation that sets out what the annotation involves,
> how their data will be used, that their individual agreement with the consensus
> will be reported, and whether they wish to be named or reported anonymously as
> "Expert A, B, C…". They are offered acknowledgement or co-authorship.

**B14 / B15 / B16 / B17** — Participant Information Sheet and Consent Form to be
drafted on the University template. I can draft both from the above; they are not
yet written. B16 debrief: recommend a short on-screen debrief at completion.

**B18 Right to withdraw:**

> Participants may stop at any point simply by closing the page; partial data is
> retained only if they have already submitted it, and they may ask for it to be
> removed.
>
> Withdrawal of data is possible **only via the anonymous code** the application
> issues at the start and which the participant is asked to record. Quoting that
> code to the research team allows their submission to be located and deleted.
> The Participant Information Sheet states this prominently, together with its
> two consequences: that the code cannot be recovered if lost, because no
> code-to-identity record exists anywhere; and that **withdrawal is possible up
> to the point at which results are aggregated for publication**, after which
> individual contributions cannot be isolated and removed. A specific cut-off
> date will be given in the Information Sheet.
>
> Participants will not be penalised, disadvantaged or treated differently in any
> way for withdrawing. Because participation is anonymous, the research team
> cannot know who has withdrawn.

**B19** select: **No**

> No deception is used. Participants are told the true purpose of the study. One
> detail is deliberately withheld: participants are not told the imaging depth of
> each image region, because knowing that an image is from deeper in the tissue —
> and therefore expected to be harder — would bias how many cells they report.
> This is withholding of a specific detail that would bias responses, not
> misrepresentation of the purpose or nature of the research, and the practice is
> stated in the debrief.

**B20** select: **No**

> The task is counting features in microscope images and carries no sensitive
> content. One aspect warrants explicit mention: observers complete a short
> practice round with feedback and must reach a defined level of agreement with
> the reference before their counts are included, so it is possible not to pass
> at the first attempt. This is mitigated by design — there is no limit on
> attempts, feedback is framed as calibration rather than assessment, the
> threshold is derived from what the expert panel themselves achieve rather than
> set arbitrarily, participation is anonymous so no individual's performance is
> known to anyone, and no individual results are reported or fed back to any
> third party. The residual risk is a moment of mild frustration, below that
> ordinarily encountered in daily life.

---

## Data collection and dissemination

**B21** Where:

> Online. Participants take part remotely at a time and place of their choosing,
> using their own computer, tablet or phone. There is no in-person data
> collection and no University premises are used for participant contact.

**B22** tick **Other** *(and OneDrive)*, specify:

> Custom static web application served from GitHub Pages, with annotation data
> submitted to [Google Apps Script writing to a Google Sheet controlled by the PI
> — or the University-hosted alternative, see §0b]. Working data and analysis in
> the PI's University OneDrive. Analysis in Python.

**B23 Dissemination:**

> Peer-reviewed publication and conference presentation. The anonymous annotation
> dataset, the consensus reference, and the analysis code will be deposited in a
> public repository to allow reuse and independent checking.
>
> Individual participants will not receive individual results, since anonymity
> makes it impossible to return them to a known person and reporting individual
> counting performance to individuals is not a purpose of the study. A plain
> summary of the overall findings will be made available at a stated web address
> given in the Participant Information Sheet, so that anyone who took part can
> see what the study found.

**B24** select: **Yes** — anonymous data, open repository, which also serves the
reference-set purpose.

---

## Quantitative sub-module

**B37** select: **Yes**

> Automated image-analysis algorithms are central to the study's purpose: the
> annotations collected here provide the reference against which an automated
> cell-counting pipeline is evaluated. The pipeline uses classical image
> processing — intensity thresholding, morphological filtering and connected
> component labelling — rather than machine learning, and runs locally on
> University equipment on image data containing no personal information. A simple
> peak-detection routine may be used to propose candidate cell positions for an
> expert to correct when constructing the reference; those proposals are always
> reviewed and edited by a human, and are never used as the reference themselves,
> because training or evaluating observers against an algorithm's output would
> make the comparison circular. No personal data is processed by any AI or
> cloud-based service.

**B38 Design:**

> An observational inter- and intra-observer reliability study, non-interventional.
>
> Existing confocal image stacks of porcine scleral explants, acquired under
> approved animal-tissue application 4696, are divided into small square regions
> of approximately 106 µm. Participants view one region at a time in a web
> application and click once on each cell nucleus, recording for each whether it
> is live, dead, or uncertain. Each click stores its position, which allows two
> observers to be compared cell by cell rather than only by totals.
>
> The design has three stages. First, an expert panel each count a shared set of
> regions three times, and their answers are combined into a consensus reference.
> Second, participants complete a short practice round against that reference with
> feedback, and must reach a defined agreement threshold before proceeding.
> Third, participants count their assigned set, which overlaps with others' sets
> so that pairwise agreement is estimable, and includes a proportion of regions
> repeated later in their own sequence to estimate intra-observer agreement.
>
> Assignment guarantees that no observer sees the same tissue location at two
> different imaging depths, since the second encounter would measure recall
> rather than counting.
>
> Procedures participants undergo: viewing images on screen and clicking on them.
> Risks: none physical or psychological beyond the time burden of approximately
> 20–40 minutes. No sensitive or health-related measurements are taken from
> participants, so the question of incidental findings does not arise.

**B39** Not a survey instrument. Upload the participant-facing instruction pages
and a screenshot of the counting interface.

**B40** Not applicable — no random assignment to intervention and control.
Observers are allocated to overlapping sets of images for coverage, and everyone
performs the same task.

**B41 Minimising bias:**

> Several sources of bias are controlled by design.
>
> *Display.* All images are rendered with a single intensity scaling computed
> across the whole image set rather than per image, so that identical cells appear
> identical wherever they occur and a dim image is not artificially brightened.
> Participants may adjust brightness and contrast, and the settings they choose
> are recorded with their counts so that display becomes a measured variable
> rather than an uncontrolled one.
>
> *Blinding.* Participants are blind to imaging depth and to which regions are
> repeats of ones they have already counted. Regions are presented in a shuffled
> order, and the shared anchor regions are distributed through each observer's
> sequence rather than placed at the start, so that they are not systematically
> counted while least practised.
>
> *Boundary effects.* A cell is attributed to the region containing its centre,
> and the application enforces this by refusing marks outside the region while
> still displaying surrounding context, removing double counting and
> under-counting at region edges.
>
> *Reference construction.* The consensus reference is built from multiple
> experts each counting repeatedly, with marks required to survive a majority of
> an expert's own passes and then a majority of experts, so that no single
> generous or conservative counter determines it. Where experts locate the same
> cell but disagree on live versus dead, the cell is marked uncertain and
> excluded from classification scoring rather than resolved arbitrarily.
>
> *Sampling.* Image regions are sampled stratified by cell density so that dense,
> sparse and empty regions are all represented; empty regions are deliberately
> retained, since they are the only places where false positives can be observed.
>
> Response bias from non-completion is addressed by allowing participants to stop
> and resume, and by reporting how many regions each observer completed.

**B42** select: **No**

> The confocal microscope was used to acquire the tissue images under the
> separately approved animal-tissue work. No device of any kind is applied to
> participants, who use their own general-purpose computer or mobile device.

**B43** select: **No**

**B44 Analysis plan:**

> Agreement is reported following GRRAS (Kottner et al., 2011).
>
> *Counts.* Intraclass correlation coefficient ICC(2,1) — two-way random effects,
> absolute agreement, single measure — with 95% confidence intervals, reported
> with model, type and definition stated explicitly as required by Koo & Li
> (2016). Bland–Altman analysis of per-region differences with limits of
> agreement, accompanied by regression of the difference on the mean to test for
> proportional bias, since a mean difference near zero can conceal bias that grows
> with the number of cells present.
>
> *Positions.* Because every click carries a coordinate, marks from two observers
> are matched to each other by optimal assignment within a fixed radius derived
> from cell size. This yields, for each pair of observers, the number of cells
> both found, the number found by only one, and a detection F1 score. This
> separates disagreement about whether a cell exists from disagreement about what
> it is — a distinction impossible with totals alone.
>
> *Classification.* Cohen's kappa on live/dead labels, computed only over cells
> that both observers located, and excluding cells the expert panel could not
> agree on.
>
> *Intra-observer.* The same statistics computed between an observer's first and
> repeated presentation of the same region. This provides the upper bound on
> achievable inter-observer agreement.
>
> *Depth.* Agreement statistics stratified by imaging depth, with the important
> caveat that detection sensitivity itself falls with depth; a sensitivity floor
> will be applied so that apparent changes in viability with depth are not
> confused with the assay losing the ability to detect cells at all.
>
> *Training effect.* Comparison of agreement before and after the practice round.
>
> Analysis in Python. All code and anonymous data deposited publicly.

**B45 Data integrity:**

> Each invitation carries a single-use access key, so submissions can only be made
> through a link issued by the research team; the collection endpoint rejects
> anything else. Submissions are matched on the participant's self-generated code,
> so a participant who resumes or resubmits replaces their earlier rows rather
> than creating duplicates.
>
> The task is not a survey and offers no incentive, so there is no motive for
> multiple or fraudulent submission. Automated submission is impractical because
> the task requires interpreting images. Quality is additionally monitored through
> data the application records automatically: time spent per region, number of
> practice attempts, and agreement with the reference on shared anchor regions,
> any of which would identify an implausibly rapid or inattentive submission.
> Participants must be 18 or over; this is stated in the information and confirmed
> at consent, and the study is not advertised to or accessible via any channel
> aimed at children.

**B46** select: **No**

---

## Risk

**C01** **[YOU]** — upload the completed UoP risk assessment template.
**C02** **[YOU]** — sign-off by someone with risk assessment training.

**C03** — tick **C. Breach of Confidentiality Risks** only, with the note:

> The residual confidentiality consideration is not disclosure of participant
> identity, which is not collected, but the possibility of re-identification by
> inference. The application records time spent per region, display settings,
> interface language and timestamps. Within a small pool of colleagues, an unusual
> combination — for example a session conducted overnight in German — could in
> principle be attributed. This is addressed by not reporting or publishing
> per-observer metadata at that granularity and by coarsening timestamps before
> the dataset is shared.

Leave A, B, D–M unticked. Justify in the risk assessment as follows: no physical
or psychological procedures; no covert observation or private information; no
sensitive topics; no questions about relationships; no deception or withholding of
benefit; no legal exposure; no commercial sensitivity; no reputational risk beyond
normal publication; no vulnerable groups; resources adequate; no social media,
generative AI, biometric or security-sensitive elements.

**C04** All four: **No**

**C05** select: **Low (1–4)**

**C06** select: **Minimal** *(see §0a — becomes Moderate if students or supervisees)*

**C08 Additional context — argue for expedited review:**

> This project is submitted as suitable for expedited review.
>
> Participants are competent adults, recruited outside any supervisory or
> assessment relationship, who view microscope images on their own device and
> click on the cells they see. The activity is closer to a de-identified survey
> than to an experimental procedure, and the burden is approximately 20–40
> minutes of their time.
>
> No personal data is collected from participants at all. The application issues
> a random code that the participant records themselves, and no code-to-identity
> key exists in any form. Their data is anonymous rather than pseudonymised, and
> therefore falls outside the scope of UK GDPR. The only identifiable individuals
> are members of the expert reference panel, who are named collaborators
> contributing methodological expertise and are offered acknowledgement or
> co-authorship.
>
> The tissue that appears in the images is porcine, obtained from a local abattoir
> as a food-chain by-product, and is covered by approved application 4696. No
> animals were killed for this study and no human tissue is involved.
>
> Two features that might otherwise attract attention are addressed by design.
> Participants may not pass the practice round at the first attempt; attempts are
> unlimited, performance is anonymous and never reported individually, and the
> threshold is derived from what the expert panel themselves achieve rather than
> set arbitrarily. And participants are not told the imaging depth of each region,
> which is withholding of a detail that would bias their responses rather than
> deception about the purpose of the research, and is explained at debrief.

---

## Equity check

**C09:**

> Core research team, plus an expert reference panel of approximately four to six
> researchers in microscopy, cell biology or ocular tissue, some of whom are
> external to the University.

**C10:**

> **Group: Expert reference panel.**
> *Burdens:* approximately 20–30 minutes of skilled time to annotate a shared set
> of images three times, plus optional methodological advice. Their individual
> agreement with the group consensus is measured and reported, which is a modest
> professional exposure; they choose whether to be named or reported anonymously.
> *Benefits:* co-authorship or acknowledgement on resulting publications; early
> sight of the methods; a reference dataset they may reuse.
>
> **Group: Participants (~20 observers).**
> *Burdens:* approximately 20–40 minutes of their time, at a place and moment of
> their choosing. No travel, no cost, no risk.
> *Benefits:* no direct personal benefit. Contribution to a methodological result
> relevant to their field, and access to a plain summary of the findings.
>
> **Group: Core research team (PI and co-investigators).**
> *Burdens:* study design, software development, analysis and writing.
> *Benefits:* publications, and a reference dataset enabling subsequent work.

**C11:**

> Burdens in this study are small and evenly distributed: no group bears
> significant risk, cost or time commitment relative to the others. The expert
> panel gives the most skilled time and receives the most direct benefit through
> co-authorship or acknowledgement, which has been discussed with them openly in
> the invitation rather than assumed. Participants give the least time and receive
> no individual benefit, which is proportionate to a burden amounting to a short
> task with no risk; they are told this plainly rather than offered an inflated
> account of personal benefit.
>
> No group is recruited on the basis of, or excluded by, any protected
> characteristic. The task is designed for accessibility — browser-based with no
> installation, usable on a phone or tablet as well as a computer, available in
> English and German, with keyboard alternatives and adjustable image display —
> so that participation is practically as well as formally open, in line with the
> Equality Act 2010. Nobody is recruited from a position of dependency on the
> research team.

---

## Final

**D01** **[YOU]** — upload Researcher Safety Risk Assessment. Content is
straightforward: online study, no fieldwork, no lone working, no participant
contact; risks limited to standard display screen equipment use.

**D02** Optional.

**D03** select: **No** *(unless you consider a professional body's code binding
on you personally — if you are HCPC-registered you may prefer Yes)*

**D04** select: **No**

**Declaration** — tick.

---

## The 8 things I could not answer

1. **P03** — project start, end, and data-collection start dates
2. **P05** — your GDPR training completed and still in date?
3. **A02** — funding source (or Unfunded)
4. **A08** — have all data-handling team members done GDPR training?
5. **A12** — DMP Online PDF
6. **C01 / C02** — risk assessment and its authorised sign-off
7. **D01** — Researcher Safety Risk Assessment
8. **P06 / A05** — are Matt and Claudia UoP or external?

And the three decisions in §0: participant population, collection platform, and
whether the expert panel is named.

**Not yet written, and mandatory:** the Participant Information Sheet (B14) and
Consent Form (B15). I can draft both against the University template — say the
word.
