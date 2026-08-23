#!/usr/bin/env python3
"""
legacy_agreement.py -- what Maryam's and Louise's tally sheets already tell us,
and which squares are worth using for the training round.

    /usr/bin/python3 analysis/legacy_agreement.py

Reads the two .xlsx tally sheets from the first counting round (64 squares of one
field, columns: counter_name, square, total, dead, unsure_optional).

Why this matters
----------------
Those sheets record NUMBERS, not positions. So they can tell you which squares
two counters found equally easy, but they cannot supply the reference marks the
training round draws -- that needs coordinates, which only a pass through the app
produces. Use this to CHOOSE the training squares; then count those few squares
in the app once to create the reference.

What it reports
---------------
Agreement is split the same way agreement.py splits it for the new data:

  detection      did they find the same NUMBER of nuclei
  classification did they call the same proportion of them dead

Those have different causes and different fixes, and in this dataset they behave
very differently.
"""

import argparse
import sys
from pathlib import Path

import numpy as np

try:
    import openpyxl
except ImportError:
    sys.exit("needs openpyxl: /usr/bin/python3 -m pip install --user openpyxl")

REPO = Path(__file__).resolve().parent.parent.parent
LEGACY = REPO / "SCLERA_Detection_Analysis" / "manual_count_experiment"

DEFAULT_SHEETS = [
    LEGACY / "Maryam Counts" / "Maryam.csv.xlsx",
    LEGACY / "Louise Counts" / "Louise LiveDead cell count.xlsx",
]


def read_tally(path):
    """square -> (total, dead, dead_was_blank). Blank dead is kept distinct from 0."""
    ws = openpyxl.load_workbook(path, data_only=True).worksheets[0]
    name, out = None, {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or not row[1]:
            continue
        sq = str(row[1]).strip()
        if len(sq) < 2 or not sq[0].isalpha():
            continue
        name = name or (str(row[0]).strip() if row[0] else path.stem)
        out[sq] = (row[2] or 0, row[3], row[3] is None)
    return name, out


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("sheets", nargs="*", type=Path, default=DEFAULT_SHEETS)
    p.add_argument("--n-training", type=int, default=6,
                   help="how many training squares to recommend")
    p.add_argument("--out", type=Path, default=None,
                   help="write the recommended square list here, one per line")
    args = p.parse_args()

    if len(args.sheets) != 2:
        sys.exit("give exactly two tally sheets")
    for f in args.sheets:
        if not f.exists():
            sys.exit(f"not found: {f}")
        if f.stat().st_blocks == 0:
            sys.exit(f"{f.name} has not downloaded from OneDrive yet -- open its "
                     f"folder in Finder and choose 'Always keep on this device'.")

    (na, A), (nb, B) = (read_tally(f) for f in args.sheets)
    sq = sorted(set(A) & set(B))
    if not sq:
        sys.exit("the two sheets share no squares")

    at = np.array([A[s][0] for s in sq], float)
    bt = np.array([B[s][0] for s in sq], float)
    ad = np.array([A[s][1] or 0 for s in sq], float)
    bd = np.array([B[s][1] or 0 for s in sq], float)
    a_blank = sum(A[s][2] for s in sq)
    b_blank = sum(B[s][2] for s in sq)

    print(f"{len(sq)} squares counted by both {na} and {nb}\n")

    print("=== detection: did they find the same nuclei? ===")
    d = at - bt
    print(f"  total nuclei      {na} {at.sum():.0f}   {nb} {bt.sum():.0f}")
    print(f"  per-square diff   mean {d.mean():+.2f}, SD {d.std(ddof=1):.2f}, "
          f"max |diff| {np.abs(d).max():.0f}")
    print(f"  correlation       r = {np.corrcoef(at, bt)[0, 1]:.3f}")
    exact = [s for s in sq if A[s][0] == B[s][0]]
    print(f"  exact agreement   {len(exact)}/{len(sq)} squares\n")

    print("=== classification: did they call the same ones dead? ===")
    dd = ad - bd
    print(f"  dead nuclei       {na} {ad.sum():.0f}   {nb} {bd.sum():.0f}")
    print(f"  per-square diff   mean {dd.mean():+.2f}, SD {dd.std(ddof=1):.2f}, "
          f"max |diff| {np.abs(dd).max():.0f}")
    print(f"  correlation       r = {np.corrcoef(ad, bd)[0, 1]:.3f}")
    va = 100 * (1 - ad.sum() / max(at.sum(), 1))
    vb = 100 * (1 - bd.sum() / max(bt.sum(), 1))
    print(f"  IMPLIED VIABILITY {na} {va:.1f}% live   {nb} {vb:.1f}% live")
    print(f"                    -> {abs(va - vb):.1f} percentage points apart\n")

    if a_blank or b_blank:
        print("  WARNING: blank 'dead' entries were left in the sheets "
              f"({na} {a_blank}, {nb} {b_blank} of {len(sq)}).")
        print("  A blank is not the same as a zero, but it has to be read as one to")
        print("  compute anything, which flatters whoever left them blank. Some of")
        print("  the viability gap above may be this and not a real difference of")
        print("  judgement. The new app removes the ambiguity: every nucleus gets an")
        print("  explicit label, and an empty square is its own recorded answer.\n")

    print("=== what this means ===")
    # The discriminator is SYSTEMATIC bias, not spread. Random scatter of similar
    # size on both measures still averages out over squares; a bias does not, and
    # it is what moves the headline viability number. So compare each mean signed
    # difference against the level it sits on.
    det_bias = abs(d.mean()) / max(np.mean([at.mean(), bt.mean()]), 1e-9)
    cls_bias = abs(dd.mean()) / max(np.mean([ad.mean(), bd.mean()]), 1e-9)
    print(f"  scatter is similar on both  (mean |diff| {np.abs(d).mean():.2f} nuclei "
          f"vs {np.abs(dd).mean():.2f} dead)")
    print(f"  but the BIAS is not:        detection {100*det_bias:.0f}% of the level, "
          f"classification {100*cls_bias:.0f}%")
    print()
    if cls_bias > det_bias * 2:
        print("  Their disagreement about which nuclei EXIST is scatter around zero --")
        print("  it cancels out and barely moves the headline number. Their")
        print("  disagreement about which are DEAD is one-directional: one of them")
        print("  calls dead consistently more often. That does not cancel, and it is")
        print("  what produces the viability gap above.")
        print()
        print("  So the counters do not need training on finding nuclei. They need an")
        print("  agreed criterion for what makes a nucleus dead. Spend the training")
        print("  round almost entirely on that.")
    elif det_bias > cls_bias * 2:
        print("  Detection carries the systematic bias: one counter consistently finds")
        print("  more nuclei. Training should concentrate on what counts as a nucleus.")
    else:
        print("  Neither measure carries a clearly larger bias. Train on both, and")
        print("  treat the scatter as the honest limit of the method.")
    print()

    # ---- recommend training squares -------------------------------------
    # A square is a good reference candidate when the two counters independently
    # arrived at the same total: that makes the detection reference credible.
    # Among those, prefer the busiest, because a square with one nucleus teaches
    # almost nothing. Squares where they agreed on the total but split on dead are
    # the most valuable of all -- the detection is settled, so the feedback
    # isolates exactly the judgement that is actually in dispute.
    cand = [s for s in exact if A[s][0] > 0]
    split = [s for s in cand if (A[s][1] or 0) != (B[s][1] or 0)]
    agreed = [s for s in cand if (A[s][1] or 0) == (B[s][1] or 0)]
    split.sort(key=lambda s: (-abs((A[s][1] or 0) - (B[s][1] or 0)), -A[s][0]))
    agreed.sort(key=lambda s: -A[s][0])

    pick, seen = [], set()
    for s in split + agreed:
        if s not in seen:
            pick.append(s); seen.add(s)
        if len(pick) >= args.n_training:
            break

    print(f"=== recommended training squares ({len(pick)}) ===")
    print("  square  total  dead(%s / %s)  why" % (na, nb))
    for s in pick:
        why = ("agreed on total, split on dead -- trains the disputed judgement"
               if s in set(split) else "agreed on total and dead -- an easy calibration case")
        print(f"  {s:<7} {A[s][0]:<6} {A[s][1] or 0} / {B[s][1] or 0:<10} {why}")
    print()
    print("  These are square NAMES, not reference marks -- the old sheets hold no")
    print("  coordinates. Count these few squares once in the app yourself, export")
    print("  the *_session.json, and pass it to build_segments.py --training-from.")
    print("  For the split ones your own answer settles which reading is right.")

    if args.out:
        args.out.write_text("\n".join(pick) + "\n")
        print(f"\nwrote {args.out}")


if __name__ == "__main__":
    sys.exit(main())
