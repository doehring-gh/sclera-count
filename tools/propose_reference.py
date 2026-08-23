#!/usr/bin/env python3
"""
propose_reference.py -- draft a set of marks on the reference squares, so making
the reference is a review job rather than a from-scratch clicking job.

    /usr/bin/python3 tools/propose_reference.py --manifest docs/manifest.json

READ THIS BEFORE USING IT
-------------------------
What comes out is a PROPOSAL, not the reference. You must open it in the app and
correct it, and your corrected version is what becomes the reference.

The reason is not politeness. The whole point of the counting study is to find
out how manual counts compare with the automated pipeline. If participants are
trained to match a detector, and then you measure how well they agree with a
detector, the answer is guaranteed in advance and means nothing. The reference
has to be a human judgement; this only saves you the clicking.

Bafti et al. (2021) is the precedent: assistive tools cut annotation cost while
preserving or improving quality -- when a person still adjudicates.

How the proposal is made
------------------------
Deliberately simple and separate from the production detector, so it cannot
quietly become the thing it is meant to be checked against:

  1. flatten the tile's large-scale background
  2. blur at roughly the radius of a nucleus
  3. keep local maxima at least one nucleus-width apart
  4. keep those above a threshold set from the tile's own noise
  5. call each one dead or live from the EthD-1 tile at that point

Every parameter is printed and stored, and the diameters come from config.yaml.
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

REPO = Path(__file__).resolve().parent.parent.parent
MIN_UM, MAX_UM = 5.0, 30.0          # cell diameters, from config.yaml


def load_gray(path):
    return np.asarray(Image.open(path).convert("L"), dtype=np.float32)


def propose(nuc, dead, um_per_px, k_noise, dead_k):
    """Return [(x, y, label, score)] for one tile."""
    r_px = max(1.5, (MIN_UM / 2.0) / um_per_px)        # nucleus radius in pixels
    sep = max(3, int(round(MIN_UM / um_per_px)))        # min separation
    bg_sigma = max(4.0, (MAX_UM / um_per_px))

    flat = nuc - ndi.gaussian_filter(nuc, bg_sigma)     # kill the slow background
    sm = ndi.gaussian_filter(flat, r_px * 0.6)

    # noise scale from the image itself: MAD is not dragged up by the bright spots
    med = float(np.median(sm))
    mad = float(np.median(np.abs(sm - med))) or 1e-6
    thr = med + k_noise * 1.4826 * mad

    mx = ndi.maximum_filter(sm, size=sep)
    peaks = (sm == mx) & (sm > thr)
    ys, xs = np.nonzero(peaks)

    out = []
    for y, x in zip(ys, xs):
        d = float(dead[y, x]) if dead is not None else 0.0
        out.append((float(x), float(y), d, float(sm[y, x])))
    if not out:
        return []

    # dead if the EthD-1 tile is clearly bright there, judged against its own spread
    dv = np.array([o[2] for o in out])
    dmed, dmad = float(np.median(dv)), float(np.median(np.abs(dv - np.median(dv)))) or 1e-6
    dthr = dmed + dead_k * 1.4826 * dmad
    return [(x, y, "dead" if d > dthr else "live", s) for x, y, d, s in out]


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--manifest", type=Path, default=Path("docs/manifest.json"))
    p.add_argument("--squares", default="",
                   help="restrict to these segment ids or square names, e.g. F5,E1")
    p.add_argument("--noise-k", type=float, default=3.5,
                   help="how far above the tile's own noise a peak must sit")
    p.add_argument("--dead-k", type=float, default=1.5,
                   help="how far above the EthD-1 median counts as dead")
    p.add_argument("--out", type=Path, default=Path("reference_proposal.json"))
    p.add_argument("--expect", default="",
                   help="known totals to check against, e.g. 'F5=11,E1=12,F4=6'")
    args = p.parse_args()

    man = json.loads(args.manifest.read_text())
    root = args.manifest.parent
    um = {f["field"]: f.get("um_per_px", 1.0) for f in man.get("fields", [])}
    want = {w.strip().upper() for w in args.squares.split(",") if w.strip()}
    expect = {}
    for kv in args.expect.split(","):
        if "=" in kv:
            k, v = kv.split("=", 1)
            expect[k.strip().upper()] = int(v)

    segs = man["segments"]
    if want:
        segs = [s for s in segs if s["id"].upper() in want or s["square"].upper() in want]
    if not segs:
        sys.exit("no matching squares in that manifest")

    print(f"proposing on {len(segs)} square(s)")
    print(f"  cell diameter {MIN_UM}-{MAX_UM} um (config.yaml), "
          f"noise-k {args.noise_k}, dead-k {args.dead_k}\n")

    order, seg_out, rows = [], {}, []
    for i, s in enumerate(segs):
        upp = um.get(s["field"], 1.0) / s.get("upscale", 1)
        nuc_key = "nuclei" if "nuclei" in s["layers"] else "live"
        nuc = load_gray(root / s["layers"][nuc_key])
        dead = load_gray(root / s["layers"]["dead"]) if "dead" in s["layers"] else None

        pts = propose(nuc, dead, upp, args.noise_k, args.dead_k)
        x0, y0, x1, y1 = s["count_box"]
        pts = [q for q in pts if x0 <= q[0] <= x1 and y0 <= q[1] <= y1]

        marks = [{"x": round(x, 1), "y": round(y, 1), "label": lab, "t": ""}
                 for x, y, lab, _ in pts]
        order.append(s["id"])
        seg_out[f"{s['id']}#{i}"] = {"marks": marks, "undone": [], "empty": not marks,
                                     "note": "", "bri": 100, "con": 100,
                                     "seconds": 0, "done": True}
        nd = sum(1 for m in marks if m["label"] == "dead")
        rows.append((s["square"], len(marks), nd,
                     expect.get(s["square"].upper())))

    print("square   proposed  dead  known total  vs known")
    tot_p = tot_e = 0
    for sq, n, nd, exp in rows:
        if exp is None:
            print(f"  {sq:<7} {n:<9} {nd:<5} {'-':<12} -")
        else:
            tot_p += n; tot_e += exp
            print(f"  {sq:<7} {n:<9} {nd:<5} {exp:<12} {n-exp:+d}")
    if tot_e:
        print(f"\n  proposed {tot_p} vs known {tot_e} "
              f"({100*tot_p/tot_e:.0f}% of the known total)")
        if abs(tot_p - tot_e) / tot_e > 0.35:
            print("  That is a long way off. Adjust --noise-k (higher finds fewer)")
            print("  before you start reviewing, or you will spend the whole time")
            print("  correcting the detector instead of reading the images.")

    out = {"schema": "sclera-count-v1", "rater": "PROPOSAL — must be reviewed",
           "mode": "livedead", "study": man.get("study"),
           "built_by": "propose_reference.py",
           "params": {"noise_k": args.noise_k, "dead_k": args.dead_k,
                      "min_um": MIN_UM, "max_um": MAX_UM},
           "order": order, "seg": seg_out}
    args.out.write_text(json.dumps(out, indent=1))
    print(f"\nwrote {args.out}")
    print("\n  This is a DRAFT. Load it into the app, correct it, and export your")
    print("  corrected version -- that is what becomes the reference:")
    print(f"    /usr/bin/python3 build_segments.py ... --prefill-from {args.out}")


if __name__ == "__main__":
    sys.exit(main())
