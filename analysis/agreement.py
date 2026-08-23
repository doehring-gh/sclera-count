#!/usr/bin/env python3
"""
agreement.py -- what the counters actually disagree about.

    /usr/bin/python3 analysis/agreement.py results/ --out analysis/out

Point it at a folder of the CSVs the app produces (*_summary.csv and
*_markers.csv, any number of counters), or at summary.csv / markers.csv
downloaded from the collection spreadsheet.

Why object level and not just totals
------------------------------------
Two counters reporting 40 and 55 nuclei in a square tell you they disagree but
not why. Because the app records where every click landed, their marks can be
matched to each other and the gap split into its parts:

  detection      one counter marked a nucleus the other never marked
  classification both marked the same nucleus, but called it live vs dead

Those have different fixes -- the first is a threshold or training problem, the
second is a criterion problem -- so a single "they disagree by 15" number hides
the thing worth acting on.

Outputs (CSV, in --out)
    per_square.csv     every rater x square, counts side by side
    pairwise.csv       one row per pair of raters: counts, detection, kappa
    disagreements.csv  the individual squares with the worst gaps, worst first
    matched.csv        every matched pair of marks, with both labels
    by_depth.csv       counts and detection agreement at each imaging depth

Depth
-----
The counter is never told how deep a square was imaged, so depth cannot leak
into their answer. It is joined back on from the manifest afterwards, which is
what by_depth.csv reports: whether the same square gets harder to count, and
harder to agree on, further into the tissue.
"""

import argparse
import itertools
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment
from scipy import stats

MATCH_UM = 8.0        # two marks are the same nucleus if closer than this
UM_PER_PX = 1.6604    # 850.10 um field / 512 px; overridden by --um-per-px


# --------------------------------------------------------------------- loading
def load_depths(manifest: Path):
    """segment id -> depth in um, from the manifest the app was built with.

    Depth is deliberately never shown to the counter, so it cannot come back in
    the results -- it has to be joined on afterwards from the build.
    """
    if not manifest or not manifest.exists():
        return {}, {}
    m = json.loads(manifest.read_text())
    depth = {s["id"]: s.get("depth_um") for s in m["segments"]}
    loc = {s["id"]: s.get("location") for s in m["segments"]}
    n = sum(1 for v in depth.values() if v is not None)
    if n:
        print(f"joined depth for {n} segments from {manifest}")
    return depth, loc


def load(src: Path):
    """Read every summary/marker CSV under src and concatenate."""
    if src.is_file():
        files = [src]
    else:
        files = sorted(src.rglob("*.csv"))
    if not files:
        raise SystemExit(f"no CSV files found under {src}")

    summ, mark = [], []
    for f in files:
        try:
            df = pd.read_csv(f)
        except Exception as e:
            print(f"  skipping {f.name}: {e}", file=sys.stderr)
            continue
        if {"segment", "rater"} - set(df.columns):
            continue
        (mark if "x_tile_px" in df.columns else summ).append(df)

    if not summ:
        raise SystemExit("no summary CSVs found (need columns rater, segment, n_total)")
    s = pd.concat(summ, ignore_index=True)
    if "rep" not in s.columns:
        s["rep"] = 1
    # keep rep 1 and rep 2 as separate answers -- they are the test-retest pair
    s = s.drop_duplicates(subset=["rater", "block", "mode", "segment", "rep"],
                          keep="last")
    if mark:
        m = pd.concat(mark, ignore_index=True)
        if "rep" not in m.columns:
            m["rep"] = 1
        m = m.drop_duplicates(subset=["rater", "block", "mode", "segment", "rep",
                                      "marker"], keep="last")
    else:
        m = pd.DataFrame(columns=["rater", "segment", "label", "rep",
                                  "x_tile_px", "y_tile_px"])
    print(f"loaded {len(s)} counted squares and {len(m)} marks "
          f"from {s.rater.nunique()} counters")
    return s, m


# ------------------------------------------------------------------ statistics
def icc21(mat, alpha=0.05):
    """ICC(2,1) with a 95% CI: two-way random effects, absolute agreement, single
    measure -- McGraw & Wong's ICC(A,1).

    Koo & Li (2016) ask for the model, type and definition to be stated rather
    than "ICC = 0.8", and for the CI to carry the interpretation, since a point
    estimate from few squares is very imprecise. Their bands, applied to the CI:
    <0.5 poor, 0.5-0.75 moderate, 0.75-0.9 good, >0.9 excellent.

    mat is squares x raters, complete cases only. Returns (icc, lo, hi).
    """
    mat = np.asarray(mat, float)
    n, k = mat.shape
    if n < 3 or k < 2:
        return np.nan, np.nan, np.nan
    grand = mat.mean()
    msr = k * ((mat.mean(1) - grand) ** 2).sum() / (n - 1)           # between squares
    msc = n * ((mat.mean(0) - grand) ** 2).sum() / (k - 1)           # between raters
    resid = mat - mat.mean(1, keepdims=True) - mat.mean(0, keepdims=True) + grand
    mse = (resid ** 2).sum() / ((n - 1) * (k - 1))

    denom = msr + (k - 1) * mse + k * (msc - mse) / n
    if denom <= 0:
        return np.nan, np.nan, np.nan
    icc = (msr - mse) / denom
    if not np.isfinite(icc) or abs(1 - icc) < 1e-12 or mse <= 0:
        return icc, np.nan, np.nan

    a = k * icc / (n * (1 - icc))
    b = 1 + k * icc * (n - 1) / (n * (1 - icc))
    num = (a * msc + b * mse) ** 2
    den = (a * msc) ** 2 / (k - 1) + (b * mse) ** 2 / ((n - 1) * (k - 1))
    if den <= 0:
        return icc, np.nan, np.nan
    v = num / den
    f1 = stats.f.ppf(1 - alpha / 2, n - 1, v)
    f2 = stats.f.ppf(1 - alpha / 2, v, n - 1)
    lo = n * (msr - f1 * mse) / (f1 * (k * msc + (k * n - k - n) * mse) + n * msr)
    hi = n * (f2 * msr - mse) / (k * msc + (k * n - k - n) * mse + n * f2 * msr)
    return icc, lo, hi


def proportional_bias(a, b):
    """Regress the difference on the mean: does disagreement grow with count?

    Britten-Jones et al. (2022) found exactly this for manual corneal cell counts
    on confocal images -- observers diverged more as the number of cells in an
    image rose. A Bland-Altman mean difference near zero hides it, which is why
    Buryska et al. (2023) warn against reading Bland-Altman alone.

    Returns (slope, p). A positive slope means the busier the square, the worse
    the agreement.
    """
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) < 3:
        return np.nan, np.nan
    mean, diff = (a + b) / 2, a - b
    if np.ptp(mean) == 0:
        return np.nan, np.nan
    r = stats.linregress(mean, diff)
    return r.slope, r.pvalue


def cohen_kappa(a, b):
    """Cohen's kappa for two aligned label sequences."""
    a, b = list(a), list(b)
    if not a:
        return np.nan
    cats = sorted(set(a) | set(b))
    idx = {c: i for i, c in enumerate(cats)}
    n = len(a)
    obs = sum(x == y for x, y in zip(a, b)) / n
    ca = np.bincount([idx[x] for x in a], minlength=len(cats)) / n
    cb = np.bincount([idx[x] for x in b], minlength=len(cats)) / n
    exp = float((ca * cb).sum())
    return np.nan if exp >= 1 else (obs - exp) / (1 - exp)


def match_marks(ma, mb, radius_px):
    """Optimally pair one rater's marks with another's inside a radius.

    Returns (pairs, n_only_a, n_only_b) where pairs are (label_a, label_b).
    Assignment is globally optimal rather than greedy, so the pairing does not
    depend on the order the marks happen to be listed in.
    """
    if len(ma) == 0 or len(mb) == 0:
        return [], len(ma), len(mb)

    pa = ma[["x_tile_px", "y_tile_px"]].to_numpy(float)
    pb = mb[["x_tile_px", "y_tile_px"]].to_numpy(float)
    d = np.hypot(pa[:, None, 0] - pb[None, :, 0], pa[:, None, 1] - pb[None, :, 1])

    big = radius_px * 1e3
    cost = np.where(d <= radius_px, d, big)
    ri, ci = linear_sum_assignment(cost)

    pairs = []
    used_a, used_b = set(), set()
    for i, j in zip(ri, ci):
        if d[i, j] <= radius_px:
            pairs.append((ma.iloc[i]["label"], mb.iloc[j]["label"]))
            used_a.add(i); used_b.add(j)
    return pairs, len(ma) - len(used_a), len(mb) - len(used_b)


# ----------------------------------------------------------------------- report
def analyse(summ, marks, radius_px, out: Path, top=25, depth=None):
    out.mkdir(parents=True, exist_ok=True)
    depth = depth or {}
    if depth:
        summ["depth_um"] = summ.segment.map(depth)
    summ.to_csv(out / "per_square.csv", index=False)

    pair_rows, worst_rows, matched_rows = [], [], []

    # Inter-rater comparisons use each counter's FIRST answer only. Mixing in the
    # repeat would let one counter contribute twice and would confound practice
    # with agreement.
    first = summ[summ.rep == 1] if "rep" in summ.columns else summ
    marks1 = marks[marks.rep == 1] if "rep" in marks.columns else marks

    for mode, smode in first.groupby("mode"):
        raters = sorted(smode.rater.unique())
        for ra, rb in itertools.combinations(raters, 2):
            a = smode[smode.rater == ra].set_index("segment")
            b = smode[smode.rater == rb].set_index("segment")
            shared = sorted(set(a.index) & set(b.index))
            if len(shared) < 2:
                continue

            ta = a.loc[shared, "n_total"].to_numpy(float)
            tb = b.loc[shared, "n_total"].to_numpy(float)
            diff = ta - tb

            det_a_only = det_b_only = agreed = 0
            lab_a, lab_b = [], []
            for seg in shared:
                ma = marks1[(marks1.rater == ra) & (marks1.segment == seg)]
                mb = marks1[(marks1.rater == rb) & (marks1.segment == seg)]
                pairs, only_a, only_b = match_marks(ma, mb, radius_px)
                det_a_only += only_a
                det_b_only += only_b
                agreed += len(pairs)
                for la, lb in pairs:
                    lab_a.append(la); lab_b.append(lb)
                    matched_rows.append({"mode": mode, "rater_a": ra, "rater_b": rb,
                                         "segment": seg, "label_a": la, "label_b": lb})

                mism = sum(la != lb for la, lb in pairs)
                worst_rows.append({
                    "mode": mode, "segment": seg, "depth_um": depth.get(seg),
                    "rater_a": ra, "rater_b": rb,
                    "n_a": int(a.loc[seg, "n_total"]), "n_b": int(b.loc[seg, "n_total"]),
                    "count_diff": int(a.loc[seg, "n_total"] - b.loc[seg, "n_total"]),
                    "matched": len(pairs), "only_a": only_a, "only_b": only_b,
                    "label_mismatch": mism,
                })

            union = agreed + det_a_only + det_b_only
            pair_rows.append({
                "mode": mode, "rater_a": ra, "rater_b": rb,
                "n_shared_squares": len(shared),
                "mean_a": round(ta.mean(), 2), "mean_b": round(tb.mean(), 2),
                "mean_diff": round(diff.mean(), 2),
                "sd_diff": round(diff.std(ddof=1), 2) if len(diff) > 1 else np.nan,
                # Bland-Altman limits of agreement on the per-square counts
                "loa_lower": round(diff.mean() - 1.96 * diff.std(ddof=1), 2) if len(diff) > 1 else np.nan,
                "loa_upper": round(diff.mean() + 1.96 * diff.std(ddof=1), 2) if len(diff) > 1 else np.nan,
                **dict(zip(("icc21", "icc21_lo", "icc21_hi"),
                           [round(v, 3) if np.isfinite(v) else np.nan
                            for v in icc21(np.c_[ta, tb])])),
                **dict(zip(("prop_bias_slope", "prop_bias_p"),
                           [round(v, 4) if np.isfinite(v) else np.nan
                            for v in proportional_bias(ta, tb)])),
                "matched_marks": agreed,
                "only_a": det_a_only, "only_b": det_b_only,
                # share of all marks either counter made that both agreed existed
                "detection_jaccard": round(agreed / union, 3) if union else np.nan,
                "detection_f1": round(2 * agreed / (2 * agreed + det_a_only + det_b_only), 3)
                                if union else np.nan,
                "label_kappa": round(cohen_kappa(lab_a, lab_b), 3) if lab_a else np.nan,
                "label_mismatches": int(sum(x != y for x, y in zip(lab_a, lab_b))),
            })

    # ------------------------------------------------------------ intra-rater
    # The same counter, the same square, twice, far apart in their sequence.
    # This is the ceiling for inter-rater agreement: two people cannot agree with
    # each other more closely than each agrees with themselves, so a poor
    # inter-rater result next to a poor intra-rater result means the task is
    # ambiguous, not that the counters are careless.
    intra_rows = []
    if "rep" in summ.columns and (summ.rep > 1).any():
        for (mode, rater), g in summ.groupby(["mode", "rater"]):
            piv = g.pivot_table(index="segment", columns="rep", values="n_total")
            piv = piv.dropna(subset=[c for c in (1, 2) if c in piv.columns])
            if not {1, 2}.issubset(piv.columns) or len(piv) < 2:
                continue
            t1 = piv[1].to_numpy(float)
            t2 = piv[2].to_numpy(float)
            d = t1 - t2

            agreed = only1 = only2 = 0
            la1, la2 = [], []
            for seg in piv.index:
                m1 = marks[(marks.rater == rater) & (marks.segment == seg) & (marks.rep == 1)]
                m2 = marks[(marks.rater == rater) & (marks.segment == seg) & (marks.rep == 2)]
                pr, o1, o2 = match_marks(m1, m2, radius_px)
                agreed += len(pr); only1 += o1; only2 += o2
                for x, y in pr:
                    la1.append(x); la2.append(y)

            icc, lo, hi = icc21(np.c_[t1, t2])
            union = agreed + only1 + only2
            intra_rows.append({
                "mode": mode, "rater": rater, "n_repeated_squares": len(piv),
                "mean_first": round(t1.mean(), 2), "mean_second": round(t2.mean(), 2),
                "mean_diff": round(d.mean(), 2),
                "sd_diff": round(d.std(ddof=1), 2) if len(d) > 1 else np.nan,
                "mean_abs_diff": round(np.abs(d).mean(), 2),
                "icc21": round(icc, 3) if np.isfinite(icc) else np.nan,
                "icc21_lo": round(lo, 3) if np.isfinite(lo) else np.nan,
                "icc21_hi": round(hi, 3) if np.isfinite(hi) else np.nan,
                "detection_f1": round(2 * agreed / (2 * agreed + only1 + only2), 3)
                                if union else np.nan,
                "label_kappa": round(cohen_kappa(la1, la2), 3) if la1 else np.nan,
            })
    intra = pd.DataFrame(intra_rows)
    if not intra.empty:
        intra.to_csv(out / "intra_rater.csv", index=False)

    pairwise = pd.DataFrame(pair_rows)
    worst = pd.DataFrame(worst_rows)
    matched = pd.DataFrame(matched_rows)

    pairwise.to_csv(out / "pairwise.csv", index=False)
    matched.to_csv(out / "matched.csv", index=False)
    if not worst.empty:
        worst["abs_diff"] = worst.count_diff.abs()
        worst = worst.sort_values(["abs_diff", "label_mismatch"], ascending=False)
        worst.to_csv(out / "disagreements.csv", index=False)

    # ------------------------------------------------------------------ print
    print()
    if pairwise.empty:
        print("no rater pair shares enough squares to compare yet.")
        return

    for mode, g in pairwise.groupby("mode"):
        print(f"=== {mode} ===")
        cols = ["rater_a", "rater_b", "n_shared_squares", "mean_a", "mean_b",
                "mean_diff", "sd_diff", "icc21", "detection_f1", "label_kappa"]
        print(g[cols].to_string(index=False))
        print()

        tot_only = int(g.only_a.sum() + g.only_b.sum())
        tot_mis = int(g.label_mismatches.sum())
        both = tot_only + tot_mis
        if both:
            print(f"  of {both} disagreements between counters, "
                  f"{100*tot_only/both:.0f}% are about whether a nucleus is there at all "
                  f"and {100*tot_mis/both:.0f}% are about what to call one they both saw.")
        print()

    if not intra.empty:
        print("=== intra-rater (same counter, same square, twice) ===")
        print("the ceiling for inter-rater agreement: nobody agrees with someone")
        print("else better than they agree with themselves")
        cols = ["mode", "rater", "n_repeated_squares", "mean_abs_diff",
                "icc21", "icc21_lo", "icc21_hi", "detection_f1", "label_kappa"]
        print(intra[cols].to_string(index=False))
        if not pairwise.empty:
            for mode in sorted(set(intra["mode"]) & set(pairwise["mode"])):
                wi = intra[intra["mode"] == mode].detection_f1.mean()
                be = pairwise[pairwise["mode"] == mode].detection_f1.mean()
                if np.isfinite(wi) and np.isfinite(be):
                    line = (f"\n  {mode}: within-counter detection F1 {wi:.3f}, "
                            f"between-counter {be:.3f}. ")
                    if be >= wi:
                        line += ("Between is not below within, so the counters are "
                                 "no more consistent with themselves than with each "
                                 "other -- the limit is the images, not the people. "
                                 "Training will not fix this; a clearer stimulus might.")
                    else:
                        line += (f"Between-counter agreement is {100*be/wi:.0f}% of "
                                 f"the ceiling their own repeatability allows, so "
                                 f"{100-100*be/wi:.0f}% of the gap is genuine "
                                 f"disagreement between people and is trainable.")
                    print(line)
        print()

    if not worst.empty and worst.depth_um.notna().any():
        by = worst.dropna(subset=["depth_um"]).groupby("depth_um").agg(
            squares=("segment", "nunique"),
            mean_n_a=("n_a", "mean"),
            mean_abs_diff=("count_diff", lambda v: v.abs().mean()),
            matched=("matched", "sum"),
            only_a=("only_a", "sum"),
            only_b=("only_b", "sum"),
            label_mismatch=("label_mismatch", "sum"))
        by["detection_f1"] = (2 * by.matched /
                              (2 * by.matched + by.only_a + by.only_b)).round(3)
        by["mean_n_a"] = by.mean_n_a.round(1)
        by["mean_abs_diff"] = by.mean_abs_diff.round(2)
        by = by.drop(columns=["matched", "only_a", "only_b"])
        by.to_csv(out / "by_depth.csv")
        print("=== by depth ===")
        print("does the same square get harder to count deeper in the tissue?")
        print(by.to_string())
        print()

    if not worst.empty:
        print(f"worst {min(top, len(worst))} squares (see disagreements.csv):")
        show = ["mode", "segment", "rater_a", "rater_b", "n_a", "n_b",
                "matched", "only_a", "only_b", "label_mismatch"]
        print(worst.head(top)[show].to_string(index=False))
    print(f"\nwrote {out}/pairwise.csv, per_square.csv, disagreements.csv, "
          f"matched.csv" + (", by_depth.csv" if (out / "by_depth.csv").exists() else ""))


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("src", type=Path, help="folder of exported CSVs, or one CSV")
    p.add_argument("--out", type=Path, default=Path("analysis/out"))
    p.add_argument("--match-um", type=float, default=MATCH_UM,
                   help=f"two marks are the same nucleus within this distance "
                        f"(default {MATCH_UM} um)")
    p.add_argument("--um-per-px", type=float, default=UM_PER_PX,
                   help=f"scale of the tiles (default {UM_PER_PX}, from the manifest)")
    p.add_argument("--manifest", type=Path, default=Path("docs/manifest.json"),
                   help="the manifest the app was built with, to join depth onto "
                        "each segment (depth is never shown to the counter)")
    p.add_argument("--top", type=int, default=25)
    args = p.parse_args()

    radius_px = args.match_um / args.um_per_px
    print(f"matching marks within {args.match_um} um = {radius_px:.1f} px\n")
    depth, _ = load_depths(args.manifest)
    summ, marks = load(args.src)
    analyse(summ, marks, radius_px, args.out, args.top, depth)


if __name__ == "__main__":
    sys.exit(main())
