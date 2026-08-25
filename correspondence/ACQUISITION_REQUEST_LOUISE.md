# Re-acquisition — what to set at the microscope

**For Louise. Zeiss LSM, porcine scleral buttons, Hoechst 33342 + EthD-1.**
Method from Torsten Bossing (Plymouth Light Microscopy Services), 2026-08-24/25.
Reasoning in [FINDINGS.md](../FINDINGS.md) §4c.

Everything below is one session at the scope. The order matters: the surface
setting determines the whole stack.

---

## Why we are re-imaging rather than fixing it afterwards

In the current stacks the nuclear signal is gone somewhere between 26 and 47 µm.
That is not only a quality problem. A nucleus is about 16 µm tall, so two depths
only sample *different* nuclei if they are ~47 µm apart — and with nothing
countable past 47 µm there was no pair of depths that was both countable and
independent. The depth part of the study was impossible as acquired.

If a gain ramp reaches ~90 µm, that constraint disappears. So this is not a
better-looking picture; it is the difference between having a depth design and not
having one.

---

## 1. Set the surface first, with headroom

Focus on the **surface slice** and set exposure there. This slice becomes the
brightness target for every deeper slice, so:

**Do not set the surface at or near saturation.** Leave visible headroom — the
brightest nuclei should sit clearly below the top of the range, not clipped. If
the surface is at the ceiling, every deeper slice is aimed at the ceiling too, and
bright nuclei merge into it. We tested this: pushing a shallow slice to saturation
made detected nuclei measurably *harder* to separate, not easier.

Set this for **each channel separately** (see step 3).

## 2. Auto Z Brightness Correction — ramp gain

At the foot of the Z-stack window, enable **Auto Z Brightness Correction**, and
choose **gain** as the ramped parameter (it gives the strongest amplification).

In Live mode, focus down through the sample. As the signal darkens, **raise the
gain and save that setting at that depth**, repeating at intervals, so each depth
comes out about as bright as the surface. On acquisition the software then raises
gain automatically as the scan goes deeper.

**Gain, not laser power.** More laser light means bleaching and phototoxicity, and
this is a *viability* assay — raising laser power would change the very thing we
are trying to measure.

If the gain gets strong enough to look pixelated: **increase Average**, or close
the **Offset** slightly — but **not beyond −20**.

## 3. Both channels, each aimed at its own surface

Torsten's guidance: channels can be adjusted separately, and EthD-1 should be kept
as bright as *its own* surface slice. That is what we want — it keeps each
channel's sensitivity steady with depth, which is what our live/dead call depends
on.

**Watch the EthD-1 background particularly.** Gain amplifies background along with
signal. If EthD-1 background creeps up with depth, live nuclei start to look
faintly EthD-positive and get miscalled as dead — which is precisely the artifact
we are trying to remove, arriving by a different route. Use the offset to hold the
background down rather than letting it rise.

## 4. Save the settings with the data — **per channel, per slice**

The gain schedule **and** the offset/background level, for both channels, at every
saved depth. However the software will export it (settings file, metadata, or a
screenshot of the ramp as a last resort).

Without this we cannot tell a genuinely bright deep nucleus from a heavily
amplified dim one, and every viability number downstream depends on that
distinction. **This is the one most likely to be forgotten and the most expensive
to lack.**

## 5. One control stack — correction OFF

**The same field, imaged twice: once with the correction on, once with it off.**

This is the request that matters most and the easiest to drop. Nothing we can
compute from the existing images tells us whether ramping gain restores *countable*
signal or only *brighter* signal — gain is applied before digitisation, so it
cannot be simulated afterwards. A corrected and an uncorrected stack of the *same
nuclei* is the only comparison that can answer it.

Torsten independently agreed the control is worth doing. It costs one extra stack.

## 6. Extend the z range

Do not stop at the old z19. Go as deep as the ramp still yields signal — the whole
point is to find out how far it now reaches. Keep the 5.26 µm step so the new
stacks stay comparable with the old.

## 7. If there is time — one bleaching control

Same field, imaged twice in a row with identical settings. If the second run is
dimmer, we are bleaching, and some of the depth decay we attribute to optics and
dye penetration is really just cumulative exposure. Lowest priority of the seven,
but it closes a hole we currently cannot rule out.

---

## Checklist

- [ ] surface exposure set per channel, **not clipped**
- [ ] Auto Z Brightness Correction on, **gain** ramped, saved at multiple depths
- [ ] both channels ramped, each to its own surface brightness
- [ ] EthD-1 background held flat with offset (not beyond −20)
- [ ] **gain + offset saved per channel per slice**
- [ ] **one control stack, same field, correction OFF**
- [ ] z range extended past z19, step kept at 5.26 µm
- [ ] optional: repeat-exposure bleaching control

Any of these that turn out to be impossible on the LSM — please just say which, and
we will work around it. Knowing what was *not* done is as useful as the data.
