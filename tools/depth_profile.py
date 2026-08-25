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

IMPORTANT -- p99 is invalid on gain-ramped stacks (FINDINGS 4c). Auto Z Brightness
Correction raises gain with depth specifically to hold brightness near the surface
value, so every slice passes a brightness test by construction and the test stops
discriminating. On ramped data read `cnr` instead, which is a contrast measured in
units of the background noise and so is not restored by amplification. Pass
--ramped to drop the p99 verdict and judge on cnr alone.
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

# Contrast of a detected nucleus over local background, in units of background
# noise. Unlike p99 this survives a gain ramp: multiplying an image scales the
# peak, the background and the noise together, so the ratio is unchanged.
#
# NOT independently derived -- transferred from the eyeballed DIM_P99 boundary
# above, and it does not separate those two groups cleanly (worst slice above the
# p99 line scores 8.4, best slice below it scores 9.8). Treat a value near 9 as
# "look at the tile before trusting it", not as a verdict.
DIM_CNR = 9.0

# One grey level. In 8-bit data the background MAD of a very dark slice falls
# below the quantisation step, which would make a black field score an
# impressively high contrast ratio for no reason. Floor the denominator.
QUANT_DN = 1.0


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", default="")
    p.add_argument("--stacks", default="")
    p.add_argument("--z-levels", default="3,5,7,9,11,13,15,17")
    p.add_argument("--scheme", default="hoechst", choices=sorted(B.SCHEMES))
    p.add_argument("--dim-p99", type=float, default=DIM_P99)
    p.add_argument("--dim-cnr", type=float, default=DIM_CNR)
    p.add_argument("--ramped", action="store_true",
                   help="stack was acquired with Auto Z Brightness Correction; "
                        "ignore the p99 brightness test and judge on cnr")
    args = p.parse_args()
    if args.config:
        B.apply_config(args.config)

    stacks = ([{"specimen": s.split("/", 1)[0].strip(), "image": s.split("/", 1)[1].strip()}
               for s in args.stacks.split(",") if s.strip()] or B.DEFAULT_STACKS)
    zs = sorted({int(z) for z in args.z_levels.split(",") if z.strip()})
    ch = B.CH[B.SCHEMES[args.scheme]["nuclei"] or B.SCHEMES[args.scheme]["live"]]

    print("stack                    z   depth      p99   contrast    cnr   est.objects")
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
            noise = 1.4826 * mad
            peaks = (sm == ndi.maximum_filter(sm, size=5)) & (sm > med + 3.5 * noise)
            n = int(peaks.sum())
            # Height of a typical detected peak over local background, in grey
            # levels, then in units of noise with the quantisation floor applied.
            contrast = float(np.median(sm[peaks] - med)) if n else 0.0
            cnr = contrast / max(noise, QUANT_DN)
            dim = (cnr < args.dim_cnr) if args.ramped else (p99 < args.dim_p99)
            if not dim:
                deepest = z
            print(f"  {spec['specimen']}/{reg}/{spec['image']:<12} {z:>2}  "
                  f"{z*B.Z_UM:5.1f}um {p99:>7.0f}  {contrast:>8.1f} {cnr:>6.1f}   "
                  f"{n:>7}{'   <- nothing left to count' if dim else ''}")
        usable[f"{spec['specimen']}/{spec['image']}"] = deepest
        print()

    print("judged on " + ("cnr (stack declared gain-ramped, p99 not meaningful)"
                          if args.ramped else "p99 brightness"))
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
