# SCLERA manual-count study — findings, methods and decisions

Working record for the multi-rater counting study and the app that runs it.
Everything measured, decided, or got wrong, with enough detail to reproduce or
overturn it. Literature in [REFERENCES.md](REFERENCES.md); build and workflow in
[README.md](README.md).

Last updated 2026-08-24.

---

## 1. The specimens

Full-thickness scleral buttons punched from the **posterior pole of fresh porcine
eyes** with a stamp cutter (fixed width and length), approximately **4 hours
post-mortem**. **Not sectioned in depth** — intact from the surface down, so dyes
reach cells only by diffusing in from the top surface.

Imaged as confocal z-stacks, z00–z19 at **5.263 µm** per slice (~100 µm total).
Field of view **850.10 µm** across 512 px = **1.6604 µm/px**. The A–H × 1–8
counting grid divides a field into 64 squares of **106.3 µm**.

Scale and z-interval are from `calibration.yaml`; the 106 µm figure independently
matches the "each square ≈ 106 µm" printed on the original
`COUNT_field_*_grid.png` figures, which is a useful cross-check that the geometry
is right.

---

## 2. Staining — what is actually in the files

`czi_export.py` fixes the channel convention, and pixel data confirms it:

| channel | dye | meaning |
|---|---|---|
| R | ethidium homodimer-1 | dead |
| G | calcein | live (Calcein/EthD scheme) |
| B | Hoechst 33342 | every nucleus (Hoechst/EthD scheme) |

**Measured by channel occupancy across hydrated files:**

| specimen | scheme |
|---|---|
| 001, 002 | Calcein/EthD (R+G, B empty) |
| 003, 006 | Hoechst/EthD (R+B, G empty) |

Both manual-count specimens are Hoechst/EthD. `build_segments.py` refuses to
build if a field's channel occupancy contradicts the requested `--scheme`, so a
mismatch cannot pass silently.

### Why Hoechst and not calcein

Only a stain that labels **every** cell can support a "count the total" task.
Calcein fills live cytoplasm and has no one-to-one relationship with nuclei, so
there is no denominator and "count all the cells" is not well posed. Observed
directly: in 001, the calcein channel had mean 147 with 99.9% of pixels above 10
— a dense diffuse wash, not countable objects.

### Why not DAPI (considered 2026-08-24, rejected)

DAPI is **membrane-impermeant**; that is precisely why Hoechst 33342 is the
live-cell stain (Chazotte 2008; Hirai 2023 had to use boron-cluster carriers to
force DAPI into live cells). In living tissue DAPI would preferentially label
permeabilised cells — behaving as a second dead marker and destroying the
all-nuclei denominator. **Rejected: it would be a step backwards.**

### Why not DRAQ5 (the obvious far-red route to depth, rejected)

- Richard 2010: 30 min exposure killed U2OS cells 24 h later; **Hoechst under the
  same conditions did not**.
- Zhao 2009: DRAQ5 induced pronounced DNA damage response (H2AX, ATM, Chk2, p53).
- Mari 2010: inhibits chromatin-associated processes, "great caution" advised.

A dye that kills cells disqualifies itself from a viability assay.

Zhao 2009 also tested **SYTO 17** (far-red) and found *no* significant effect on
any measured parameter — the one far-red candidate worth testing if depth becomes
the binding constraint. It stains live and dead alike, so it would need validating
as a denominator.

**Current position: keep Hoechst 33342 + EthD-1.** Open for the expert panel to
overturn.

---

## 3. Depth — the dominant practical constraint

`tools/depth_profile.py`. Hoechst p99 (of 255) on the counting channel:

| stack | z05 (26 µm) | z09 (47 µm) | z13 (68 µm) | z17 (90 µm) |
|---|---|---|---|---|
| 006/2 Image 11 | 153 | *not downloaded* | 25 | 10 |
| 006/1 Image 5 | 72 | 57 | 31 | 12 |
| 003/1 Image 5 | 81 | 31 | 10 | 6 |
| 003/2 Image 21 | 60 | 25 | 8 | 3 |
| 003/1 Image 8 | 37 | 13 | 7 | 5 |

**Deepest slice still worth counting: 26 µm for three stacks, 47 µm for one,
none for `003/1 Image 8`.** In a sclera several hundred microns thick, we sample
a thin superficial layer.

**Consequence: `--z-levels 5,9,13,17` — recommended earlier in this project — is
wrong for this data.** z13 and z17 are black in most stacks; counting them would
hand raters noise and any "depth effect" would partly be that.

### The dimness threshold was calibrated by eye, not derived

A first cut of p99 < 20 passed `006/1 Image 5` at z13 (p99 = 31), which was
**visibly black** when the tiles were rendered. Threshold raised to **40**. This
is an eyeballed number and should be replaced by something principled (e.g.
nucleus-to-background contrast) if it starts carrying weight.

### Optics or dye penetration?

The EthD/Hoechst p99 ratio stays roughly constant with depth within each stack
(006/2: 0.40, 0.60, 0.40; 003/2: 1.80, 1.44, 1.50), so both channels decay
together. That is consistent with optical attenuation, but does **not** exclude a
shared diffusion front — both dyes enter from the same surface.

Because the tissue is **not sectioned**, diffusion is a live hypothesis. Precedent
in comparable dense tissue:

- Muerner 2026 (bovine IVD): Calcein AM/EthD-1 required **Collagenase P
  pre-treatment** for adequate penetration.
- Stoddart 2006 (cancellous bone): reagent penetration into whole cores "easily
  led to artefacts", solved by **250 µm unfixed sections**. Also found tissue
  autofluorescence made fluorescent live/dead assessment of osteocytes impossible.

**Testable prediction:** if diffusion is the limit, longer incubation should push
signal deeper. Not yet tested.

---

## 4. The depth-dependent viability artifact (important)

Apparent dead fraction rises with depth as detected counts collapse:

| 003/2 Image 21 | 26 µm | 47 µm | 68 µm |
|---|---|---|---|
| detected nuclei | 391 | 144 | 17 |
| apparent dead fraction | 72% | 90% | 100% |

**A dead nucleus carries signal in two channels and is brighter than a live one.**
As sensitivity falls with depth, dead nuclei stay detectable after live ones have
dropped out. The tissue is not dying with depth — the assay is running out of
sensitivity, and the survivors are biased.

Not universal (`006/1 Image 5` runs 37.6% → 38.2% → 25.2% → 0.0%, but n collapses
to 6 and those numbers are meaningless), which is itself the point: the direction
depends on relative channel brightness.

**This threatens the stated aim — viability per z-stack — more than the dye choice
does.** Any per-slice viability curve needs a sensitivity floor: report only where
total-nuclei detection is demonstrably complete. Not yet implemented.

---

## 4b. Z double-counting — a second, compounding error (2026-08-24)

Raised by Torsten Bossing. Measured with `tools/z_trace.py` on nine consecutive
slices of `006/1/Image 5`, with nuclei linked across slices by nearest-neighbour
within 5 µm (the minimum cell diameter in `config.yaml`), one match per slice,
tolerating a one-slice dropout.

**A nucleus is a 3D object photographed in 5.263 µm slices, so it appears in
several of them.** Median axial extent **3 slices (15.8 µm)**, maximum **9 slices
(47.4 µm)**. Summing per-slice counts therefore over-counts by **3.1×** — 2,375
detections correspond to 767 distinct nuclei.

That alone would only inflate density. The reason it corrupts *viability* is that
the error is **asymmetric**:

| | mean axial extent |
|---|---|
| dead-positive nuclei | 3.88 slices (20.4 µm) |
| EthD-negative nuclei | 2.58 slices (13.6 µm) |
| | **1.51×** |

Dead nuclei carry signal in two channels, so they clear threshold over more
slices and are counted more often. **The dead fraction inflates from 39.6% to
49.7% — a 10.1 point error**, in the same direction as the depth-sensitivity
artifact of §4 and compounding it.

Note the linked figure, 39.6% dead → **60.4% viable**, sits in a different place
from the naive one. The v4 audited pipeline reported ~48% viability for 003/004
(different specimens), so this is the same order once linking is applied.

### This breaks the current depth design

Two slices sample *different* nuclei only if they are further apart than the
axial extent:

| separation | nuclei appearing in both |
|---|---|
| 10.5 µm | 53.5% |
| **21.1 µm** (our z05→z09) | **23.2%** |
| 31.6 µm | 6.4% |
| 47.4 µm | ~0% |

**The build currently uses z05 and z09 — 21 µm apart — so roughly a quarter of
nuclei are physically the same objects at both depths.** The "no counter sees one
location at two depths" rule stops someone recognising the *square*; it does not
stop them meeting the same *nucleus*.

**And the conflict cannot be resolved inside this tissue as imaged:** clean
separation needs ~47 µm, but the usable depth range is only 26–47 µm (§3). There
is no pair of independently-sampled countable depths in these stacks.

That makes the acquisition question — Torsten's Z-correction — load-bearing
rather than an optimisation. Options: extend the usable range at acquisition;
section the tissue and image across the cut face; or accept overlap and model it
explicitly, reporting depth as a within-nucleus rather than between-nucleus
comparison.

### Why detect-then-link rather than threshold in 3D

A single 3D threshold cannot work here: signal decays steeply with depth (§3), so
one level is simultaneously too high at the top of the stack and too low at the
bottom. Detecting per slice against each slice's own noise floor and then linking
sidesteps that.

---

## 5. What Maryam and Louise's data actually shows

`analysis/legacy_agreement.py`, on the two .xlsx tally sheets (64 squares, one
field, specimen 006 / Image 11_z09 as rendered in `COUNT_field_1_grid.png`).

| | Maryam | Louise | |
|---|---|---|---|
| total nuclei | 296 | 305 | r = 0.818, mean diff −0.14, **bias 3%** |
| dead nuclei | 262 | 180 | r = 0.806, mean diff +1.28, **bias 37%** |
| implied viability | **11.5% live** | **41.0% live** | **29.5 points apart** |

**The disagreement is classification, not detection.** Scatter is nearly identical
on both measures (mean |diff| 1.42 vs 1.44); what differs is *bias*. Detection
error is scatter around zero and cancels out; dead-calling is one-directional and
does not, which is what produces the viability gap.

Two things this does **not** show, and both matter:

1. **Whether they found the same cells is unknowable.** The tally sheets recorded
   only numbers. Two counters could disagree completely and still write the same
   total. Identical totals on only **19 of 64 squares**; the 296 vs 305 agreement
   is differences cancelling.
2. **Louise left 13 of 64 "dead" cells blank.** Blank had to be read as zero to
   compute anything, which flatters her live fraction. Some of the 29.5 points may
   be that rather than judgement.

Both are structurally fixed by the new app: every click carries coordinates, every
nucleus gets an explicit label, and an empty square is its own recorded answer.

---

## 6. Design decisions and why

| decision | reason |
|---|---|
| One ~106 µm square at a time | Irshad 2014: crowd F-measure best at 400×400 px, degrading significantly at 600 and 800. Britten-Jones 2022: variability rises with cells per image. |
| Click every nucleus, store x,y | The only way to tell detection disagreement from classification disagreement. Impossible with tally sheets. |
| **Global** display stretch across the build | A per-field stretch brightens dim deep slices back up, erasing the depth effect being measured and pulling noise into plausible nuclei. |
| Context margin + centre rule, enforced | A cell belongs to the square its centre falls in; the app refuses clicks outside and says why. |
| No counter sees one location at two depths | Otherwise the second is recall, not counting. |
| Blocks shuffled | Otherwise everyone meets the anchors first, while least practised — an order effect on exactly the squares used to put all counters on one scale. |
| Depth never shown to the counter | Would measure their expectation of a hard square rather than the square. Joined back from the manifest at analysis. |
| Repeats for intra-rater reliability | Intra-rater agreement is the **ceiling** for inter-rater: nobody agrees with someone else better than with themselves. Without it, a poor inter-rater result cannot distinguish careless counters from an ambiguous task. |
| Two-stage consensus (within expert, then across) | Pooling all passes lets a generous counter dominate with a vote per pass for marks only they made. |
| Labels settled separately; ties → `unsure`, excluded from scoring | Failing a participant on a call the experts could not make is indefensible. |
| **Gate derived, never chosen** | Each expert is scored against the consensus they helped build — the most favourable test, therefore the ceiling. On simulated experts this gave location 0.90 but count **0.85**. |
| `--prefill-from` refused with `--reference-passes > 1` | Identical drafts make independent passes agree trivially, inflating the number that justifies the gate. |
| Training squares held out of every counting set | Otherwise a counter later counts a square whose answer they were shown. |
| Detector proposals are a draft, never the reference | The study compares manual counts against the automated pipeline. Training people to match a detector then measuring their agreement with a detector answers nothing. |

---

## 7. Errors made and corrected

Recorded because the corrections are part of the method.

| error | how it surfaced | fix |
|---|---|---|
| **Synthetic reference shipped live**, labelled "Daniela (reference)" — random coordinates generated to test the pipeline | Daniela counted the first square and found the reference "somewhat off" | Removed; replaced with the real reference-authoring workflow |
| Channel mapping assumed live = B | Pixel stats: B empty in 001/002, G dense | Read `czi_export.py`; scheme detection added |
| `--z-levels 5,9,13,17` recommended | Depth profiling showed z13/z17 black in most stacks | Corrected; profiler written |
| Dim threshold p99 < 20 | A field at p99 = 31 was visibly black when rendered | Raised to 40, flagged as eyeballed |
| Grid-line removal replaced green with green | Lines still visible in tiles | 5×5 median on a 3 px line is majority-line; window now 3× line width |
| Training squares appeared in 3 of 6 counting blocks | Explicit check after building the feature | Held out of assignment |
| Training attempts inflated by re-reaching the gate | Test run showed attempt 5 after two real attempts | Counted on retries only |
| Cited Jonkman poster DOI as the tutorial | Verified against PubMed before writing | Correct DOI recorded |
| Guessed a PMID for Stoddart 2006 | Returned an unrelated hypothyroidism paper | Searched properly |
| "1.0× more disagreement" line compared spread when the signal was bias | Output read as nonsense | Rewritten to compare relative bias |
| Reference/trial builds hard-coded `"endpoint": ""` so they could never auto-save | Testing the submit path against a mock endpoint | Uses `args.endpoint`; verified end to end |

---

## 7b. Where this study sits (revised 2026-08-24)

The parent project is **SCLERA-LIVE**. The existing methods manuscript is being
restructured and **should not be treated as the frame for this study**: the plan
is now two papers — one showing that current methods fail, and a second
developing a process for scleral confocal viability.

That changes what the counting study is for.

**Under the old framing** it supplied hand-annotated ground truth to pin down two
parameters of a pipeline already presented as working.

**Under the new framing it is primary evidence for the first paper.** If capable
observers cannot reproduce each other — or themselves — on these images, then the
field's implicit gold standard is not a standard, and every automated method
validated against a single human's counts inherits that. That is a stronger and
more interesting claim than parameter-fitting.

It also means **the study cannot fail**. Low expert agreement is not a spoiled
reference; it is the result. This matters for how the pass mark is read: a gate
that comes out at 0.75 rather than 0.90 is a finding about the task, not a
disappointment.

### The design tension this creates

The participant round can serve two different purposes, and they pull opposite ways:

| purpose | what it needs |
|---|---|
| **(a)** quantify how unreliable manual counting naturally is | observers counting **untrained and ungated** — the natural spread is the measurement |
| **(b)** produce a consensus good enough to evaluate automated methods | observers **trained and gated**, so the reference is as tight as possible |

**A 90% training gate serves (b) and destroys (a).** Selecting for agreement
manufactures it: after gating you can no longer say anything about natural
observer variability, because you removed the observers who displayed it.

**Proposed resolution — collect both, in order:**

1. an **ungated first pass** on a small common set, before any training or
   feedback: this is the "current methods fail" evidence
2. then the **training round and gate** as already built
3. then the **gated counting round**: this is the reference for paper two

The before/after difference is itself a result, and it directly tests
Britten-Jones et al. (2022) — who found consensus training removed systematic
inter-observer bias in manual corneal cell counting — in a new tissue and with
position-level rather than count-level agreement.

Not yet implemented. It needs an ungated block presented before the training
round, with its results kept separate.

### Evidence already in hand for the "current methods fail" paper

- **Maryam vs Louise: 11.5% versus 41.0% viability from identical images** (§5).
  Two capable people, one field, a 30-point gap in the headline number.
- Their agreement on totals is **unverifiable** — tally sheets record no positions,
  so identical totals do not mean the same cells (§5).
- **Apparent viability falls with depth as a detection artifact**, because dead
  nuclei carry two channels and outlive live ones as sensitivity drops (§4).
- **The usable depth range is 26–47 µm, not the ~100 µm the stacks span** (§3), so
  a viability computed over a whole stack is weighted by where the signal is, not
  by the tissue.

### Ethics scope is unaffected by the restructure

The tissue side is settled independently of any manuscript: porcine eyes were an
abattoir food-chain by-product, no animals were killed for the study, and ethical
review confirmed no licence was required. The new application concerns only the
human observers — what they are asked to do, what is recorded, and how they
withdraw. The proposed title describes the observers' task, so it does not depend
on how the papers are eventually split.

---

## 7c. Why an automated tool (ImageJ or ours) does not settle this

Raised by Torsten Bossing, 2026-08-24: *"Why do you want to re-invent what ImageJ
can do since 2 decades?"* The answer is not that ImageJ is inadequate.

**ImageJ is a toolbox, not a method, and it cannot validate itself.** Whatever it
produces is a number with no error bar. The only way to know whether it is right
is to compare it against human counts — so "use ImageJ" presupposes the thing
this study measures.

**Concede immediately if raised:** ImageJ's Cell Counter plugin already does
click-counting with coordinates. It could do the counting; it could not run the
study — 20 people without installation on phones and tablets in two languages, an
*identical* display transform for everyone (in ImageJ each person sets their own
brightness, so you would measure their contrast choices), the enforced edge rule,
hidden repeats, blinding to depth, and the training gate.

**Failure modes that any threshold-based workflow inherits**, all measured rather
than asserted:

- Independent thresholding of the two channels yields more dead objects than
  nuclei in **60.6% of optical sections** (v4 audit); the standard
  threshold-both-then-subtract workflow does exactly this.
- Per-image normalisation manufactures nuclei on blank fields (~54 phantom
  objects, v4). Reproduced independently here: the draft detector found 12 nuclei
  in square F2 where two observers both counted 5.
- Adaptive and Li thresholding over-count background by up to **~2,800% at low
  density** (v4) — sclera is sparsely cellular, and methods validated on
  confluent culture do not transfer.
- Autofluorescence can defeat the assay outright: Stoddart 2006 found bone
  autofluorescence made fluorescent live/dead assessment of osteocytes impossible.

**The argument to lead with**, because it is ours and nobody has it: the
depth-dependent detection bias in §4. No software warns about it, ImageJ included.

**Do not argue** that ImageJ is inaccurate or outdated. The winning argument is
that the field validates automated counts against manual counts, nobody has
checked whether manual counts are reproducible on this tissue, and two capable
observers differ by 30 points of viability on identical images.

---

## 8. Open questions

1. **Staining** — keep Hoechst/EthD-1? Any far-red all-nuclei option that survives
   depth without killing cells? *With the expert panel.*
2. **Section or not** — sectioning buys depth but creates a cut-face dead layer to
   exclude. *With the expert panel.*
3. **Sensitivity floor** — how to bound per-slice viability so §4's artifact
   cannot be reported as biology. *Unsolved.*
4. **4-hour post-mortem interval** — Svare 2021 found porcine *retina* at 240 min
   significantly more damaged than at 90 min. Sclera is far less metabolically
   demanding, so this should not be read across directly, but the window matches.
   Does it matter for scleral fibroblasts? *With the expert panel.*
5. **Ethics** — participant performance data on identifiable people is the
   trigger, not the tissue. Pseudonymise participants (R01…R20) before the main
   round. *Pending FREIC.*
6. **`confocal/006/2/Image 11_z09.png` will not download** — refused six times
   while 19 siblings arrived in 18 s. This is the field Maryam and Louise counted,
   so their agreement cannot currently select reference squares. *Likely corrupt
   server-side.*

---

## 9. Data collection

Counts post themselves to a Google Apps Script web app that appends to a Sheet
Daniela owns (`apps_script/Code.gs`, deployed 2026-08-24). Verified from the live
site end to end: the app reported a confirmed `sent ✓` — Apps Script's 302 to
`script.googleusercontent.com` carries `access-control-allow-origin: *`, so the
page can read the reply rather than falling back to the opaque no-cors path.

Rows upsert on (rater, block, mode, segment, marker), so resending or resuming
replaces earlier rows rather than duplicating them.

**GitHub was not an option and should not be revisited.** Pages is a static file
server; writing to the repository from the page would require a write-scoped token
embedded in a public page.

**What is and is not exposed.** The spreadsheet is private and the script has no
read path — `doGet` returns a fixed banner whatever it is asked, verified by
probing it. Nobody can read the data. The endpoint URL is public in
`manifest.json` by necessity, so the exposure is *write-spam*, not disclosure.

**Closed with per-counter access keys (2026-08-24).** Each counter's link carries
`&key=...`; `ACCESS_KEYS` in `Code.gs` maps key to name. The key travels only in
the emailed link, never in the published site, and the app strips it from the URL
bar after boot. The row is stamped with the name the key maps to, **not** the name
typed into the app — verified: a session typing "Someone Else" with Matt's key was
recorded as Matt. A request with no key is refused and the counter is told to
download and email instead. Keys are access control, not cryptography: they sit in
browser history and work for anyone the link is forwarded to. Leave `ACCESS_KEYS`
empty to accept anything, which keeps already-sent links working.

Undeploy the web app once collection is finished.

### Participant anonymity (`--identity code`)

Experts are named; **participants are not**. The app generates a code —
`amber-larch-63` — which the participant writes down and which becomes the only
thing linking their answers together. No name is collected and **no name-to-code
key exists for anyone to hold**, so the participant data is anonymous rather than
pseudonymous. That matters legally as well as ethically: pseudonymised data with a
key the researcher holds is still personal data under UK GDPR; genuinely anonymous
data is outside it.

The code is generated rather than chosen by the participant, which was the
original proposal. Self-chosen pseudonyms have two failure modes: several people
reach for the same obvious word and their data silently merges, and people tend to
pick something quietly identifying — a pet's name, initials and a year — which a
small department can place. Generating it removes both and costs the participant
nothing, since either way they must write it down.

Two words plus two digits from the embedded lists is ~922,000 combinations, so
with twenty participants the chance of any collision is about 0.02%. The app will
not start until they tick that they have recorded it, choosing a new code clears
that tick, and the code is shown again on the finish screen.

**Residual re-identification risk.** Even anonymous, the app records seconds per
square, brightness and contrast settings, language, and timestamps. In a pool of
twenty colleagues from one department, someone who counted at 03:00 in German is
potentially identifiable. Do not publish per-rater metadata at that granularity,
and coarsen timestamps before sharing.

**Consequence to state in the information sheet:** withdrawal is only possible
while the data still exists separately and only by quoting the code. Once results
are aggregated or published, the data cannot be found and removed.

Two test rows were written during setup and should be deleted from the Sheet:
`__TEST__` and `CONNECTIVITY_CHECK`.

---

## 10. Reproducing any of this

```bash
cd ~/Library/CloudStorage/OneDrive-UniversityofPlymouth/JupyterLab/Sclera/SCLERA_CountApp

/usr/bin/python3 tools/fetch_sources.py --fetch --watch        # get the images
/usr/bin/python3 tools/depth_profile.py --z-levels 3,5,7,9,11,13
/usr/bin/python3 analysis/legacy_agreement.py                  # Maryam vs Louise
/usr/bin/python3 tools/propose_reference.py --manifest docs/manifest.json
/usr/bin/python3 analysis/make_reference.py e1.json e2.json e3.json --manifest docs/manifest.json
/usr/bin/python3 analysis/agreement.py results/ --manifest docs/manifest.json
```

Use `/usr/bin/python3` — the bare `python3` is a broken anaconda install.

All analysis tools were verified against synthetic data with known injected error
before being trusted on real data: the marker matcher recovers an injected
2-missed / 1-invented / 3-mislabelled pattern exactly, and simulated 5/25/50%
miss rates at three depths return as F1 0.953 / 0.721 / 0.537.
