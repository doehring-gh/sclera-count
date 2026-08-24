# Where this project stands

**Last updated 2026-08-24.** Read this first after any gap. The reasoning behind
everything here is in [FINDINGS.md](FINDINGS.md); the build and workflow are in
[README.md](README.md).

---

## In one paragraph

The counting tool is built, deployed and tested. The ethics application has been
submitted and we are waiting on PIERC. A four-square trial went to the expert
panel for interface feedback — Torsten Bossing has replied, the other three have
not. **Two things must resolve before the real reference exercise can run:
PIERC approval, and the panel's answers on staining and whether to section the
tissue.** Everything downstream of those is written and tested.

---

## Waiting on

| | | blocks |
|---|---|---|
| **PIERC approval** | submitted, reference pending | the participant round |
| **Expert panel — staining** | keep Hoechst + EthD-1, or move? | which images the reference is built on |
| **Expert panel — section or not** | sectioning buys depth, costs a cut-face artifact | the whole depth design |
| **Expert panel — acquisition** | **answered** — Auto Z Brightness Correction, ramp gain (FINDINGS §4c) | re-acquisition, then the depth design |
| **Matt, Konstantin, Claudia** | trial sent, no reply yet | expert consensus reference |

Torsten has replied twice. First on four points: greyscale should be the default
view (agreed, not yet done), colour-coded overlays are a poor basis for counting
(agreed — the markers need a shape difference too), Z-correction at acquisition,
and why not just use ImageJ (answered in FINDINGS §7c — the argument is validation,
not capability).

Then with the acquisition answer: **Auto Z Brightness Correction, ramping gain**,
saving a setting at each depth so the deep slices come out about as bright as the
surface (FINDINGS §4c). This is potentially unblocking rather than cosmetic — see
item 1 below. Reply drafted in `correspondence/REPLY_TO_TORSTEN_2.md`, asking
whether gain recovers countability or only brightness, and whether both channels
can share one schedule.

---

## Live now

**https://doehring-gh.github.io/sclera-count/** — the four-square trial, export
only, no data collection endpoint. This is what the panel was sent.

The **participant** build is a different configuration of the same app and is
tested but not deployed: anonymous codes, consent page, training round and pass
gate. It goes live when ethics clears.

---

## Ready to run the moment approval lands

All tested, nothing outstanding:

- **Reference pass** — `--reference-passes 3`, several experts, shuffled order
- **Consensus + derived pass mark** — `analysis/make_reference.py`, two-stage
  majority, prints the gate the experts' own agreement actually supports
- **Participant round** — anonymous codes, consent page, training, 90%-style gate
  with the threshold taken from the reference data rather than assumed
- **Agreement analysis** — `analysis/agreement.py`: ICC(2,1) with CI,
  Bland–Altman with proportional bias, object-level detection F1, Cohen's kappa,
  intra-rater ceiling, by-depth breakdown
- **Ethics documents** — all four filled and in `ethics/`

---

## Known and not yet fixed

Ordered by how much they matter.

**1. The depth design is blocked on re-acquisition (FINDINGS §4b, §4c).**
Nuclei span a median of 3 slices (15.8 µm), so two depths only sample different
nuclei if they are ~47 µm apart — but the usable depth range is only 26–47 µm.
The current reference build uses z05 and z09, 21 µm apart, where **roughly a
quarter of nuclei are physically the same object at both depths**. The
"no counter sees one location at two depths" rule prevents recognising a *square*;
it does not prevent meeting the same *nucleus*.

**Torsten's gain ramp may remove this**, by extending countable range rather than
changing separation: countable signal to ~90 µm would make z05/z17 independent at
63 µm. That is conditional and must be verified with `tools/depth_profile.py` on
the new stacks before the depth design is rebuilt on it. **Do not build the depth
comparison on the current images.**

**2. No sensitivity floor for per-slice viability (FINDINGS §4).**
Apparent dead fraction rises with depth because dead nuclei are brighter and
outlive live ones as sensitivity falls. Reporting viability per z-slice without
bounding this would publish an artifact. Unsolved.

**3. Greyscale nuclei channel is not the default.**
Promised to Torsten. The merged view is for orientation; counting should happen
on the single greyscale channel. One-line change, not yet made.

**4. Marker colours are distinguished only by hue.**
Live blue / dead red / unsure yellow. Around one man in twelve cannot rely on a
red–green pair, and colour-only coding is weak generally. Needs a shape or fill
difference as well as colour.

**5. No ungated first pass (FINDINGS §7b).**
The training gate optimises the reference but destroys any claim about *natural*
observer variability, because it selects for agreement. If the "current methods
fail" paper wants that claim, participants need an ungated pass on a common set
**before** training. Decided in principle, not built.

**6. `confocal/006/2/Image 11_z09.png` will not download.**
Refused seven times while 19 siblings arrived in 18 seconds. This is the field
Maryam and Louise counted, so their agreement cannot currently be used to select
reference squares. Probably corrupt server-side.

**7. Housekeeping.** `refbuild/` and `refsrc/` build outputs are tracked in git
and are regenerable; they could be gitignored like `testbuild/`.

---

## Decisions already made, so they are not reopened by accident

- **Staining: keep Hoechst 33342 + EthD-1.** DAPI rejected (membrane-impermeant,
  would act as a second dead marker and destroy the all-nuclei denominator).
  DRAQ5 rejected (kills cells at short exposure where Hoechst does not). Open only
  to the expert panel overturning it.
- **Participants are anonymous, not pseudonymous.** A code the participant holds,
  no code-to-identity key anywhere. Stronger than a key held by the researcher,
  and it puts the data outside UK GDPR.
- **Consent is on-screen, not signed.** A signature would collect a name and
  destroy the anonymity. The departure from the template is stated on the form.
- **No third-party data platform.** Export-only; participants return their file
  and it lives in University OneDrive. The paperwork and the software agree.
- **Access keys must never be used for the participant round.** They identify the
  counter by design; the collector now refuses that combination outright.
- **The pass mark is derived, never assumed.** From what the expert panel achieve
  against their own consensus.
- **Display stretch is global across a build**, so a dim deep slice renders dim
  rather than having its noise amplified into plausible nuclei.

---

## The next four things, in order

1. **Re-acquire with Auto Z Brightness Correction** (FINDINGS §4c). Ask Louise
   for: gain ramp saved with the data per channel per slice; the same schedule on
   both channels if possible; **one control stack of the same field with the
   correction off**; and an extended z range. The control stack is the one that
   turns "we fixed it" into "we can show we fixed it", and it is the request most
   likely to be dropped.
2. Make the greyscale channel the default and give the markers a shape difference
   as well as colour — both small, both promised to Torsten, and both should land
   before anything goes to twenty people.
3. Chase Matt, Konstantin and Claudia for trial feedback; settle staining and
   sectioning with the panel.
4. On PIERC approval and new images: verify countable depth, rebuild the reference
   pass, run it with the panel, derive the gate from `make_reference.py`, then open
   the participant round.
