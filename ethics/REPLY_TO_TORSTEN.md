# Reply to Torsten Bossing

He is right on two of his four points, and the third is feedback we asked for.
Written to concede that plainly and give him something substantive for the
evening.

---

**Subject:** Re: — you are right about the greyscale, and I want your view on the Z-correction

Dear Torsten,

Thank you — that is a genuinely useful reply, and you are right on more of it than
I would like.

**On black and white: you are right, and the fact that you could not tell is my
fault.** The tool does have a greyscale nuclei channel — there are three views the
counter can switch between with one key: Hoechst alone in greyscale, EthD-1 alone
in greyscale, and the merged view. Marks stay in place when you switch, so the
intended workflow is to find nuclei on the greyscale Hoechst image and only then
flip to the dead channel to judge each one. The merged view is for orientation,
not for counting.

But the images in my email were the merged view, so you had no way of knowing
that, and if it was not obvious to you it will not be obvious to anyone. That is
exactly the interface feedback I was asking for, and I will make the greyscale
channel the default rather than something you have to discover.

**On red and green: agreed, and it is worse than an aesthetic problem.** Our
merged view is red and blue rather than red and green, but your point stands —
colour-coded overlays are a poor basis for accurate counting, and around one man
in twelve cannot use a red/green pair reliably at all. It is another argument for
counting on the single greyscale channel and using colour only for orientation.

**On the Z-correction: this is the part I would most like your advice on, and I do
not think we used it.** We have a measured problem that sounds like exactly what
you are pointing at. Across our stacks the Hoechst signal is essentially gone
somewhere between 26 and 47 µm, and in one specimen it is not countable at any
depth. The tissue is a full-thickness scleral button, not sectioned, so the dye
also has to diffuse in from the surface — which means I cannot currently separate
optical attenuation from dye penetration.

Worse, we get an artefact that would corrupt the headline number: a dead nucleus
carries signal in two channels and is brighter than a live one, so as sensitivity
falls with depth the dead cells stay detectable after the live ones have vanished.
In one stack the apparent dead fraction climbs from 72% to 90% to 100% while the
detected count collapses from 391 to 17. That is not the tissue dying, it is the
assay running out of sensitivity — and if we reported viability per z-slice
without controlling for it we would publish an artefact.

If a Z-correction ramp on the LSM 900 would flatten that out, it changes the
acquisition rather than the analysis, and I would rather redo the imaging properly
than correct for it afterwards. What would you recommend?

**On ImageJ — and here I think I explained the project badly.** I am not trying to
build a cell counter. ImageJ counts these images perfectly well, and so does our
own pipeline; that is not the difficulty.

The difficulty is that every automated method, ImageJ included, gets validated
against manual counts treated as ground truth — and we have reason to think that
ground truth does not hold. Two experienced colleagues independently counted the
same 64 regions of one of these fields. Their totals agreed in aggregate, 296
against 305, but matched exactly in only 19 of the 64 regions, and their dead
counts diverged systematically, 262 against 180. That is 11.5% versus 41.0%
viability from identical images. And because the old method recorded only totals
and not positions, we cannot even establish whether they were looking at the same
cells.

So the tool is not a counter competing with ImageJ. It is an instrument for
measuring how reproducible human counting actually is, which is why it records
where every click lands rather than just how many there were. If that
reproducibility turns out to be poor, then the validation standard the whole field
uses — including for ImageJ — is weaker than assumed, and that is the finding.

The four minutes I asked for is not a counting exercise, and I am deliberately not
collecting it as data yet. It is a test drive, so that people like you can tell me
what is wrong with it before I hand it to twenty non-experts. You have already
found one thing.

Look forward to the longer read this evening — particularly on the acquisition.

Best wishes,
Daniela

---

## Notes for you, not for the email

- **He is right about the default view and I would change it before anyone else
  looks.** The build sets the default layer per counting mode; for `livedead` it
  is currently `merged`. One-line change to `nuclei`.
- **The Z-correction point is the most valuable thing in his email.** If the LSM
  900 can ramp gain or laser power with depth, and it was not used, that may
  explain a large part of the 26–47 µm ceiling — and it is fixable at acquisition
  rather than in analysis. He runs the microscopy service, so he is the right
  person to ask and the ask is free.
- **Do not concede the ImageJ point beyond what is written.** ImageJ is one of the
  methods under test in the first paper, not an alternative to the app. The reply
  says this without being combative.
- I have not mentioned the anonymous participant codes or the ethics application;
  keep this reply on the science.
