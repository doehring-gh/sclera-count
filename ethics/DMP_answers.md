# Data Management Plan — answers for DMPonline

DCC Template · Plan ID **209838** · Paste each answer into the matching question.
Fields I could not know are marked **[YOU]**.

---

## Data Collection

### What data will you collect or create?

> **Created for this study (primary data).** For each image region a participant
> counts, the application records: the position of every click within the image
> tile, the label given to it (live, dead or uncertain), the resulting counts, the
> time spent on that region, the brightness and contrast the participant chose,
> the interface language, any free-text note, whether the region was a repeat, and
> the participant's self-generated study code. Each participant also produces a
> record that they gave consent, with a timestamp and the consent version.
> Approximately 20 participants and an expert reference panel of four to six,
> yielding an estimated 15,000–25,000 individual cell annotations. Volume is small:
> well under 50 MB of CSV and JSON in total.
>
> **No personal data is created.** Participants are not asked for a name, email
> address, or any other identifier. The application generates a random code such
> as `amber-larch-63` which the participant records themselves, and no
> code-to-identity key exists anywhere. The data is anonymous rather than
> pseudonymised. The expert panel are named collaborators and are handled
> separately from the participant data.
>
> **Re-used (secondary data).** Existing confocal microscopy z-stacks of porcine
> scleral explants, acquired previously under approved animal-tissue application
> 4696. These are 512 × 512 px PNG images, approximately 300 KB each, and are cut
> into image tiles of roughly 106 µm for annotation. They contain no personal
> data. Approximately 1 GB including derived tiles.
>
> **Software and derived outputs.** The annotation application, the tile-generation
> and analysis code, and the build manifest that records every processing parameter
> used (display cut levels, sampling seed, micron scale, depth of each image).

### How will the data be collected or created?

> Through a purpose-built web application served as static files from GitHub Pages
> and run entirely in the participant's own browser. Participants receive an
> individually issued link, work through the task on their own device at a time of
> their choosing, and at the end download their results as CSV and JSON files,
> which they return to the Principal Investigator. **No third-party data platform
> is used and no data is transmitted to any server** — the application posts
> nothing, and the files exist only on the participant's device until they send
> them.
>
> Returned files are stored immediately in the Principal Investigator's University
> of Plymouth OneDrive for Business and compiled into Microsoft Excel workbooks for
> analysis.
>
> The image tiles are generated from the existing z-stacks by a documented script
> (`build_segments.py`), which writes a manifest recording every parameter used, so
> that the exact stimulus each participant saw can be regenerated from the source
> images.

---

## Documentation and Metadata

### What documentation and metadata will accompany the data?

> - **A machine-readable build manifest** (`manifest.json`) recording, for every
>   image tile: its source file, its position within the parent field, the imaging
>   depth in micrometres, the micron-per-pixel scale, the display cut levels
>   applied, the staining scheme and which fluorophore occupied which channel, and
>   the random seed used to allocate tiles to participants. This is generated
>   automatically rather than written by hand, so it cannot drift from what was
>   actually produced.
> - **A data dictionary** defining every column in the exported CSV files.
> - **The analysis code**, version-controlled in Git with full history.
> - **A findings and decisions record** (`FINDINGS.md`) documenting what was
>   measured, every methodological decision with its reasoning, errors made and
>   corrected, and open questions.
> - **A methodological reference list** (`REFERENCES.md`, `references.bib`) stating
>   what each cited source supports in the design.
> - **The participant-facing documents**: information and consent page, versioned,
>   in both English and German, generated directly from the application source so
>   that the record and the screen cannot differ.
>
> File formats are deliberately open and non-proprietary: CSV, JSON, PNG, plain
> text and Python. Working spreadsheets are held in Excel for convenience but are
> exported to CSV for preservation.

---

## Ethics and Legal Compliance

### How will you manage any ethical issues?

> The study has been submitted for review by the Plymouth Internal Ethics Review
> Committee (PIERC), reference **[YOU — REACH number]**. The tissue imaged is
> porcine, obtained from a local abattoir as a food-chain by-product; no animals
> were killed for this study and ethical review confirmed no licence was required
> (application 4696). No human tissue and no patient data are involved.
>
> **Anonymity by design rather than by promise.** No identifying information is
> collected from participants at any point. Because no code-to-identity key exists,
> the data is anonymous and falls outside the scope of UK GDPR, and the University
> holds nothing that could link a participant to their answers.
>
> **Consent** is obtained through a plain-language information and consent page
> presented before the tool will open. Each statement must be confirmed
> individually; nothing is recorded until the participant agrees. Consent is
> recorded as an event with a timestamp, consent version and study code — never an
> identity. A signature is deliberately not collected, because it would create the
> identifiable record the design exists to avoid.
>
> **Withdrawal** is possible by quoting the study code, up to a stated cut-off
> after which results are aggregated and individual contributions can no longer be
> separated. Both the code's importance and the cut-off are stated before consent
> is given.
>
> **Residual risk of re-identification by inference** is recognised: recorded
> timing, display settings and interface language could in principle single out an
> unusual session within a small participant pool. Per-participant metadata will
> not be published at that granularity and timestamps will be coarsened before any
> dataset is shared.
>
> Recruitment excludes anyone in a supervisory, teaching, assessment or line
> management relationship with the research team, so the principal source of power
> imbalance is removed rather than mitigated after the fact.

### How will you manage copyright and Intellectual Property Rights (IPR) issues?

> All data and code are created by the research team. The University of Plymouth
> holds the intellectual property in accordance with its IP policy, with Dr Daniela
> Oehring as Principal Investigator and data steward. No third-party data,
> proprietary datasets or licensed materials are used, and there are no
> commercial-confidentiality or embargo constraints.
>
> The anonymous annotation data will be released under a Creative Commons Attribution
> licence (CC BY 4.0) and the analysis and application code under a permissive
> open-source licence (MIT), so that both the reference dataset and the method can
> be reused and independently checked. **[YOU — confirm these licence choices are
> compatible with University policy and any funder terms.]**
>
> The expert reference panel contribute annotations as collaborators and are
> offered acknowledgement or co-authorship; this is agreed in writing at invitation
> rather than assumed.

---

## Storage and Backup

### How will the data be stored and backed up during the research?

> All research data is held in the Principal Investigator's University of Plymouth
> **OneDrive for Business**, which is backed up by the institution and versioned,
> giving off-site redundancy without any additional arrangement. No research data
> is kept solely on local disks, removable media, or personal accounts.
>
> Analysis code and documentation are version-controlled in Git with the full
> history retained, giving a second independent copy and a complete audit trail of
> every change.
>
> During the task itself, a participant's work is held only in their own browser's
> local storage so they can pause and resume; it reaches the research team only
> when they choose to download and return their files.
>
> The source confocal images are held in the same OneDrive as part of the wider
> SCLERA-LIVE project and are unchanged by this study.

### How will you manage access and security?

> Access is through University of Plymouth accounts with multi-factor
> authentication, on devices with full-disk encryption, and is limited to the
> Principal Investigator and named co-investigators. Nothing is shared through
> personal accounts or non-institutional platforms.
>
> The strongest control is that **there is nothing sensitive to protect**: the
> participant dataset contains no identifiers, so even complete disclosure could
> not reveal who took part. The only identifiable information in the project is the
> names of the expert reference panel, which is held separately from the annotation
> data, is not needed for analysis, and is deleted once authorship and
> acknowledgement are settled.
>
> Participants each receive an individually issued link, and returned files are
> matched on the participant's own code so that a resubmission replaces rather than
> duplicates an earlier one.

---

## Selection and Preservation

### Which data are of long-term value and should be retained, shared, and/or preserved?

> **Retained and shared indefinitely:**
>
> - the anonymous annotation dataset — every recorded click with its position and
>   label. This is the substantive output: a position-level record of how a group
>   of observers counted the same images, which does not currently exist for this
>   tissue and cannot be reconstructed from summary counts;
> - the **consensus reference annotation** built from the expert panel, which is
>   directly reusable by anyone evaluating an automated cell-counting method on
>   scleral tissue;
> - the image tiles participants annotated, together with the manifest describing
>   how they were produced, so the annotations remain interpretable;
> - the analysis code and the documented decision record.
>
> **Not retained long-term:** intermediate working files, superseded builds, and
> the names of expert panel members once authorship is settled.
>
> Retention is a minimum of ten years after the study concludes, in line with
> University of Plymouth policy. As the participant data is anonymous, there is no
> identifiable information requiring destruction at any point.

### What is the long-term preservation plan for the dataset?

> Deposit in an open repository with a persistent DOI — the University of Plymouth
> institutional repository (PEARL) and/or a general-purpose repository such as
> Zenodo or figshare, at the point of first publication. **[YOU — confirm the
> preferred repository.]**
>
> Preservation formats are open and plain: CSV for tabular data, JSON for
> structured metadata, PNG for images, plain text for documentation. No proprietary
> format is required to read any of it, and no specialist software is needed to
> interpret it beyond the accompanying data dictionary.
>
> The analysis code is archived alongside the data with its Git history, so the
> processing that produced every figure can be re-run rather than merely described.

---

## Data Sharing

### How will you share the data?

> Openly, at the point of first publication, through a repository with a persistent
> DOI cited in the paper. The deposit will include the anonymous annotation
> dataset, the consensus reference, the image tiles, the manifest, the data
> dictionary and the analysis code.
>
> Sharing is unusually straightforward here because the data carries no
> identifiers: it can be released in full without redaction, aggregation or a
> controlled-access process. This also serves the study's purpose — a reference set
> is only useful to other groups if they can actually obtain it.
>
> A plain-language summary of the findings will be published at a stated web
> address, which is how results are made available to participants, since we hold
> no contact details and cannot approach them individually.

### Are any restrictions on data sharing required?

> **No access restrictions are required.** The participant data is anonymous, the
> tissue is porcine and already covered by approved application 4696, and there are
> no commercial, contractual or security constraints.
>
> Two limited handling conditions apply, both to prevent re-identification by
> inference rather than to restrict access:
>
> 1. per-participant metadata — time spent per image, display settings, interface
>    language — will not be published at individual granularity;
> 2. timestamps will be coarsened to no finer than the day before release.
>
> Neither affects the scientific usefulness of the dataset, since the annotations
> themselves are what is reused.
>
> Release is timed to first publication rather than delayed by an embargo.

---

## Responsibilities and Resources

### Who will be responsible for data management?

> **Dr Daniela Oehring (Principal Investigator, School of Health Professions)** is
> responsible for the plan as a whole: data collection, storage, security,
> retention, deposit, and for ensuring all team members handling data have completed
> the University's mandatory GDPR and Information Security training.
>
> Named co-investigators are responsible for following the plan for any data they
> handle. The expert reference panel contribute annotations but do not hold or
> manage the dataset.
>
> Responsibility for the deposited dataset after the project ends rests with the
> Principal Investigator, and with the University of Plymouth as data controller and
> sponsor. Should the Principal Investigator leave the institution, custody
> transfers to a nominated member of academic staff. **[YOU — name a successor if
> your DMP or funder requires one.]**

### What resources will you require to deliver your plan?

> Minimal, and no additional funding is sought for data management.
>
> - **Storage:** well under 2 GB in total, comfortably within existing University
>   OneDrive for Business allocations. No specialist storage is required.
> - **Software:** all tools are either institutionally provided (OneDrive, Microsoft
>   Excel) or free and open-source (Python, Git). The annotation application was
>   built in-house and requires no licence, subscription or hosting cost; it is
>   served as static files at no charge.
> - **Repository deposit:** free at the point of use for both PEARL and Zenodo.
> - **Staff time:** data curation, documentation and deposit are undertaken by the
>   Principal Investigator as part of normal research activity. The documentation
>   and manifests are generated automatically by the analysis pipeline rather than
>   compiled by hand, which is what keeps this cost negligible.
>
> No hardware, licences, training or external services need to be purchased.

---

## What I could not fill

1. **REACH application number** — once PIERC issues it
2. **Repository choice** — PEARL, Zenodo, figshare, or both
3. **Licence confirmation** — CC BY 4.0 for data, MIT for code, subject to
   University and funder policy
4. **Successor custodian** — if your DMP or funder requires one named

Everything else follows from decisions already made, and matches the Participant
Information Sheet, the consent page and the risk assessment. If any of those
change, this needs changing with them — the answers deliberately use the same
wording so a reviewer comparing them finds no discrepancy.
