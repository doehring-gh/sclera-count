# Methodological references

Sources for the design of the SCLERA manual-count study, with what each one
actually supports in this repository. BibTeX in [`references.bib`](references.bib).

Retrieved and verified via **PubMed** and **Consensus** on 2026-08-23. Every DOI
below was read back from the PubMed record rather than written from memory — one
was wrong on first pass (the Jonkman *Nature Protocols* tutorial is
`10.1038/s41596-020-0313-9`; `10.1038/s41596-020-0307-7` is its poster).

---

## Reporting standards

**Kottner J, Audigé L, Brorson S, Donner A, Gajewski BJ, Hróbjartsson A, Roberts C,
Shoukri M, Streiner DL (2011). Guidelines for Reporting Reliability and Agreement
Studies (GRRAS) were proposed.** *J Clin Epidemiol* 64(1):96–106.
[10.1016/j.jclinepi.2010.03.002](https://doi.org/10.1016/j.jclinepi.2010.03.002)
· PMID 21130355 · also *Int J Nurs Stud* 48(6):661–71,
[10.1016/j.ijnurstu.2011.01.016](https://doi.org/10.1016/j.ijnurstu.2011.01.016)

15 reporting items covering **both interrater and intrarater** designs. Requires
that you state how raters and objects were sampled, and **the interval between
repeated measurements**.

> Used for: the whole inter/intra split; `--repeat-gap` exists and is written
> into `manifest.json` specifically because GRRAS asks for that interval.
> Use this as the reporting checklist when writing the methods section.

---

## Which statistic, and how to report it

**Koo TK, Li MY (2016). A Guideline of Selecting and Reporting Intraclass
Correlation Coefficients for Reliability Research.** *J Chiropr Med* 15(2):155–163.
[10.1016/j.jcm.2016.02.012](https://doi.org/10.1016/j.jcm.2016.02.012) · PMID 27330520

There are **10 forms of ICC**; each carries different assumptions, so the model,
type and definition must be stated. Interpretation should hang on the **95% CI**,
not the point estimate: <0.5 poor, 0.5–0.75 moderate, 0.75–0.9 good, >0.9 excellent.

> Used for: `agreement.py` reports **ICC(2,1)** — two-way random effects,
> absolute agreement, single measure (McGraw & Wong's ICC(A,1)) — with a 95% CI
> from the F distribution. On 13 repeated squares in testing the CI ran −0.13 to
> 0.77, which is exactly their argument for never quoting the point estimate alone.

**Buryska S, Arji S, Wuertz B, Ondrey F (2023). Using Bland-Altman Analysis to
Identify Appropriate Clonogenic Assay Colony Counting Techniques.**
*Technol Cancer Res Treat* 22:15330338231214250.
[10.1177/15330338231214250](https://doi.org/10.1177/15330338231214250) · PMID 37997353

Counting methods that looked unbiased on average carried strong bias **with
respect to magnitude**. Concludes that Bland–Altman or correlation **alone**
should not decide interchangeability — use them together.

> Used for: reporting ICC, detection F1, kappa and a proportional-bias slope
> side by side rather than any one of them.

---

## Manual counting agreement — the closest analogue

**Britten-Jones AC, Rajan R, Craig JP, Downie LE (2022). Quantifying corneal immune
cells from human in vivo confocal microscopy images: Can manual quantification be
improved with observer training?** *Exp Eye Res* 216:108950.
[10.1016/j.exer.2022.108950](https://doi.org/10.1016/j.exer.2022.108950) · PMID 35065982

Manual cell counting on **in vivo confocal** images, 184 images, with both
intra-observer (same observer, repeated) and inter-observer arms. Findings:

- ICC > 0.90 for total counts, intra- and inter-observer.
- **Variability rises with the number of cells in the image** — Bland–Altman bias
  increased as a function of total count.
- A **consensus training process** before counting removed the systematic
  inter-observer bias.
- Agreement was much worse for morphological subtypes than for total counts.

> Used for: the proportional-bias slope in `pairwise.csv`; the argument for small
> squares (fewer cells per judgement); and the **training round** in the app.
> The subtype finding is a warning for the live/dead mode — expect classification
> agreement to be the weaker half.

---

## Crowdsourced annotation with non-experts

**Irshad H, Montaser-Kouhsari L, Waltz G, Bucur O, Nowak JA, Dong F, Knoblauch NW,
Beck AH (2015). Crowdsourcing image annotation for nucleus detection and
segmentation in computational pathology.** *Pac Symp Biocomput* 294–305.
[10.1142/9789814644730_0029](https://doi.org/10.1142/9789814644730_0029) · PMID 25592590

4,860 crowd-annotated images. Non-expert crowd reached F-measure 87–88% against
expert pathologists for **nucleus detection** (research fellows 93.7%). Two
findings that shaped this app directly:

- **Crowd performance is strongest on small images (400×400 px) and degrades
  significantly at 600×600 and 800×800.**
- **Aggregating several annotations into a consensus gave the best performance.**

> Used for: one small square at a time rather than a whole field; `detection_f1`
> as the concordance metric; and `--replicates 3` so a consensus can be formed.

**Kentley J, Weber J, Liopyris K, Braun RP, Marghoob AA, Quigley EA, Nelson K,
Prentice K, Duhaime E, Halpern AC, Rotemberg V (2023). Agreement Between Experts
and an Untrained Crowd for Identifying Dermoscopic Features Using a Gamified App.**
*JMIR Med Inform* 11:e38412.
[10.2196/38412](https://doi.org/10.2196/38412) · PMID 36652282

139,731 crowd ratings. An untrained crowd matched a group of experts, and —
importantly — **the features experts disagreed on were the same features the
crowd disagreed on** (dots κ 0.53, globules κ 0.40 vs vessels κ 0.80).

> Used for: the expectation that low agreement on a square is evidence about the
> *image*, not only about the counters. `disagreements.csv` is built to find
> exactly those squares.

**Bafti SM, Ang CS, Hossain MM, Marcelli G, Alemany-Fornes M, Tsaousis AD (2021).
A crowdsourcing semi-automatic image segmentation platform for cell biology.**
*Comput Biol Med* 130:104204.
[10.1016/j.compbiomed.2020.104204](https://doi.org/10.1016/j.compbiomed.2020.104204)
· PMID 33429139

A web platform for non-expert annotation of microbiological images; assistive
tools cut annotation cost while preserving or improving quality.

> Used for: precedent that a browser-based annotation tool handed to non-experts
> is an accepted method, not an improvisation.

---

## Confocal methodology

**Jonkman J, Brown CM, Wright GD, Anderson KI, North AJ (2020). Tutorial: guidance
for quantitative confocal microscopy.** *Nat Protoc* 15(5):1585–1611.
[10.1038/s41596-020-0313-9](https://doi.org/10.1038/s41596-020-0313-9) · PMID 32235926

Standard reference for acquisition and analysis choices, including presenting
images in a way that preserves their quantitative nature.

> Used for: the fixed, documented display transform. Cut levels are pooled across
> the whole build and recorded in the manifest rather than adjusted per image.

---

## What is *not* covered by any of these

No paper found here measures **how manual countability changes with confocal
imaging depth**, which is the novel part of this design. The searches run were
around inter/intra-observer variability in manual cell counting, crowdsourced
biomedical image annotation, and confocal depth attenuation effects on counting;
depth attenuation is well documented optically, but not as a driver of *rater
disagreement*. Worth a more targeted search before writing it up as novel.
