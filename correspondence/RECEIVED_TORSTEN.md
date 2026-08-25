# Received from Torsten Bossing — verbatim archive

Dr Torsten Bossing FRMS, fHEA — Associate Professor in Neurobiology, **Head of
Plymouth Light Microscopy Services**, Peninsula Medical School, University of
Plymouth.

Kept verbatim because this is expert method advice acted on in the study design,
and paraphrase would lose the detail. Our reading of each is in
[FINDINGS.md](../FINDINGS.md) §4c and §7c — **where the two differ, this file is
the source**. Typography as received.

---

## 1 — 2026-08-24 12:55

> Dear Daniela,
> I will go through your email in more details in the evening. Just an urgent question.
>
> Why do you want to re-invent what Image J can do since 2 decades? You also should have the nuclei channel in black and white and use a Z-correlation for scanning. The images you presented in the email are easy to count in Image J and black and white. In red and green you cannot be accurate.
>
> Cheers
> Torsten

**Acted on:** greyscale nuclei made the default counting view; markers given
distinct shapes as well as colours (both live 2026-08-25). The ImageJ question is
answered in §7c — the argument is validation, not capability. Note he says
"Z-correlation"; the Zeiss feature is Auto Z Brightness **Correction**, which his
next message names correctly.

---

## 2 — 2026-08-24 21:50

> Good Evening Daniela,
> The Z-correction may help. I am more famililar with Leica but I remember that in the Zeiss 710 software at the bottom of the Z-stack window you can klick on "Auto Z Brightness correction". When you activate the mode you can choose laser power, gain, digital offset and offset. Choose gain it give the strongest amplification. In Live mode you focus through the sample when the signal gets darker increase the gain and type save or add (cannot remember the command name. Continue to save different gain settings always try to make it as bright as the surface of the sample (you may have to cut signal with offset to prevent excessive background). If you now scan your sample, the software automatically increases the gain the deeper the scan goes.
>
> Cheers
> Torsten

**Acted on:** the whole of §4c. Note he cites the **710**; ours is an LSM 900, so
the control may sit elsewhere in the UI — flagged for Louise.

---

## 3 — 2026-08-25 (sent 24 Aug 22:40)

> Dear Daniela,
> Always take the surface Z-slice as your aim. The deeper slices should aim for the same brightness. Channels can be adjusted separately i.e. the EthD should be kept as bright as the surface slice. If the gain gets too strong which results in more pixelated images you can increase Average or close the Offset a little (not beyond -20). There is a gain increase which makes the image looks very artificial despite all the countermeasures. The control is a good idea.
>
> Use 3D Analyse in Image J and Thresholding to count the nuclei. In 3D mode it is clear which nuclei overlap and which are separate regardless from the Z step.
>
> Cheers
> Torsten

**Acted on:** §4c "Torsten's second answer", and the protocol in
[ACQUISITION_REQUEST_LOUISE.md](ACQUISITION_REQUEST_LOUISE.md). Four operative
points:

1. **Surface slice is the target** for every deeper slice.
2. **Channels adjusted separately**, each to its own surface brightness — *better
   than the shared schedule we asked for*, which was aimed at the wrong hazard.
3. **Average up / Offset closed, not beyond −20**, against pixelation.
4. **There is a gain level that looks artificial despite countermeasures** — he
   confirms the brightness/countability distinction is real but judges it by eye.
   We cannot resolve it from existing images (§4c), so the **control stack**, which
   he independently endorses, is the only evidence.

On **3D Analyse**: correct for the automated pipeline, and the gain ramp is what
makes a single 3D threshold defensible for the first time. It does not help the
human study (counters see 2D tiles), but it replaces our *assumed* depth overlap
with a *measured* one. See §4c.

---

## Not yet replied to

`REPLY_TO_TORSTEN_3.md` is drafted and not sent. `for_torsten/` holds the two
interface figures.

## Still outstanding from the original expert email

He has not commented on **staining** (Hoechst + EthD-1 vs alternatives) or on
**whether to section**, which remain the two blockers. Nor has he done the
four-square trial. Matt, Konstantin and Claudia have not replied at all.
