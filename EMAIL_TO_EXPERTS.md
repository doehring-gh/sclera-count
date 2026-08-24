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
2. **Only click inside the dashed box.** The dimmed border is context so you can
   see cells on the edge. A cell belongs to the square its *centre* falls in.
3. **Use the brightness slider freely.** Some squares are deliberately deeper in
   the tissue and dimmer. The app records where you set it, so it is not cheating.
4. **Please do not confer with each other.** The whole value is that the four
   answers are independent — if you agree because you discussed it, we learn
   nothing, and I will have to build the standard on sand.

If a square genuinely has nothing in it, press **Nothing here**. That is a real
answer and I need it recorded as one.

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

If you know someone else with the right expertise who might be willing, tell me
and I will send them a link — more independent experts makes the reference
stronger, not weaker.

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
