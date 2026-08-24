#!/usr/bin/env python3
"""
make_reference.py -- build a consensus reference from several experts, each of
whom counted the same squares several times, and DERIVE the pass mark from what
those experts actually achieved.

    /usr/bin/python3 analysis/make_reference.py expert1.json expert2.json expert3.json \\
        --manifest docs/manifest.json --out reference_consensus.json

Two stages, not one pool
------------------------
Pooling all nine passes and taking a majority lets one generous counter dominate:
they contribute three votes to every mark they alone made. Instead:

  1. within an expert, a mark survives if it appears in a majority of THEIR passes
     -- this uses the repeats for what they are for, stability, not extra votes
  2. across experts, a mark enters the reference if a majority of EXPERTS found it
     -- one vote each, regardless of how trigger-happy anyone is

Labels are settled separately from positions. A nucleus everyone located but split
on live/dead becomes "unsure" and is excluded from the label score: failing a
participant on a call three experts could not agree on is indefensible.

Setting the pass mark
---------------------
The gate must come out of this file, not out of a round number. Each expert is
scored against the consensus they helped build, which is the most favourable test
there is -- and that is the ceiling. If the best experts only reach 0.84 against
their own consensus, a 0.90 gate fails everyone and you would wrongly conclude the
participants were careless.
"""

import argparse
import json
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

import numpy as np

DEFAULT_MATCH_UM = 8.0


def load_expert(path):
    """name -> {segment: [pass marks, ...]}"""
    sess = json.loads(Path(path).read_text())
    name = sess.get("rater") or Path(path).stem
    per = {}
    for key, st in (sess.get("seg") or {}).items():
        if not st.get("done"):
            continue
        seg_id, _, pos = key.partition("#")
        per.setdefault(seg_id, []).append((int(pos or 0), st.get("marks", [])))
    for k in per:
        per[k].sort()
        per[k] = [m for _, m in per[k]]
    return name, per, sess


def cluster(groups, radius):
    """Cluster marks from several sources; at most one mark per source per cluster.

    `groups` is a list of mark-lists. Returns clusters of (source_index, x, y, label).
    """
    clusters = []
    for gi, marks in enumerate(groups):
        for m in marks:
            best, bestd = None, radius
            for c in clusters:
                if any(p[0] == gi for p in c):
                    continue
                cx = np.mean([p[1] for p in c]); cy = np.mean([p[2] for p in c])
                d = float(np.hypot(m["x"] - cx, m["y"] - cy))
                if d <= bestd:
                    best, bestd = c, d
            (best if best is not None else clusters.append([]) or clusters[-1]).append(
                (gi, m["x"], m["y"], m.get("label", "cell")))
    return clusters


def f1_between(a, b, radius):
    if not a and not b:
        return 1.0
    used, matched = set(), 0
    for p in a:
        best, bestd = None, radius
        for k, q in enumerate(b):
            if k in used:
                continue
            d = float(np.hypot(p["x"] - q["x"], p["y"] - q["y"]))
            if d <= bestd:
                best, bestd = k, d
        if best is not None:
            used.add(best); matched += 1
    den = 2 * matched + (len(a) - matched) + (len(b) - matched)
    return 2 * matched / den if den else 1.0


def label_agreement(a, b, radius):
    """Of the marks both found, what fraction carry the same label."""
    used, same, tot = set(), 0, 0
    for p in a:
        best, bestd = None, radius
        for k, q in enumerate(b):
            if k in used:
                continue
            d = float(np.hypot(p["x"] - q["x"], p["y"] - q["y"]))
            if d <= bestd:
                best, bestd = k, d
        if best is not None:
            used.add(best); tot += 1
            same += (p.get("label") == b[best].get("label"))
    return (same / tot) if tot else float("nan"), tot


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("sessions", nargs="+", type=Path,
                   help="one *_session.json per expert (each containing their passes)")
    p.add_argument("--manifest", type=Path, default=Path("docs/manifest.json"))
    p.add_argument("--match-um", type=float, default=DEFAULT_MATCH_UM)
    p.add_argument("--min-passes", type=int, default=0, help="default: majority of passes")
    p.add_argument("--min-experts", type=int, default=0, help="default: majority of experts")
    p.add_argument("--out", type=Path, default=Path("reference_consensus.json"))
    args = p.parse_args()

    man = json.loads(args.manifest.read_text()) if args.manifest.exists() else {}
    umpp = {f["field"]: f.get("um_per_px", 1.0) for f in man.get("fields", [])}
    seg_field = {s["id"]: s["field"] for s in man.get("segments", [])}
    seg_square = {s["id"]: s.get("square", s["id"]) for s in man.get("segments", [])}

    experts = []
    for f in args.sessions:
        if not f.exists():
            sys.exit(f"not found: {f}")
        experts.append(load_expert(f))
    names = [e[0] for e in experts]
    if len(set(names)) != len(names):
        names = [f"{n} ({f.stem})" for n, f in zip(names, args.sessions)]
    print(f"{len(experts)} expert(s): {', '.join(names)}\n")

    segs = sorted({s for _, per, _ in experts for s in per})
    need_e = args.min_experts or (len(experts) // 2 + 1)

    ref, per_expert_marks = {}, {n: {} for n in names}
    rows, split_labels = [], 0
    for seg in segs:
        radius = args.match_um / umpp.get(seg_field.get(seg, 0), 1.0)

        # ---- stage 1: each expert's own passes -> that expert's marks
        expert_marks, within = [], []
        for (name, per, _), disp in zip(experts, names):
            plist = per.get(seg, [])
            if not plist:
                expert_marks.append([]); within.append(float("nan")); continue
            need_p = args.min_passes or (len(plist) // 2 + 1)
            cl = cluster(plist, radius)
            keep = [c for c in cl if len(c) >= need_p]
            mk = []
            for c in keep:
                lab = Counter(pt[3] for pt in c).most_common(1)[0][0]
                mk.append({"x": round(float(np.mean([pt[1] for pt in c])), 1),
                           "y": round(float(np.mean([pt[2] for pt in c])), 1),
                           "label": lab})
            expert_marks.append(mk)
            per_expert_marks[disp][seg] = mk
            within.append(np.mean([f1_between(a, b, radius)
                                   for a, b in combinations(plist, 2)])
                          if len(plist) > 1 else float("nan"))

        # ---- stage 2: across experts -> the reference
        cl = cluster(expert_marks, radius)
        keep = [c for c in cl if len(c) >= need_e]
        marks = []
        for c in keep:
            labs = Counter(pt[3] for pt in c)
            top, cnt = labs.most_common(1)[0]
            tie = sum(1 for v in labs.values() if v == cnt) > 1
            if tie:
                split_labels += 1
            marks.append({"x": round(float(np.mean([pt[1] for pt in c])), 1),
                          "y": round(float(np.mean([pt[2] for pt in c])), 1),
                          "label": "unsure" if tie else top,
                          "label_split": bool(tie)})
        ref[seg] = marks
        rows.append({"seg": seg, "square": seg_square.get(seg, seg),
                     "per_expert": [len(m) for m in expert_marks],
                     "ref": len(marks), "dropped": len(cl) - len(keep),
                     "within": within})

    # ---------------------------------------------------------------- report
    print("square   each expert found   reference   dropped   their own repeatability")
    for r in rows:
        w = ", ".join("--" if np.isnan(x) else f"{x:.2f}" for x in r["within"])
        print(f"  {r['square']:<7} {str(r['per_expert']):<18} {r['ref']:<11} "
              f"{r['dropped']:<9} {w}")

    total_ref = sum(len(v) for v in ref.values())
    print(f"\nreference: {total_ref} nuclei over {len(segs)} squares")
    if split_labels:
        print(f"  {split_labels} of them are labelled 'unsure': the experts located the")
        print(f"  nucleus but split on live vs dead. Those are excluded from the label")
        print(f"  score -- participants are not marked on calls the experts could not make.")

    print("\n=== each expert against the consensus they helped build ===")
    print("this is the most favourable test there is, so it is the ceiling\n")
    print("expert                    location F1   count acc   label agree")
    ceil_loc, ceil_cnt = [], []
    for disp in names:
        f1s, cnts, labs = [], [], []
        for seg in segs:
            radius = args.match_um / umpp.get(seg_field.get(seg, 0), 1.0)
            mine = per_expert_marks[disp].get(seg, [])
            them = [m for m in ref[seg]]
            f1s.append(f1_between(mine, them, radius))
            cnts.append(1 - abs(len(mine) - len(them)) / max(len(them), 1)
                        if them else (1.0 if not mine else 0.0))
            scoreable = [m for m in them if not m.get("label_split")]
            la, n = label_agreement(mine, scoreable, radius)
            if n:
                labs.append(la)
        loc = float(np.mean(f1s)); cnt = float(np.clip(np.mean(cnts), 0, 1))
        lab = float(np.mean(labs)) if labs else float("nan")
        ceil_loc.append(loc); ceil_cnt.append(cnt)
        print(f"  {disp:<24} {loc:.3f}         {cnt:.3f}       "
              f"{'--' if np.isnan(lab) else f'{lab:.3f}'}")

    if len(experts) > 1:
        print("\n=== experts against each other ===")
        for (i, a), (j, b) in combinations(list(enumerate(names)), 2):
            f1s = [f1_between(per_expert_marks[a].get(s, []),
                              per_expert_marks[b].get(s, []),
                              args.match_um / umpp.get(seg_field.get(s, 0), 1.0))
                   for s in segs]
            print(f"  {a} vs {b}: location F1 {np.mean(f1s):.3f}")

    worst_loc, worst_cnt = min(ceil_loc), min(ceil_cnt)
    rec_loc = np.floor(worst_loc * 20) / 20      # round down to a 0.05 step
    rec_cnt = np.floor(worst_cnt * 20) / 20
    print("\n=== the pass mark this data supports ===")
    print(f"  weakest expert: location {worst_loc:.3f}, number {worst_cnt:.3f}")
    print(f"  suggested gate: --gate-location {rec_loc:.2f} --gate-count {rec_cnt:.2f}")
    if rec_loc < 0.90:
        print(f"\n  A 0.90 location gate is NOT supported: your own experts only reach")
        print(f"  {worst_loc:.2f} against a consensus they helped build. Setting 0.90")
        print(f"  would fail participants for not beating the people defining the answer.")
    else:
        print(f"\n  A 0.90 gate is supported by this data.")
    n_obj = total_ref
    if n_obj < 80:
        print(f"\n  Note: the gate is judged on only {n_obj} nuclei, so a participant near")
        print(f"  the line passes or fails partly on chance. More training squares would")
        print(f"  tighten it -- around 80-100 nuclei is a more stable basis.")

    out = {"schema": "sclera-count-v1", "rater": "consensus of " + ", ".join(names),
           "mode": experts[0][2].get("mode"), "study": experts[0][2].get("study"),
           "built_by": "make_reference.py",
           "experts": names, "n_experts": len(experts),
           "own_pairwise_f1": round(float(np.mean(ceil_loc)), 4),
           "weakest_expert_location_f1": round(worst_loc, 4),
           "weakest_expert_count_acc": round(worst_cnt, 4),
           "suggested_gate": {"location": rec_loc, "count": rec_cnt},
           "label_split_count": split_labels,
           "order": sorted(ref),
           "seg": {f"{k}#0": {"marks": [{kk: vv for kk, vv in m.items()
                                         if kk != "label_split"} | {"t": ""}
                                        for m in v],
                              "undone": [], "empty": not v, "note": "",
                              "bri": 100, "con": 100, "seconds": 0, "done": True}
                   for k, v in ref.items()}}
    args.out.write_text(json.dumps(out, indent=1))
    print(f"\nwrote {args.out}")
    print(f"  build with:  --training-from {args.out} "
          f"--gate-location {rec_loc:.2f} --gate-count {rec_cnt:.2f}")


if __name__ == "__main__":
    sys.exit(main())
