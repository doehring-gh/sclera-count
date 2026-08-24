# Reply to Torsten — Auto Z Brightness Correction

He has given a concrete, actionable answer, and it may unblock something I had
written down as unresolvable. The reply thanks him properly, then asks the two
questions his answer raises rather than treating it as settled.

---

**Subject:** Re: — that may unblock the whole depth design, thank you

Dear Torsten,

Thank you — that is more useful than you may realise, and I do not think we have
been using it.

**Why it matters more than image quality here.** I had written the depth part of
this study off as impossible. A nucleus is a 3D object and ours span a median of
about 16 µm axially, so two slices only sample genuinely different nuclei if they
are roughly 47 µm apart. But our countable range is only 26–47 µm, so there was no
pair of depths that was both countable and independent — at the 21 µm separation
we were using, about a quarter of nuclei are the same physical object at both
depths. If a gain ramp gets countable signal to 90 µm, that constraint simply goes
away: z05 and z17 become 63 µm apart and independent. So this changes the
acquisition from "could be better" to "makes the design possible", and we will
re-image rather than patch it afterwards.

Two things I would value your view on before Louise re-acquires.

**1. Does ramping gain actually recover countability, or only brightness?** Gain
amplifies noise along with signal, so it helps where read noise dominates and much
less where scattering and shot noise do. A deep slice can end up brighter without
being any easier to count. Is that distinction one you see in practice on the
Zeiss, and is there a depth beyond which you would say the ramp is cosmetic? I ask
because our failure mode is not "the image looks dark" — it is that dim live
nuclei drop below detection while brighter dead ones survive, which biases
viability rather than merely degrading it.

**2. Can we keep both channels on the same schedule?** Our dead/live call is a
comparison of EthD-1 against Hoechst at the same point. If both channels are
ramped identically the comparison survives; if the ramps differ, a nucleus could
be called dead simply because the red channel was amplified more than the blue at
that depth. Is a common schedule across channels possible, or should we record the
two separately and correct afterwards?

**Two things I will ask Louise to do**, unless you would change them:

- **save the gain schedule with the data**, per channel per slice — without it we
  cannot distinguish a genuinely bright deep nucleus from a heavily amplified dim
  one, and every downstream number depends on that;
- **acquire one control stack of the same field with the correction off.** A
  paired corrected/uncorrected stack of the same nuclei is what would let us
  actually measure whether the artefact is gone, rather than assert it. It costs
  one extra stack and it is the difference between "we fixed it" and "we can show
  we fixed it".

On the greyscale point from this morning — that is now top of my list, and I will
make it the default view rather than something you have to find. Your colour point
has also made me change the markers themselves: at the moment live and dead are
distinguished only by hue, which is exactly the mistake you flagged, so they will
get a shape difference as well.

Thank you — this was the most useful reply I could have had.

Best wishes,
Daniela

---

## Notes — not for the email

- The claim "z05 and z17 become 63 µm apart" assumes the ramp genuinely extends
  countable range to ~90 µm. It is stated as conditional in the email and must be
  verified on the new stacks with `tools/depth_profile.py` before the depth design
  is rebuilt on it.
- If he confirms a common schedule is not possible across channels, the live/dead
  call needs a per-channel correction step, and that must be built before the
  reference exercise runs on new images.
- The control stack is the load-bearing request. If only one thing survives the
  conversation, it should be that.
- Recorded in FINDINGS §4c.
