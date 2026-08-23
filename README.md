# SCLERA cell count

A browser app for collecting manual cell counts from 10–20 people, and the
analysis that says where they disagree and why.

It replaces the "here is a whole field, write a number on a tally sheet" round
that Maryam and Louise did. Three things change:

- **One grid square at a time**, not a whole field. A field is 64 squares of
  about 106 µm; a square holds a countable number of nuclei.
- **Every nucleus is clicked, not tallied.** The click position is recorded, so
  two counters' marks can be matched to each other. That is what turns
  "they differ by 15" into "they differ by 15 because one of them never saw
  9 of these nuclei, and they disagree about live/dead on 6 more".
- **Depth is a factor, not a constant.** Squares are sampled at several z levels,
  so you can measure whether countability falls off with depth.

**Live now:** https://doehring-gh.github.io/sclera-count/ — currently a PILOT
build from a stand-in field, because the five real fields have not finished
downloading from OneDrive. Rebuild and push to replace it.

Send each counter their own pre-filled link:
`https://doehring-gh.github.io/sclera-count/?block=B03&mode=livedead&rater=Maryam&lang=de`

```
SCLERA_CountApp/
├── build_segments.py     cuts stacks into per-square tiles + manifest.json
├── docs/                 the app itself — this folder is what you publish
│   ├── index.html        single self-contained page, no dependencies
│   ├── manifest.json     written by build_segments.py
│   └── tiles/            written by build_segments.py
├── apps_script/Code.gs   Google Apps Script that collects counts into a Sheet
├── study.example.json    point the build at another stain, tissue or depth
├── analysis/agreement.py inter-rater agreement, object level, by depth
├── analysis/legacy_agreement.py  reads Maryam's and Louise's original tally sheets
└── testbuild/            a working demo (see "Try it now")
```

---

## Depth

Every stack is `z00..z19` at 5.263 µm per slice — about 100 µm of tissue. The
original five manual-count fields all sat at z05–z09, so depth was never a
deliberate choice. `--z-levels` samples several depths from every stack.

The attenuation is steep. Measured on `003/1/Image 1`, with one shared display
stretch so the comparison is honest:

| z | depth | Hoechst p99 |
|---|---|---|
| 11 | 57.9 µm | 71 |
| 14 | 73.7 µm | 35 |
| 16 | 84.2 µm | 22 |

At 58 µm nuclei are crisp; by 84 µm they are faint smudges. That is almost
certainly a large part of why two careful people disagree, and it is now
measurable rather than confounded.

**The same square at two depths is the same x,y location**, so depth is compared
within location rather than across fields. Two safeguards make that work:

- **No counter ever sees one location at two depths.** Otherwise at the second
  one they would be recalling their earlier answer, not counting. Enforced in
  block assignment; the build tells you if it had to drop placements to keep it.
- **The counter is never told the depth.** The app shows "Square 12 of 48" and
  nothing else — no field number, no z, no µm. Depth is joined back on from the
  manifest at analysis time. Otherwise you would be measuring their expectation
  of a hard square rather than the square.

Blocks are also shuffled, so anchors are interspersed rather than counted first
by everyone while least practised, and depths arrive interleaved.

---

## Language, and using it on a tablet or phone

The whole interface switches between **English and German** with the EN/DE
buttons, or `?lang=de` in the link. That includes the wording carried in the
manifest — channel names, task names, prompts — so a new stain added through
`study.json` supplies both languages alongside each other (`name` / `name_de`).
A missing German string falls back to English, so translation can be partial.

Counters start on a **How to count** page with worked diagrams for the two things
that actually cause disagreement: what to click, and the centre-in-the-square
edge rule. It is reachable at any time from the **?** button while counting.

Layout adapts down to a phone: the side panel becomes a strip under the image,
"nothing here" and undo stay above the fold, and the rarely-used display sliders
fold behind **More**. Pinch to zoom, drag to pan, tap a mark to remove it.

The interface is light grey, white and blue — but **the image stage stays black**,
deliberately. Confocal nuclei are faint emission on a dark ground; showing them
against white would change what a counter can see, and this study depends on the
stimulus being identical for everyone.

---

## Using another stain, tissue or depth range

Copy `study.example.json` to `study.json`, edit, and build:

```bash
/usr/bin/python3 build_segments.py --config study.json --clean
```

Everything the build assumes lives in that one file: where the images are, how
they are named, which RGB channel carries which dye, how the grid is cut, the
physical scale, and the exact wording counters read in both languages. It carries
a worked example of adding a completely new stain (DAPI + propidium iodide).
Command-line flags still override the file, and any key you leave out keeps its
default.

One constraint that is not a limitation of the code: only a stain that labels
**every** cell can support a "count the total" task. With a stain that marks a
subset there is no denominator, so offer the live/dead task instead.

---

## Reliability design, and where it comes from

**Two different quantities, often confused.** Showing one square to *several
people* measures **inter-rater** reliability — that is what `--replicates 3`
does. Showing one square to the *same person twice* measures **intra-rater**
(test–retest) reliability — that is `--repeat-fraction`. You need both, because
**intra-rater agreement is the ceiling for inter-rater agreement**: two people
cannot agree with each other more closely than each agrees with themselves. A
poor inter-rater result on its own cannot distinguish careless counters from an
irreducibly ambiguous image. `analysis/agreement.py` prints the comparison and
says which one you have.

Repeats are drawn from the first half of a counter's sequence and placed at
least `--repeat-gap` squares later, so recall is minimised, and the app shows
nothing to mark a square as a repeat.

### What the literature supports

- **GRRAS** — Kottner et al. (2011) give 15 reporting items for reliability and
  agreement studies, and explicitly cover *both* interrater and intrarater
  designs, the sampling of raters and objects, and the interval between repeated
  measurements. That interval is `--repeat-gap` and it is recorded in the
  manifest. [10.1016/j.jclinepi.2010.03.002](https://doi.org/10.1016/j.jclinepi.2010.03.002)
- **ICC reporting** — Koo & Li (2016): there are 10 forms of ICC, so the model,
  type and definition must be stated, and the 95% CI should carry the
  interpretation rather than the point estimate. This app reports **ICC(2,1)**,
  two-way random effects, absolute agreement, single measure, with a CI. Their
  bands: <0.5 poor, 0.5–0.75 moderate, 0.75–0.9 good, >0.9 excellent.
  [10.1016/j.jcm.2016.02.012](https://doi.org/10.1016/j.jcm.2016.02.012)
- **Small images count better** — Irshad et al. (2014) crowdsourced nucleus
  detection and segmentation in pathology and found crowd performance *strongest
  at 400×400 px and degrading significantly at 600×600 and 800×800*. They scored
  concordance with an F-measure, and found that aggregating several annotations
  into a consensus gave the best result. That is direct support for one small
  square at a time, for `detection_f1`, and for `--replicates 3`.
- **Training reduces inter-observer variability** — Britten-Jones et al. (2022)
  is the closest study to this one: manual counting of corneal immune cells in
  *in vivo confocal* images, with both intra- and inter-observer arms. After a
  consensus training step, ICC exceeded 0.90 and systematic inter-observer bias
  disappeared. They also found **variability rises with the number of cells in
  the image** — which is why `pairwise.csv` now reports a proportional-bias slope,
  not just a Bland–Altman mean.
- **Do not read Bland–Altman alone** — Buryska et al. (2023), counting colonies,
  found methods that looked unbiased on average carried a strong bias with
  respect to magnitude. Hence reporting ICC, F1, kappa and the bias slope together.
- **Quantitative confocal practice** — Jonkman et al. (2020), *Nature Protocols*,
  is the standard reference for acquisition and analysis choices.

### The training round

Britten-Jones et al. found a **consensus training step** was what actually removed
systematic inter-observer bias, so the app has one. Every counter starts with a
few practice squares. When they move on from each, the reference answer appears
over their own marks — green rings for nuclei you both found, dashed white for
ones they missed — with a plain-English tally, then they continue.

### Choosing which squares to train on

`analysis/legacy_agreement.py` reads Maryam's and Louise's original tally sheets
and recommends the squares. Run it first:

```bash
/usr/bin/python3 analysis/legacy_agreement.py --n-training 6
```

It picks squares where the two of them **independently reached the same total** —
so the detection reference is credible — preferring those where they then **split
on how many were dead**, because that is the judgement actually in dispute and
the one worth practising.

Their sheets record numbers, not positions, so they cannot supply the reference
marks themselves; they choose the squares, and you supply the marks.

### Making the reference — count them several times

The reference comes from **your own passes through the app**, not from the
automated detector. Training counters against the detector would make the whole
comparison circular.

Count the chosen squares **more than once**. A single pass is one opinion on one
day, and the gate then holds twenty people to it at 90%. Counting three times and
keeping only what survives removes the marks you were never sure about — a
nucleus you found in one pass out of three was not a stable observation, and
failing someone for missing it measures your noise, not theirs.

```bash
/usr/bin/python3 build_segments.py --from-grid --fields 1 --only-squares F5,E1,F4,F2,G6 --reference-passes 3 --out refbuild --clean
cd refbuild && /usr/bin/python3 -m http.server 8731
```

Count all 15 (5 squares × 3 passes, shuffled so you do not meet them in the same
order), press **Download my counts**, then:

```bash
/usr/bin/python3 analysis/make_reference.py ~/Downloads/SCLERA_..._session.json --manifest refbuild/manifest.json --out reference_consensus.json
```

A mark becomes part of the reference if it appears in a **majority of passes**;
its position is the mean of those marks and its label the majority label. The
script prints **your own agreement between passes**, which is the ceiling for the
gate:

```
your own agreement between passes: F1 0.864

  YOUR OWN passes agree at 0.86, below a 0.90 pass mark.
  A gate at 0.90 would demand participants be more consistent with you
  than you are with yourself, and most would fail on your noise.
```

Then build:

1. Build once without `--training-from`.
2. Count some squares yourself in the app and press **Download my counts** —
   you want the `*_session.json`.
3. Rebuild pointing at it:

```bash
/usr/bin/python3 build_segments.py --z-levels 5,9,13,17 --squares-per-field 16 --blocks 20 --replicates 3 --anchors 5 --repeat-fraction 0.15 --training-from ~/Downloads/SCLERA_Daniela_B01_livedead_..._session.json --training-n 6 --clean
```

### The pass gate

Participants must reproduce the reference before any of their real counts are
kept. Two separate scores, because they fail for different reasons:

| | |
|---|---|
| **number** | how close your total is to the reference, summed over the practice squares |
| **location** | detection F1 — were they the *same* nuclei, matched by position |

Both must clear `--gate-count` and `--gate-location` (default 0.90). Number alone
is not enough: marking ten wrong things scores 100% on count and nothing on
location. Location alone is not enough either, because it ignores a systematic
tendency to over- or under-count.

Failing shows a square-by-square table and **one** piece of advice aimed at what
actually went wrong — missing nuclei, marking too many, marks off-centre, or
right nuclei but wrong live/dead call. "Practice again" wipes the practice
answers and restarts the set. There is no limit on attempts; the attempt count
and both scores are written into every exported row, so you can see afterwards
who sailed through and who needed five goes.

The build refuses to let this pass silently:

```
WARNING: the reference author's own passes agree at only 0.86, below the 0.90
gate. Participants would have to beat the reference's own repeatability.
Lower --gate-location or add more reference passes.
```

**This is a workflow gate, not a security control.** It lives in the browser, so
someone determined could edit their way past it. That is why the scores are in
the exported data — the audit is the defence, not the lock.

Two properties the build enforces, both verified:

- **Training squares are held out of every counting set.** Otherwise a counter
  would later count a square whose answer they had just been shown. (This was
  wrong on the first attempt — 3 of 6 blocks contained a training square before
  the fix.)
- **Training answers never reach the results.** They are practice with the answer
  visible, so they are excluded from `rows()` and `markerRows()` entirely.
- **Returning later cannot skip the gate.** Anyone resuming without a recorded
  pass lands back on practice square 1.

Practice squares are labelled `PRACTICE 1 of 4` with "these do not count towards
your results", and the real squares are numbered from 1 independently.

---

## Staining

`czi_export.py` fixes the channel convention, and the build follows it:

| channel | dye | meaning |
|---|---|---|
| R | ethidium homodimer-1 | dead |
| G | calcein | live (Calcein/EthD scheme) |
| B | Hoechst 33342 | every nucleus (Hoechst/EthD scheme) |

The build defaults to `--scheme hoechst`, and **that is the scheme this study
needs**: only Hoechst labels every nucleus, so only it gives a *total* to count
dead against. With calcein there is no well-posed "count all the cells" task —
calcein fills live cytoplasm, which has no one-to-one relationship with nuclei.

Measured from the pixel data: specimens **001 and 002 are Calcein/EthD**, **003
is Hoechst/EthD**. The build checks each slice's channel occupancy and refuses
to run if it contradicts the scheme you asked for, so a mismatch cannot pass
silently.

---

## Build

```bash
cd ~/Library/CloudStorage/OneDrive-UniversityofPlymouth/JupyterLab/Sclera/SCLERA_CountApp && /usr/bin/python3 build_segments.py --z-levels 5,9,13,17 --squares-per-field 16 --blocks 20 --replicates 3 --anchors 5 --clean
```

- `--z-levels 5,9,13,17` — four depths spanning 26–89 µm, from every stack.
- `--squares-per-field 16` — 16 of the 64 squares per stack, **stratified by
  signal** so dense, sparse and empty squares are all represented, and **chosen
  once per stack** so the same locations are counted at every depth. Empty
  squares are kept on purpose: they are the only place a false positive can show
  up, and dropping them would flatter everyone's agreement.
- `--blocks 20 --replicates 3` — 20 counters, every square counted by 3 of them.
- `--anchors 5` — squares **everybody** counts, the common ground that puts all
  20 counters on one scale.
- `--repeat-fraction 0.15` — 15% of each counter's set is shown to them a second
  time, far later, for intra-rater reliability. `--repeat-gap 12` sets the
  minimum separation.

That build is 5 stacks × 4 depths × 16 squares = 320 segments, so roughly 48
squares each, about 35 minutes per person. The build prints the estimate. Drop
`--squares-per-field` to use all 64 (1280 segments) if you want the full grid.

Other flags: `--stacks "003/Image 5,006/Image 11"` to choose stacks,
`--scheme calcein`, `--stretch per-field`, `--from-grid`.

### What the build fixes so counters cannot drift

- **One display stretch for the whole build.** Cut levels are pooled across every
  field. This matters more than it sounds: deep slices genuinely *are* dimmer, so
  a per-field stretch would brighten them back up and erase the depth effect the
  study is trying to measure — while pulling their noise up into plausible-looking
  nuclei. `--stretch per-field` restores the old behaviour for comparison.
- **Weak fields are flagged, not silently rescued.** Any field whose signal sits
  far below the shared white point is marked `<- weak, consider dropping`.
- **The edge rule is enforced, not just written down.** Tiles carry a 12% context
  margin so a counter can see a nucleus straddling the boundary, but the app
  refuses clicks outside the square and says why. A nucleus belongs to the square
  its **centre** falls in.
- **Everything is recorded in the manifest** — cut levels, percentiles, per-channel
  stats, µm/px, z and depth per field, the assignment seed. Nothing about the
  display is a hidden degree of freedom.

### `--from-grid`

```bash
/usr/bin/python3 build_segments.py --from-grid --blocks 20
```

Cuts tiles out of the existing `COUNT_field_*_grid.png` figures instead of the
confocal stacks. That gives the **identical stimulus Maryam and Louise saw**, so
new counts stay directly comparable with theirs, and it needs no channel or
stretch decisions because the figure already made them. Single depth only — those
figures are one slice each. Use it to extend the existing round; use the stack
path to run the depth experiment.

---

## Publishing it so people can count online

The `docs/` folder is completely self-contained — one HTML file plus PNGs, no
server, no build step, no dependencies, no accounts. Any static host works.
A 320-segment build is about 8 MB of tiles; the full 1280-segment build is ~32 MB.
Both are comfortably inside every option below.

### Quickest: Netlify Drop — a public link in about a minute

1. Go to **https://app.netlify.com/drop**
2. Drag the **`docs` folder** onto the page.
3. You get a URL like `https://random-name-123.netlify.app` immediately.

No account needed to start, no command line, and you can rename the site later.
This is the least friction if you want to send the link to people this week.

### Durable: GitHub Pages

Better if the study will run for a while, because updates are a `git push` and
the URL never changes.

```bash
cd ~/Library/CloudStorage/OneDrive-UniversityofPlymouth/JupyterLab/Sclera/SCLERA_CountApp && git init -b main && git add docs README.md build_segments.py apps_script analysis && git -c user.name="Daniela Oehring" -c user.email="danielaoehring@googlemail.com" commit -m "SCLERA counting app"
```

Then on github.com: **New repository** → name it `sclera-count` → **do not** add a
README → copy the two lines it shows you under "push an existing repository", and
run them. Finally **Settings → Pages → Source: Deploy from a branch → `main` /
`/docs` → Save**.

Your link appears within a minute or two:
`https://YOURNAME.github.io/sclera-count/`

Make the repository **public** — Pages on private repos needs a paid plan, and
there is nothing sensitive here (tiles of stained tissue, no patient data).

### What will not work

**Google Drive, OneDrive and SharePoint cannot do this.** They refuse to serve
HTML as a web page — people would have to download the whole folder and open
`index.html` locally, which means 20 downloads, 20 chances to open the wrong
file, and no shared link you can fix. If you want the Drive route anyway, zip
`docs/` and tell people to unzip and double-click `index.html`; it does work
offline, it is just fragile.

### Sending people their own link

Every counter gets a different set of squares. Pre-fill it so nobody picks wrong:

```
https://YOURNAME.github.io/sclera-count/?block=B03&mode=livedead&rater=Maryam
```

`block`, `mode` and `rater` all fill themselves in. The build prints the block
names (`B01`…`B20`). Keep a list of who got which block — that is the only thing
the app cannot recover for you.

Works on a laptop or an iPad. Nothing to install.

### Collecting the counts automatically

1. Make a Google Sheet.
2. **Extensions → Apps Script**, paste `apps_script/Code.gs`.
3. **Deploy → New deployment → Web app**, **Execute as: Me**, **Who has access:
   Anyone**. (Anyone is required — counters are not signed in to your account.)
4. Rebuild with the `/exec` URL and republish:

```bash
/usr/bin/python3 build_segments.py --z-levels 5,9,13,17 --squares-per-field 16 --blocks 20 --replicates 3 --anchors 5 --endpoint 'https://script.google.com/macros/s/AKfy.../exec'
```

Counts then land in the Sheet by themselves: progress is sent every 15 squares
and again at the end, and rows are upserted on (rater, block, mode, segment) so
resending never duplicates.

**Without an endpoint the app still works** — it runs in export-only mode and each
person emails you three files. The Download button is always there regardless.

One honest caveat: Apps Script does not always let the page read its reply. When
that happens the app says **"sent, not confirmed"** rather than claiming success,
and asks the counter to email a copy too. Reconcile the Sheet against the CSVs at
the end of the round.

---

## What the counter sees

One square, filling the screen, labelled only `Square 12 of 48`. Click every
nucleus; a dot appears so they cannot lose their place or count one twice.

- `1` `2` `3` — live / dead / unsure (or one "nucleus" button in nuclei-only mode)
- `Q` `W` `E` — merged / all nuclei / dead only. **The layers are stacked and
  aligned**, so a mark placed while looking at Hoechst stays exactly where it is
  when they flip to EthD-1 to decide live vs dead.
- `U` or `⌘Z` — undo; clicking a dot removes it
- `0` — "nothing here", which is a real answer and recorded as one, not a skip
- scroll to zoom, drag to pan, sliders to brighten

Brightness and contrast are deliberately left to the counter **and recorded per
square**, so the setting becomes data rather than an uncontrolled variable. Time
per square is recorded too — useful for spotting someone who rushed.

Work saves continuously in the browser; closing the tab and returning to the same
link resumes where they left off.

---

## Analysis

```bash
cd ~/Library/CloudStorage/OneDrive-UniversityofPlymouth/JupyterLab/Sclera/SCLERA_CountApp && /usr/bin/python3 analysis/agreement.py results/ --manifest docs/manifest.json --out analysis/out
```

Point it at a folder of exported CSVs or at `summary.csv` / `markers.csv`
downloaded from the Sheet. `--manifest` joins depth back onto each segment.

For every pair of counters on their shared squares:

| | |
|---|---|
| `mean_diff`, `sd_diff`, `loa_*` | Bland–Altman on per-square counts |
| `icc21` | ICC(2,1), two-way random, absolute agreement |
| `detection_f1`, `detection_jaccard` | did they mark the *same* nuclei |
| `label_kappa` | Cohen's kappa on live/dead, over nuclei **both** marked |
| `prop_bias_slope`, `prop_bias_p` | does disagreement grow with how busy the square is |
| `intra_rater.csv` | each counter against their own repeat — the ceiling |

and then the two lines that matter:

```
of 192 disagreements between counters, 98% are about whether a nucleus is
there at all and 2% are about what to call one they both saw.

=== by depth ===
          squares  mean_n_a  mean_abs_diff  label_mismatch  detection_f1
depth_um
57.9           16      11.1           0.69               0         0.953
73.7           16       8.9           1.19               3         0.721
84.2           16       6.8           1.81               0         0.537
```

Marks are paired by optimal assignment within 8 µm (`--match-um`), not greedily,
so the pairing does not depend on the order marks happen to be listed in.
`disagreements.csv` ranks individual squares worst-first — your list of images to
look at together when calibrating counters.

Inter-rater comparisons use each counter's **first** answer only; letting the
repeat in would make one person contribute twice and confound practice with
agreement.

Both the matcher and the depth table were verified against synthetic data with
known injected error: a 2-missed / 1-invented / 3-mislabelled pattern per square
is recovered exactly, and simulated 5% / 25% / 50% miss rates at three depths
come back as F1 0.953 / 0.721 / 0.537.

---

## Try it now

```bash
cd ~/Library/CloudStorage/OneDrive-UniversityofPlymouth/JupyterLab/Sclera/SCLERA_CountApp/testbuild && /usr/bin/python3 -m http.server 8731
```

Open http://localhost:8731/. It is a three-depth build of `003/1/Image 1`
(z11/z14/z16), the stack that had downloaded when it was made. Delete
`testbuild/` before you deploy.

---

## Decisions worth revisiting

- **Which depths.** `5,9,13,17` spans 26–89 µm evenly. If the question is "where
  does it stop being countable", a denser ladder near the fall-off (say
  `9,11,13,15,17`) buys more resolution where it matters.
- **Nuclei-only vs live/dead.** Running the nuclei-only pass first, then
  live/dead, separates detection from classification disagreement by design
  rather than by analysis. If counter time is short, live/dead alone still gives
  you both, because the analysis decomposes them anyway.
- **`--replicates` vs `--blocks`.** The one-depth-per-location rule caps how much
  a single block can hold. If the build reports dropped placements, raise
  `--blocks` or lower `--replicates` — it tells you which.
- **Anchor count.** 5 squares is a thin common scale for 20 people. Raising
  `--anchors` tightens the between-counter comparison at the cost of counting time.
