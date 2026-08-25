# Where this project stands

**Last updated 2026-08-25.** Read this first after any gap. The reasoning behind
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
| **Expert panel — acquisition** | **answered in full** — ramp gain, per-channel, control stack endorsed (FINDINGS §4c) | nothing; protocol written for Louise |
| **Louise — re-acquisition** | protocol ready to send, not yet sent | the depth design, the reference build |
| **Matt, Konstantin, Claudia** | trial sent, no reply yet | expert consensus reference |

Torsten has replied three times, and every reply changed something.

**First**, on the interface: greyscale should be the default counting view, and
colour-coded overlays are a poor basis for accurate counting. **Both are now
done** (items 3 and 4 below, closed). He also asked why not just use ImageJ —
answered in FINDINGS §7c, and revisited below.

**Second**, the acquisition answer: **Auto Z Brightness Correction, ramping gain**,
saving a setting at each depth so deep slices come out about as bright as the
surface. Potentially unblocking rather than cosmetic — see item 1.

**Third** (2026-08-25), answering both follow-ups. Channels are ramped
**separately, each to its own surface brightness** — which is better than the
shared schedule we asked for, and revealed we had the wrong model of our own
measurement. He confirms there is a gain level where the image goes artificial but
judges it by eye; he endorses the control stack; and he recommends **3D Analyse in
ImageJ** for the overlap problem.

Three things came out of working through that reply, all in FINDINGS §4c:

- **The ramp cannot be validated from our existing images.** Simulating gain is
  structurally vacuous — detection thresholds against each slice's own noise, so
  multiplying scales signal, background and noise together and the detected set is
  unchanged (measured: identical object count from x1 to x8). Real gain acts before
  the ADC. **So the paired control stack is not good practice, it is the only
  available evidence.** It must not be dropped.
- **`depth_profile.py` would have gone silently blind on ramped data**, because it
  judged countability by absolute brightness and a ramp holds brightness constant
  by design. Fixed: it now also reports contrast and a noise-referenced ratio, with
  `--ramped` to switch the verdict. Both thresholds need re-deriving on new stacks.
- **His 3D suggestion converts an assumption into a measurement.** It does not help
  the human study (counters see 2D tiles), but instead of inferring depth overlap
  from the *median* axial extent of a nucleus, we can measure what fraction of
  nuclei actually appear at both of two candidate depths. Worth doing either way.

Replies drafted: `correspondence/REPLY_TO_TORSTEN_3.md`. Acquisition protocol for
Louise: `correspondence/ACQUISITION_REQUEST_LOUISE.md`.

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

**3. ~~Greyscale nuclei channel is not the default.~~ DONE 2026-08-25.**
Counting now opens on the greyscale Hoechst view; merged is one key away for
orientation. Prompts updated in both languages.

**4. ~~Marker colours are distinguished only by hue.~~ DONE 2026-08-25.**
Live is a circle, dead a square, unsure a triangle — shown in the palette and
taught on a marker key on the "How to count" page. Colour now reinforces the
shape rather than carrying the meaning alone.

**5. No ungated first pass (FINDINGS §7b).**
The training gate optimises the reference but destroys any claim about *natural*
observer variability, because it selects for agreement. If the "current methods
fail" paper wants that claim, participants need an ungated pass on a common set
**before** training. Decided in principle, not built.

**6. `confocal/006/2/Image 11_z09.png` will not download.**
Refused seven times while 19 siblings arrived in 18 seconds. This is the field
Maryam and Louise counted, so their agreement cannot currently be used to select
reference squares. Probably corrupt server-side.

**7. Countability thresholds are eyeballed, and the new one is transferred
(FINDINGS §4c).** `DIM_P99 = 40` was calibrated by looking at tiles. The new
`DIM_CNR = 9.0` is transferred from it rather than derived, and does not separate
the groups cleanly — two slices sit in the overlap and may be cases where the
*brightness* rule is wrong. Re-derive both on the new stacks; look at those two
tiles by eye first.

**8. Housekeeping.** `refbuild/` and `refsrc/` build outputs are tracked in git
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

1. **Send Louise the acquisition protocol** — `correspondence/ACQUISITION_REQUEST_LOUISE.md`
   is written and ready. The load-bearing items are the **saved gain and background
   per channel per slice** and the **one control stack with the correction off**;
   both are the easiest to drop and the control stack is now the only thing that
   can tell us whether the ramp worked at all.
2. **Send Torsten the third reply** (`REPLY_TO_TORSTEN_3.md`) with the two interface
   figures from `for_torsten/`, if the short note has not already gone.
3. Chase Matt, Konstantin and Claudia for trial feedback; settle staining and
   sectioning with the panel. **Staining is the older blocker and has been open
   longest** — it decides which images the reference is built on.
4. On new images: run `depth_profile.py --ramped`, re-derive both thresholds,
   measure real depth overlap by 3D linking rather than assuming it, then rebuild
   the reference pass. Only after that does the depth design get committed to.
