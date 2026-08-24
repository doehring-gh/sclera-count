# Email to the reference panel

Four personalised links — each person must use their own, so the file comes back
labelled. The app remembers progress in that browser, so they can stop and return.

| | link |
|---|---|
| **Matt** | `https://doehring-gh.github.io/sclera-count/?rater=Matt&block=REF&mode=livedead` |
| **Thorsten** | `https://doehring-gh.github.io/sclera-count/?rater=Thorsten&block=REF&mode=livedead` |
| **Konstantin** | `https://doehring-gh.github.io/sclera-count/?rater=Konstantin&block=REF&mode=livedead` |
| **Claudia** | `https://doehring-gh.github.io/sclera-count/?rater=Claudia&block=REF&mode=livedead` |

Add `&lang=de` to any link to open it in German (there is also an EN/DE switch top right).

---

**Subject:** Would you count some cells for me? ~20 minutes, and it sets the standard for the whole study

Dear Matt, Thorsten, Konstantin and Claudia,

I am asking a small favour that carries more weight than it looks.

We are setting up a study on how reliably people count live and dead cells in
confocal images of sclera — and, in the end, whether an automated pipeline can
replace that. Before we can ask ~20 people to count, we need a reference: an
agreed answer for a handful of images, saying not just *how many* cells there
are but *where* each one is and whether it is live or dead.

That reference is what everyone else will be measured against, so it has to come
from people who know what they are looking at. Hence the four of you.

**Why we cannot just carry on as we were**

Two colleagues already counted the same 64 squares of one field independently.
The result is uncomfortable:

- On **how many** cells there are, they are close overall — 296 versus 305 — but
  that agreement is thinner than it looks. They gave an identical number on only
  **19 of the 64 squares**, and differed by up to 7 in a single square. The totals
  match largely because the differences cancel out.
- On **which cells are dead**, they are not close at all: 262 versus 180. That is
  a one-directional difference, not scatter — one of them calls dead consistently
  more often, so it does not cancel. It comes out as **11.5% versus 41.0% live**.
  Nearly 30 percentage points of viability, from the same images.
- Worst of all, **we cannot tell whether they found the same cells**. The old
  method recorded only numbers on a tally sheet, so when two people both wrote
  "9" we have no way of knowing whether they meant the same nine objects. Two
  counters could disagree completely and still produce identical totals.

That last point is the reason for this exercise. This time every click is recorded
with its position, so we can match your answers to each other cell by cell and
say precisely where expert judgement converges and where it does not. It also
means the live/dead question — clearly the harder one — can be looked at only for
cells that everyone actually found.

**What it involves — about 20 minutes**

Open your own link (each is different, so your answers come back labelled):

> **Matt** — https://doehring-gh.github.io/sclera-count/?rater=Matt&block=REF&mode=livedead
> **Thorsten** — https://doehring-gh.github.io/sclera-count/?rater=Thorsten&block=REF&mode=livedead
> **Konstantin** — https://doehring-gh.github.io/sclera-count/?rater=Konstantin&block=REF&mode=livedead
> **Claudia** — https://doehring-gh.github.io/sclera-count/?rater=Claudia&block=REF&mode=livedead

Nothing to install. It works on a laptop, tablet or phone, though a larger screen
is easier. There is a short "How to count" page first — please do read it, the
one rule that matters is not obvious. There is also an English/German switch in
the top right.

You will then get 18 small squares, one at a time. **Click once on every nucleus**
and say whether it is live or dead. A dot appears where you click, so you cannot
lose your place; click a dot again to remove it.

**Four things worth knowing**

1. **You will see each square three times.** That is deliberate — it tells us how
   reproducible the answer is. Please count each one *fresh* rather than trying to
   remember what you did before. They are shuffled to make that easier.
   If your three passes disagree with each other, that is useful information and
   not a failure — it puts a ceiling on what we can fairly ask of anyone else.
2. **Only click inside the dashed box.** The dimmed border is context so you can
   see cells on the edge. A cell belongs to the square its *centre* falls in.
3. **Use the brightness slider freely.** Some squares are deliberately deeper in
   the tissue and dimmer. The app records where you set it, so it is not cheating.
4. **Please do not confer with each other.** The whole value is that the four
   answers are independent — if you agree because you discussed it, we learn
   nothing, and I will have to build the standard on sand.

If a square genuinely has nothing in it, press **Nothing here**. That is a real
answer and I need it recorded as one.

**The specimens, so you know what you are advising on**

Full-thickness scleral buttons punched from the posterior pole of fresh porcine
eyes with a stamp cutter (fixed width and length), roughly 4 hours post-mortem.
Not sectioned in depth — the tissue is intact from the surface down, so the dyes
reach the cells only by diffusing in from the top. Currently Hoechst 33342 for
all nuclei and ethidium homodimer-1 for dead cells, imaged as confocal z-stacks
at 5.26 µm per slice.

**Four things I would genuinely value your view on**

I have been through the images and the literature and formed some opinions. I
would rather have them corrected now than defended later, so please push back.

**1. The staining.** My current thinking is to *keep* Hoechst + EthD-1 rather
than change it. I had considered moving to DAPI, but DAPI is membrane-impermeant
— that is precisely why Hoechst 33342 is the live-cell one — so in living tissue
it would behave as a second dead-cell marker and I would lose the "all nuclei"
denominator that makes counting a total meaningful. DRAQ5, the obvious far-red
alternative for depth, looks worse for a viability assay specifically: short
exposures have been reported to induce DNA damage responses and cell death where
Hoechst under the same conditions did not. Using a dye that kills cells to
measure whether cells are alive seems like a bad trade.

Where I am much less sure: whether there is a better far-red option that keeps a
true all-nuclei denominator, given how much depth we are losing. If you have used
something in dense collagenous tissue that works at depth, I would like to hear it.

**2. Depth — and a problem I think is bigger than the dye.** Signal dies fast.
Measured across our stacks, the nuclear channel is essentially gone somewhere
between 26 and 47 µm, and only one stack reaches 68 µm. In a sclera several
hundred microns thick, we are sampling a thin superficial layer — and it is the
layer most exposed to handling and to the longest dye contact.

Two things follow, and I would like your opinion on both:

- Because the tissue is not sectioned, I suspect diffusion is as much the limit
  as optics. Work on other dense tissues points the same way: intervertebral disc
  organ culture needed collagenase pre-treatment before Calcein AM/EthD-1
  penetrated adequately, and in cancellous bone the penetration artefacts were
  only solved by cutting thick unfixed sections. Would you section these, and if
  so how, accepting that cutting creates its own dead layer to exclude?

- More worrying: apparent viability may fall with depth for a purely technical
  reason. A dead nucleus carries signal in two channels and is brighter than a
  live one, so as sensitivity drops with depth the dead cells stay detectable
  after the live ones have disappeared. In one of our stacks the apparent dead
  fraction climbs 72% → 90% → 100% as the detected count collapses from 391 to
  17. I do not think that is the tissue dying; I think it is the assay running out
  of sensitivity. If we report viability per z-slice without controlling for it,
  we will publish an artefact. I would welcome any view on how to bound this
  properly.

**3. A question about the specimens themselves.** Our dead fractions look high to
me. There is work showing porcine retina at 240 minutes post-enucleation has
significantly more damage and apoptosis than at 90 minutes — different tissue, and
sclera is far less metabolically demanding, so I would not read it across
directly. But our 4-hour window sits exactly at that mark. Is that a timescale
you would worry about for scleral fibroblasts, or is sclera forgiving enough that
it does not matter?

**4. The tool itself.** Was it clear what you were being asked to do? Anything
confusing, tedious, or missing? Did the brightness control do what you needed on
the dimmer squares? It is about to go to roughly twenty non-experts, so
awkwardness now is far cheaper than awkwardness then — blunt feedback is more
useful than kind feedback.

**When you are done**

Press **Download my counts**. You will get three files. Please send me all three,
but the important one ends in `_session.json`.

If you get halfway and stop, just reopen the same link on the same device — it
picks up where you left off.

**One thing I will do with it**

Your individual answers get combined into a consensus, and I will also look at how
closely each of you matched that consensus. That number sets the pass mark for
everyone else, so if the four of you agree at 85% rather than 95%, the standard we
hold participants to has to reflect that. I will report those figures anonymously
(Expert A, B, C, D) unless you would rather be named.

Given how far apart the first two counters turned out to be, I would rather
over-sample the expert opinion than under-sample it. **If you know someone else
with the right expertise who might be willing, tell me and I will send them a
link** — more independent experts makes the reference stronger, not weaker.

One caveat in fairness: if the staining does change, the images change with it,
and I may have to ask you to repeat this on the new ones. I would rather warn you
now than surprise you later. Your answers on this set are not wasted either way —
they tell me how much expert opinion converges at all, which is the number that
decides what we can fairly ask of everyone else.

Thank you — this is genuinely the part the rest of the study rests on.

Best wishes,
Daniela

---

## Notes for you, not for the email

- **Deadline** — I have deliberately left one out. Add one; a request with no date
  tends to sit.
- **Naming** — the links carry their first names, which is fine for an expert panel
  contributing a reference. For the ~20 participants later I would switch to codes
  (see the ethics note).
- **If someone else joins**, their link is the same with `?rater=TheirName`.
  `make_reference.py` takes any number of expert files.
- **When the files come back:**

```bash
cd ~/Library/CloudStorage/OneDrive-UniversityofPlymouth/JupyterLab/Sclera/SCLERA_CountApp && /usr/bin/python3 analysis/make_reference.py ~/Downloads/SCLERA_Matt_*_session.json ~/Downloads/SCLERA_Thorsten_*_session.json ~/Downloads/SCLERA_Konstantin_*_session.json ~/Downloads/SCLERA_Claudia_*_session.json --manifest docs/manifest.json --out reference_consensus.json
```

That prints the pass mark their data supports. Use the numbers it gives, not 0.90
by default.
