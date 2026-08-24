#!/usr/bin/env python3
"""
depth_profile.py -- how deep into the tissue is each stack still countable?

    /usr/bin/python3 tools/depth_profile.py --z-levels 3,5,7,9,11,13

Confocal signal falls off with depth, and it does not fall off at the same rate in
every stack. Handing counters a square from below that point is asking them to
count noise -- and any "depth effect" you then measure is partly just that.

Read the p99 column. Below about 40 (of 255) on the counting channel the discrete
nuclei have gone, whatever the peak finder claims. The estimated-nuclei column is deliberately shown next to
it as a warning: a peak finder keeps confidently reporting hundreds of objects in
fields that are essentially black, which is precisely the failure this table is
meant to catch.
"""
import argparse, sys
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import build_segments as B   # noqa: E402

# Calibrated by rendering the tiles and looking at them, not derived. A field at
# p99 = 31 (006/1/Image 5, z13, 68 um) still passed a threshold of 20 and was
# visibly black -- discrete nuclei had gone. 40 is where they were still there.
DIM_P99 = 40.0


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", default="")
    p.add_argument("--stacks", default="")
    p.add_argument("--z-levels", default="3,5,7,9,11,13,15,17")
    p.add_argument("--scheme", default="hoechst", choices=sorted(B.SCHEMES))
    p.add_argument("--dim-p99", type=float, default=DIM_P99)
    args = p.parse_args()
    if args.config:
        B.apply_config(args.config)

    stacks = ([{"specimen": s.split("/", 1)[0].strip(), "image": s.split("/", 1)[1].strip()}
               for s in args.stacks.split(",") if s.strip()] or B.DEFAULT_STACKS)
    zs = sorted({int(z) for z in args.z_levels.split(",") if z.strip()})
    ch = B.CH[B.SCHEMES[args.scheme]["nuclei"] or B.SCHEMES[args.scheme]["live"]]

    print("stack                    z   depth      p99   bright%   est.objects")
    usable = {}
    for spec in stacks:
        try:
            zmap, reg = B.resolve_stack(spec["specimen"], spec["image"])
        except SystemExit as e:
            print(f"  ! {e}"); continue
        deepest = None
        for z in zs:
            f = zmap.get(z)
            if f is None:
                continue
            if f.stat().st_blocks == 0:
                print(f"  {spec['specimen']}/{reg}/{spec['image']:<12} {z:>2}   "
                      f"not downloaded")
                continue
            a = np.asarray(Image.open(f).convert("RGB"), dtype=np.float32)[..., ch]
            p99 = float(np.percentile(a, 99))
            flat = a - ndi.gaussian_filter(a, 40)
            sm = ndi.gaussian_filter(flat, 1.5)
            med = float(np.median(sm)); mad = float(np.median(np.abs(sm - med))) or 1e-6
            n = int(((sm == ndi.maximum_filter(sm, size=5)) &
                     (sm > med + 3.5 * 1.4826 * mad)).sum())
            dim = p99 < args.dim_p99
            if not dim:
                deepest = z
            print(f"  {spec['specimen']}/{reg}/{spec['image']:<12} {z:>2}  "
                  f"{z*B.Z_UM:5.1f}um {p99:>7.0f}  {100*float((a>20).mean()):>6.2f}   "
                  f"{n:>7}{'   <- nothing left to count' if dim else ''}")
        usable[f"{spec['specimen']}/{spec['image']}"] = deepest
        print()

    print("deepest slice still worth counting:")
    for k, v in usable.items():
        print(f"  {k:<24} " + (f"z{v:02d}  ({v*B.Z_UM:.0f} um)" if v is not None
                               else "none of the slices checked"))
    got = [v for v in usable.values() if v is not None]
    if got:
        print(f"\nA depth ladder should sit inside 0-{min(got)*B.Z_UM:.0f} um if every "
              f"stack must\ncontribute at every depth, or be set per stack otherwise.")


if __name__ == "__main__":
    sys.exit(main())
