#!/usr/bin/env python3
"""
make_reference.py -- turn several passes over the same squares into one
consensus reference the training round can mark participants against.

    /usr/bin/python3 analysis/make_reference.py ~/Downloads/SCLERA_..._session.json

Why more than one pass
----------------------
A single pass is one person's opinion on one day, and the training gate then
holds twenty people to it at 90%. Counting the same squares three times and
keeping what survives removes the marks you were never sure about: a nucleus
that appears in only one of three passes was not a stable observation, and
failing a participant for missing it would be measuring your noise, not theirs.

What survives
-------------
Marks from different passes are clustered by position (within --match-um, and at
most one mark per pass in a cluster). A cluster becomes a reference nucleus if it
appears in at least a majority of passes. Its position is the mean of its marks;
its label is the majority label, or "unsure" on a tie.

The script also reports YOUR OWN agreement between passes. That number is the
ceiling for the gate: if your three passes only agree with each other at 85%,
a 90% pass mark is asking participants to be more consistent than you are.
"""

import argparse
import json
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

import numpy as np

DEFAULT_MATCH_UM = 8.0


def load(path):
    sess = json.loads(Path(path).read_text())
    order = sess.get("order") or []
    passes = {}
    for key, st in (sess.get("seg") or {}).items():
        if not st.get("done"):
            continue
        seg_id, _, pos = key.partition("#")
        passes.setdefault(seg_id, []).append((int(pos), st))
    for k in passes:
        passes[k].sort()
    return sess, passes


def cluster(passlist, radius):
    """Group marks from several passes. At most one mark per pass per cluster."""
    clusters = []          # each: {"pts":[(pass_i, x, y, label)]}
    for pi, (_, st) in enumerate(passlist):
        for m in st.get("marks", []):
            best, bestd = None, radius
            for c in clusters:
                if any(p[0] == pi for p in c["pts"]):
                    continue
                cx = np.mean([p[1] for p in c["pts"]])
                cy = np.mean([p[2] for p in c["pts"]])
                d = float(np.hypot(m["x"] - cx, m["y"] - cy))
                if d <= bestd:
                    best, bestd = c, d
            if best is None:
                clusters.append({"pts": [(pi, m["x"], m["y"], m.get("label", "cell"))]})
            else:
                best["pts"].append((pi, m["x"], m["y"], m.get("label", "cell")))
    return clusters


def pairwise_f1(passlist, radius):
    """Mean detection F1 between every pair of the counter's own passes."""
    outs = []
    for (i, (_, a)), (j, (_, b)) in combinations(list(enumerate(passlist)), 2):
        ma, mb = a.get("marks", []), b.get("marks", [])
        if not ma and not mb:
            outs.append(1.0); continue
        used, matched = set(), 0
        for p in ma:
            best, bestd = None, radius
            for k, q in enumerate(mb):
                if k in used:
                    continue
                d = float(np.hypot(p["x"] - q["x"], p["y"] - q["y"]))
                if d <= bestd:
                    best, bestd = k, d
            if best is not None:
                used.add(best); matched += 1
        denom = 2 * matched + (len(ma) - matched) + (len(mb) - matched)
        outs.append(2 * matched / denom if denom else 1.0)
    return float(np.mean(outs)) if outs else float("nan")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("session", type=Path, help="the *_session.json from the REF pass")
    p.add_argument("--manifest", type=Path, default=Path("refbuild/manifest.json"))
    p.add_argument("--match-um", type=float, default=DEFAULT_MATCH_UM)
    p.add_argument("--min-passes", type=int, default=0,
                   help="a nucleus must appear in this many passes (default: a majority)")
    p.add_argument("--out", type=Path, default=Path("reference_consensus.json"))
    args = p.parse_args()

    if not args.session.exists():
        sys.exit(f"not found: {args.session}")
    man = json.loads(args.manifest.read_text()) if args.manifest.exists() else {}
    um_per_px = {f["field"]: f.get("um_per_px", 1.0) for f in man.get("fields", [])}
    seg_field = {s["id"]: s["field"] for s in man.get("segments", [])}

    sess, passes = load(args.session)
    if not passes:
        sys.exit("that session has no completed squares")

    print(f"reference from {sess.get('rater','?')}, mode {sess.get('mode','?')}\n")

    ref, report = {}, []
    for seg_id, plist in sorted(passes.items()):
        n = len(plist)
        need = args.min_passes or (n // 2 + 1)
        radius = args.match_um / um_per_px.get(seg_field.get(seg_id, 0), 1.0)

        cl = cluster(plist, radius)
        keep = [c for c in cl if len(c["pts"]) >= need]
        marks = []
        for c in keep:
            labs = Counter(pt[3] for pt in c["pts"])
            top, cnt = labs.most_common(1)[0]
            tied = sum(1 for _, v in labs.items() if v == cnt) > 1
            marks.append({"x": round(float(np.mean([pt[1] for pt in c["pts"]])), 1),
                          "y": round(float(np.mean([pt[2] for pt in c["pts"]])), 1),
                          "label": "unsure" if tied else top})
        ref[seg_id] = marks

        counts = [len(st.get("marks", [])) for _, st in plist]
        unanimous = sum(1 for c in keep if len(c["pts"]) == n)
        dropped = len(cl) - len(keep)
        report.append({"seg": seg_id, "passes": n, "counts": counts,
                       "kept": len(keep), "unanimous": unanimous, "dropped": dropped,
                       "f1": pairwise_f1(plist, radius)})

    print("square      passes  your counts     kept  unanimous  dropped  your own F1")
    for r in report:
        print(f"  {r['seg']:<10} {r['passes']:<7} {str(r['counts']):<15} "
              f"{r['kept']:<5} {r['unanimous']:<10} {r['dropped']:<8} {r['f1']:.3f}")

    npass = [r["passes"] for r in report]
    own = float(np.mean([r["f1"] for r in report]))
    kept = sum(r["kept"] for r in report)
    drop = sum(r["dropped"] for r in report)
    print(f"\nreference: {kept} nuclei across {len(report)} squares "
          f"({drop} marks dropped as unstable)")
    print(f"your own agreement between passes: F1 {own:.3f}")

    if min(npass) < 2:
        print("\n  WARNING: some squares were only counted once, so nothing could be")
        print("  cross-checked there. Those marks are in the reference unfiltered.")

    print()
    if own < 0.90:
        print(f"  YOUR OWN passes agree at {own:.2f}, below a 0.90 pass mark.")
        print("  A gate at 0.90 would demand participants be more consistent with you")
        print("  than you are with yourself, and most would fail on your noise.")
        print(f"  Either count more passes until this rises, or set the gate near "
              f"{max(0.6, own - 0.05):.2f}.")
    else:
        print(f"  Your passes agree at {own:.2f}, so a 0.90 gate is defensible: it asks")
        print("  participants to match a reference you can reproduce yourself.")

    out = {"schema": "sclera-count-v1", "rater": sess.get("rater", "reference"),
           "mode": sess.get("mode"), "study": sess.get("study"),
           "built_by": "make_reference.py",
           "passes_per_square": npass, "own_pairwise_f1": round(own, 4),
           "order": sorted(ref),
           "seg": {f"{k}#0": {"marks": [dict(m, t="") for m in v], "undone": [],
                              "empty": not v, "note": "", "bri": 100, "con": 100,
                              "seconds": 0, "done": True}
                   for k, v in ref.items()}}
    args.out.write_text(json.dumps(out, indent=1))
    print(f"\nwrote {args.out}")
    print("  use it with:  build_segments.py --training-from " + str(args.out))


if __name__ == "__main__":
    sys.exit(main())
