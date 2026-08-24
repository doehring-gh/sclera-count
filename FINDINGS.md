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

The endpoint URL is public in `manifest.json` by necessity. Undeploy the web app
once collection is finished.

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
