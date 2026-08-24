#!/usr/bin/env python3
"""
z_trace.py -- link the same nucleus across z-slices, so it is counted once.

    /usr/bin/python3 tools/z_trace.py --stacks "006/Image 5" --z-range 3,11

Why
---
A nucleus is a three-dimensional object photographed in slices 5.263 um apart.
Counting each slice and adding the totals counts the same nucleus several times.
Measured on 006/1/Image 5 over nine consecutive slices: 2,375 per-slice
detections correspond to **787 distinct nuclei — a 3.0x over-count**.

That alone would only inflate the density. The reason it also corrupts viability
is that the error is **not symmetric**:

    dead-positive nuclei   mean axial extent 3.82 slices (20.1 um)
    EthD-negative nuclei   mean axial extent 2.51 slices (13.2 um)   -> 1.52x

Dead nuclei carry signal in two channels, so they stay above threshold across
more slices and are counted more often. Summing slices therefore inflates the
dead fraction from **38.9% to 49.2% — a 10.3 point error** in the headline number,
in the same direction as, and compounding, the depth-sensitivity artifact.

Method
------
Detect per slice, then link, rather than thresholding the volume in 3D. A single
3D threshold cannot work here because signal decays steeply with depth (see
tools/depth_profile.py), so one level is simultaneously too high at the top of
the stack and too low at the bottom.

  1. per slice: flatten background, smooth at nucleus scale, keep local maxima
     above the slice's own noise floor
  2. link a detection to the nearest unclaimed detection in the next slice within
     `--link-um` laterally, at most one per slice
  3. tolerate `--max-gap` slices where a nucleus drops below threshold and
     reappears, which is common near the detection limit
  4. a chain is one nucleus: position = centroid, depth = mid-slice, axial extent
     = chain length, dead = EthD-positive on any slice of the chain

`--link-um` defaults to 5 um, the minimum cell diameter in config.yaml: two
detections further apart than one nucleus width are not the same nucleus.
"""

import argparse, sys
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import build_segments as B   # noqa: E402


def detect(a, lo, hi, noise_k, min_frac):
    sm = ndi.gaussian_filter(a - ndi.gaussian_filter(a, 40), 1.5)
    med = float(np.median(sm)); mad = float(np.median(np.abs(sm - med))) or 1e-6
    pk = ((sm == ndi.maximum_filter(sm, size=5))
          & (sm > med + noise_k * 1.4826 * mad)
          & (a > lo + min_frac * (hi - lo)))
    ys, xs = np.nonzero(pk)
    return list(zip(xs.astype(float), ys.astype(float)))


def link(per_slice, radius, max_gap):
    """per_slice: {z: [(x, y), ...]} -> list of chains [(z, x, y), ...]"""
    chains, active = [], []
    for z in sorted(per_slice):
        pts, used, nxt = per_slice[z], set(), []
        for ch in active:
            lz, cx, cy = ch[-1]
            if z - lz > max_gap + 1:            # lost for too long
                chains.append(ch); continue
            best, bd = None, radius
            for i, (x, y) in enumerate(pts):
                if i in used:
                    continue
                d = float(np.hypot(x - cx, y - cy))
                if d <= bd:
                    best, bd = i, d
            if best is None:
                nxt.append(ch)                  # keep alive across the gap
            else:
                used.add(best); ch.append((z,) + pts[best]); nxt.append(ch)
        for i, p in enumerate(pts):
            if i not in used:
                nxt.append([(z,) + p])
        active = nxt
    return chains + active


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--stacks", default="006/Image 5")
    p.add_argument("--z-range", default="3,11", help="first,last consecutive slice")
    p.add_argument("--link-um", type=float, default=5.0)
    p.add_argument("--max-gap", type=int, default=1,
                   help="slices a nucleus may drop below threshold and still link")
    p.add_argument("--noise-k", type=float, default=3.5)
    p.add_argument("--min-frac", type=float, default=0.25)
    p.add_argument("--scheme", default="hoechst", choices=sorted(B.SCHEMES))
    args = p.parse_args()

    z0, z1 = (int(v) for v in args.z_range.split(","))
    sc = B.SCHEMES[args.scheme]
    nuc_ch, dead_ch = B.CH[sc["nuclei"] or sc["live"]], B.CH[sc["dead"]]

    for spec in [{"specimen": s.split("/", 1)[0].strip(), "image": s.split("/", 1)[1].strip()}
                 for s in args.stacks.split(",") if s.strip()]:
        zmap, reg = B.resolve_stack(spec["specimen"], spec["image"])
        zs = [z for z in range(z0, z1 + 1)
              if z in zmap and zmap[z].stat().st_blocks > 0]
        if len(zs) < 2:
            print(f"  {spec['specimen']}/{spec['image']}: need consecutive slices "
                  f"downloaded (tools/fetch_sources.py --z-levels {z0}..{z1})")
            continue

        vols = {z: np.asarray(Image.open(zmap[z]).convert("RGB"), dtype=np.float32)
                for z in zs}
        pool = np.concatenate([v[..., nuc_ch].ravel() for v in vols.values()])
        lo, hi = float(np.percentile(pool, 1)), float(np.percentile(pool, 99.7))
        dthr = float(np.percentile(
            np.concatenate([v[..., dead_ch].ravel() for v in vols.values()]), 99.0))

        per = {z: detect(vols[z][..., nuc_ch], lo, hi, args.noise_k, args.min_frac)
               for z in zs}
        radius = args.link_um / (B.FIELD_WIDTH_UM / vols[zs[0]].shape[1])
        chains = link(per, radius, args.max_gap)

        spans = np.array([len(c) for c in chains])
        naive = sum(len(per[z]) for z in zs)
        dead = np.array([len(c) for c in chains
                         if max(vols[z][int(y), int(x), dead_ch]
                                for z, x, y in c) > dthr])
        live = np.array([len(c) for c in chains
                         if max(vols[z][int(y), int(x), dead_ch]
                                for z, x, y in c) <= dthr])

        print(f"\n{spec['specimen']}/{reg}/{spec['image']}  "
              f"z{zs[0]:02d}-z{zs[-1]:02d} ({len(zs)} slices)")
        print(f"  per-slice detections {naive}   distinct nuclei {len(chains)}   "
              f"over-count {naive/max(len(chains),1):.2f}x")
        print(f"  axial extent: median {np.median(spans):.0f} slices "
              f"({np.median(spans)*B.Z_UM:.1f} um), max {spans.max()} "
              f"({spans.max()*B.Z_UM:.1f} um)")
        if len(dead) and len(live):
            print(f"  dead span {dead.mean():.2f} slices vs live {live.mean():.2f} "
                  f"-> {dead.mean()/live.mean():.2f}x")
            tf = 100*len(dead)/(len(dead)+len(live))
            af = 100*dead.sum()/(dead.sum()+live.sum())
            print(f"  dead fraction: linked {tf:.1f}%  naive slice-sum {af:.1f}%  "
                  f"({af-tf:+.1f} points)")

        print("\n  independent-depth spacing: two slices sample different nuclei only "
              "if further\n  apart than the axial extent.")
        for k in range(1, min(7, spans.max() + 1)):
            print(f"    {k*B.Z_UM:5.1f} um apart -> {100*(spans>=k+1).mean():5.1f}% "
                  f"of nuclei still appear in both")


if __name__ == "__main__":
    sys.exit(main())
