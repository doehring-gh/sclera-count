# Email to the reference panel — round 1: feedback, not data

**This is deliberately not the counting exercise.** The staining and imaging
questions are not settled, and if they change the images change with them, so any
counting done now would be wasted. This round asks for two things only: a short
try-out of the tool, and their opinion on the method questions. The real
reference exercise follows once those are settled.

Four personalised links to a **4-square trial**, about four minutes. Their
answers are not used as data — the point is whether the tool makes sense.

| | link |
|---|---|
| **Matt** | `https://doehring-gh.github.io/sclera-count/?rater=Matt&block=REF&mode=livedead` |
| **Thorsten** | `https://doehring-gh.github.io/sclera-count/?rater=Thorsten&block=REF&mode=livedead` |
| **Konstantin** | `https://doehring-gh.github.io/sclera-count/?rater=Konstantin&block=REF&mode=livedead` |
| **Claudia** | `https://doehring-gh.github.io/sclera-count/?rater=Claudia&block=REF&mode=livedead` |

Add `&lang=de` for German (there is also an EN/DE switch, top right).

---

**Subject:** A 4-minute look at a counting tool — and three method questions I would rather get wrong now than later

Dear Matt, Thorsten, Konstantin and Claudia,

I am building a study on how reliably people count live and dead cells in
confocal images of sclera, and eventually whether an automated pipeline can do it
instead. Before I ask anyone to count anything seriously, I would value your eyes
on two things: a tool, and a handful of decisions I am not confident about.

**Why I am asking at all**

Two colleagues already counted the same 64 squares of one field independently.
The result is uncomfortable:

- On **how many** cells there are they look close overall — 296 versus 305 — but
  that is thinner than it appears. They gave an identical number on only **19 of
  the 64 squares**, and differed by up to 7 in a single square. The totals agree
  because the differences cancel.
- On **which cells are dead** they are not close: 262 versus 180. That is a
  one-directional difference rather than scatter, so it does not cancel. It comes
  out as **11.5% versus 41.0% live** — nearly 30 percentage points of viability
  from the same images.
- And **we cannot tell whether they found the same cells at all.** The old method
  recorded only numbers on a tally sheet, so when two people both wrote "9" there
  is no way to know they meant the same nine objects. Two counters could disagree
  completely and still produce identical totals.

That last point is why the tool records where every click lands, not just how many.

**First: four squares, about four minutes**

> **Matt** — https://doehring-gh.github.io/sclera-count/?rater=Matt&block=REF&mode=livedead
> **Thorsten** — https://doehring-gh.github.io/sclera-count/?rater=Thorsten&block=REF&mode=livedead
> **Konstantin** — https://doehring-gh.github.io/sclera-count/?rater=Konstantin&block=REF&mode=livedead
> **Claudia** — https://doehring-gh.github.io/sclera-count/?rater=Claudia&block=REF&mode=livedead

Nothing to install; works on a laptop, tablet or phone. There is a short "How to
count" page first — please read it, because the rule that matters is not obvious.
Then click once on every nucleus and say whether it is live or dead.

**Please treat this as a test drive, not a measurement.** I am not going to use
these four squares as data. What I want to know is:

- Was it clear what you were being asked to do?
- Did the brightness and contrast controls do what you needed on the dimmer squares?
- Anything confusing, tedious, slow, or missing?
- Would you have wanted a different view, a different control, a different order?

It is going to roughly twenty people who are not experts, so awkwardness now is
far cheaper than awkwardness then. Blunt is more useful than kind.

**Second: three things I would like you to disagree with**

The specimens are full-thickness scleral buttons punched from the posterior pole
of fresh porcine eyes with a stamp cutter, about 4 hours post-mortem. **Not
sectioned in depth** — the tissue is intact from the surface down, so the dyes
only reach cells by diffusing in from the top. Currently Hoechst 33342 for all
nuclei and ethidium homodimer-1 for dead cells, imaged as confocal z-stacks at
5.26 µm per slice. The aim is viability through the tissue, per z-slice, not one
number per field.

**1. The staining.** I had assumed we would move to DAPI, and I now think that
would be a mistake: DAPI is membrane-impermeant, which is precisely why Hoechst
33342 is the live-cell one, so in living tissue it would behave as a second
dead-cell marker and I would lose the all-nuclei denominator that makes counting
a total meaningful. DRAQ5, the obvious far-red alternative for depth, looks worse
still for a viability assay — short exposures have been reported to induce DNA
damage responses and cell death where Hoechst under the same conditions did not.
Using a dye that kills cells to measure whether cells are alive seems like a poor
trade. So my current position is to **keep Hoechst + EthD-1**. Where I am much
less sure is whether there is a better far-red option that still gives a true
all-nuclei denominator. If you have used something that works at depth in dense
collagenous tissue, I would like to hear it.

**2. Depth, and whether we should be sectioning.** Signal dies fast. Across our
stacks the nuclear channel is essentially gone between 26 and 47 µm, and only one
reaches 68 µm. In a sclera several hundred microns thick we are sampling a thin
superficial layer — and it is the layer most exposed to handling and to the
longest dye contact. Since the tissue is not sectioned, I suspect diffusion is as
much the limit as optics. Work on other dense tissues points the same way:
intervertebral disc organ culture needed collagenase pre-treatment before
Calcein AM/EthD-1 penetrated adequately, and in cancellous bone the penetration
artefacts were only solved by cutting thick unfixed sections. **Would you section
these?** And if so how, given that cutting creates its own dead layer to exclude?

**3. A trap I think we are walking into.** Apparent viability may fall with depth
for a purely technical reason. A dead nucleus carries signal in two channels and
is brighter than a live one, so as sensitivity drops with depth the dead cells
stay detectable after the live ones have vanished. In one of our stacks the
apparent dead fraction climbs 72% → 90% → 100% while the detected count collapses
from 391 to 17. I do not believe that is the tissue dying — I think it is the
assay running out of sensitivity, with the survivors biased towards the dead. If
we report viability per z-slice without controlling for this, we will publish an
artefact. I would welcome any view on how to bound it honestly.

**And one about the specimens.** Our dead fractions look high. There is work
showing porcine retina at 240 minutes post-enucleation is significantly more
damaged than at 90 minutes. Different tissue, and sclera is far less
metabolically demanding, so I would not read it across — but our 4-hour window
sits exactly at that mark. Is that a timescale you would worry about for scleral
fibroblasts, or is sclera forgiving enough that it does not matter?

**What happens next**

Once these are settled I will send the real exercise: five or six squares,
counted three times each, roughly twenty minutes. Several of you doing that
independently gives a consensus reference — position and live/dead for every
nucleus — and, just as importantly, tells me how closely expert opinion converges
at all. That number sets the standard we can fairly hold twenty non-experts to,
so it has to be measured rather than assumed.

If you know someone else with the right expertise, please tell me and I will send
them a link. Given how far apart the first two counters turned out to be, I would
rather over-sample expert opinion than under-sample it.

Thank you — the counting is the easy part; these decisions are the part I would
rather not get wrong quietly.

Best wishes,
Daniela

---

## Notes for you, not for the email

- **Deadline** — deliberately left out. Add one.
- **The live link is currently the 4-square trial.** When the method is settled,
  rebuild the reference pass and the same links keep working:

```bash
cd ~/Library/CloudStorage/OneDrive-UniversityofPlymouth/JupyterLab/Sclera/SCLERA_CountApp && /usr/bin/python3 build_segments.py --stacks "006/Image 5" --z-levels 5,9 --squares-per-field 3 --reference-passes 3 --study "SCLERA cell count" --out docs --clean && git add -A && git commit -m "reference pass" && git push
```

- **Their trial answers are still saved** in the files they download, if you want
  a cheap early read on how far apart four experts are on four squares. Do not
  treat it as data — one pass, no repeats, and they were told it does not count.
- **When the real exercise comes back:**

```bash
/usr/bin/python3 analysis/make_reference.py ~/Downloads/SCLERA_Matt_*_session.json ~/Downloads/SCLERA_Thorsten_*_session.json ~/Downloads/SCLERA_Konstantin_*_session.json ~/Downloads/SCLERA_Claudia_*_session.json --manifest docs/manifest.json --out reference_consensus.json
```

That prints the pass mark their data supports. Use its numbers, not 0.90.

- **Everything from this work is recorded** in [FINDINGS.md](FINDINGS.md) —
  measurements, decisions and reasons, mistakes and corrections, open questions —
  with the literature in [REFERENCES.md](REFERENCES.md).
