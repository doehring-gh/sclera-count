#!/usr/bin/env python3
"""
ramp_check.py -- did Auto Z Brightness Correction buy countability, or brightness?

    /usr/bin/python3 tools/ramp_check.py --simulate --stacks "006/Image 5"
    /usr/bin/python3 tools/ramp_check.py --pair "007/Image 1" "007/Image 2"
    /usr/bin/python3 tools/ramp_check.py --self-test

Background (FINDINGS 4c)
-----------------------
Torsten Bossing's advice is to ramp PMT gain with depth so deep slices come out
about as bright as the surface. Gain amplifies noise along with signal, so a slice
can be made brighter without being made more countable -- and our failure mode
(4) is that dim live nuclei drop below detection while brighter dead ones survive,
which biases viability rather than merely degrading it. So "is it brighter" is the
wrong question and "is it countable" is the right one.

Why --simulate is a NEGATIVE control, not a measurement
-------------------------------------------------------
The obvious idea is to multiply an existing slice by a gain factor and see whether
more nuclei appear. **This cannot work, and this mode exists to show why.**

Detection thresholds at `median + k*sigma` of each slice's own background. Under a
multiplication by g the peak, the median and sigma all scale by g, so the
inequality is unchanged and the detected set is *identical by construction*. Any
"result" from this is an artifact of arithmetic.

Worse, it cannot even be fixed: real gain is applied at the PMT, **before** the
analogue-to-digital converter. Our stacks are already 8-bit. Multiplying integers
cannot recover what quantisation and read noise discarded.

**Conclusion: nothing computable from the existing images predicts whether the
ramp will work. Only a paired corrected/uncorrected stack of the same field can
answer it.** That is what --pair is for, and why the control stack is not
good practice but the only available evidence.

What --pair actually tests
--------------------------
Given the same field imaged twice -- once with the correction on, once off -- the
question is whether extra detections in the corrected stack are *real nuclei that
were previously too dim*, or *amplified noise*. Brightness cannot distinguish
these. Axial persistence can:

    a real nucleus is ~16 um tall and so appears on ~3 consecutive slices
    an amplified noise maximum does not reappear at the same (x, y) on the next slice

So the discriminator is the fraction of detections that link into a chain spanning
two or more slices, using the same linking as tools/z_trace.py:

    detections up, persistence holds     -> the ramp recovered real nuclei
    detections up, persistence collapses -> the ramp amplified noise (cosmetic)
    detections flat                      -> the ramp changed nothing countable

Read the persistence column, not the count column.
"""
import argparse, sys
from pathlib import Path
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import build_segments as B          # noqa: E402
from z_trace import detect, link    # noqa: E402  -- same detector, deliberately


def _spec(s):
    a, b = s.split("/", 1)
    return {"specimen": a.strip(), "image": b.strip()}


def _slices(spec, zs, ch):
    """{z: single-channel float array} for the slices that are actually present."""
    zmap, reg = B.resolve_stack(spec["specimen"], spec["image"])
    out = {}
    for z in zs:
        f = zmap.get(z)
        if f is None or f.stat().st_blocks == 0:
            continue
        out[z] = np.asarray(Image.open(f).convert("RGB"), dtype=np.float32)[..., ch]
    return out, reg


def _profile(vols, args, radius_px):
    """detections per slice, and what fraction of them persist axially."""
    per = {}
    for z, a in vols.items():
        lo, hi = float(a.min()), float(a.max()) or 1.0
        per[z] = detect(a, lo, hi, args.noise_k, args.min_frac)
    chains = link(per, radius_px, args.max_gap)
    # a detection persists if its chain touches more than one slice
    persistent = {z: 0 for z in per}
    for ch in chains:
        if len(ch) >= 2:
            for (z, _x, _y) in ch:
                if z in persistent:
                    persistent[z] += 1
    return per, persistent


def _table(title, vols, args, radius_px):
    per, persistent = _profile(vols, args, radius_px)
    print(f"  {title}")
    print(f"    {'z':>3}{'depth':>9}{'p99':>7}{'detected':>10}{'persist':>9}{'%':>7}")
    rows = {}
    for z in sorted(per):
        n = len(per[z]); k = persistent[z]
        pc = 100.0 * k / n if n else 0.0
        rows[z] = (n, k, pc)
        print(f"    {z:>3}{z*B.Z_UM:>8.1f}u{np.percentile(vols[z], 99):>7.0f}"
              f"{n:>10}{k:>9}{pc:>6.1f}%")
    return rows


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", default="")
    p.add_argument("--simulate", action="store_true",
                   help="negative control: show that synthetic gain changes nothing")
    p.add_argument("--pair", nargs=2, metavar=("CORRECTED", "UNCORRECTED"),
                   help='e.g. --pair "007/Image 1" "007/Image 2"')
    p.add_argument("--self-test", action="store_true",
                   help="check the pair plumbing using a synthetically dimmed copy")
    p.add_argument("--stacks", default="006/Image 5")
    p.add_argument("--z-range", default="3,13")
    p.add_argument("--gains", default="1,2,4,8")
    p.add_argument("--link-um", type=float, default=5.0)
    p.add_argument("--max-gap", type=int, default=1)
    p.add_argument("--noise-k", type=float, default=3.5)
    p.add_argument("--min-frac", type=float, default=0.25)
    p.add_argument("--atten", type=float, default=4.0,
                   help="self-test: how much dimmer the 'uncorrected' stack is")
    p.add_argument("--empty-stack", default="003/Image 5",
                   help="self-test negative control: a stack whose deep slices "
                        "have no countable signal left")
    p.add_argument("--empty-range", default="13,19")
    p.add_argument("--read-noise", type=float, default=2.0,
                   help="self-test: read noise in grey levels, added AFTER "
                        "attenuation -- this is what a gain ramp fights")
    p.add_argument("--scheme", default="hoechst", choices=sorted(B.SCHEMES))
    args = p.parse_args()
    if args.config:
        B.apply_config(args.config)

    sc = B.SCHEMES[args.scheme]
    ch = B.CH[sc["nuclei"] or sc["live"]]
    z0, z1 = (int(v) for v in args.z_range.split(","))
    zs = list(range(z0, z1 + 1))

    def _radius(vols):
        """um -> px, same conversion as tools/z_trace.py"""
        w = next(iter(vols.values())).shape[1]
        return args.link_um / (B.FIELD_WIDTH_UM / w)

    if args.simulate:
        spec = _spec(args.stacks.split(",")[0])
        vols, reg = _slices(spec, zs, ch)
        if not vols:
            raise SystemExit("no slices downloaded for that stack")
        print(f"\nNEGATIVE CONTROL -- {spec['specimen']}/{reg}/{spec['image']}")
        print("Synthetic gain on already-digitised images, run through two detectors.")
        print("Neither column is evidence about the real ramp. See the note below.\n")
        base = {z: a.copy() for z, a in vols.items()}
        print(f"    {'gain':>8}{'noise-referenced':>20}{'production':>14}{'saturated':>12}")
        for g in [float(v) for v in args.gains.split(",")]:
            scaled = {z: np.clip(a * g, 0, 255) for z, a in base.items()}
            pure = sum(len(detect(a, float(a.min()), float(a.max()) or 1.0,
                                  args.noise_k, 0.0)) for a in scaled.values())
            prod = sum(len(detect(a, float(a.min()), float(a.max()) or 1.0,
                                  args.noise_k, args.min_frac)) for a in scaled.values())
            clip = 100.0 * np.mean([float((a >= 255).mean()) for a in scaled.values()])
            print(f"    x{g:<7.2f}{pure:>20}{prod:>14}{clip:>11.3f}%")
        print("""
  Two different ways of learning nothing:

  noise-referenced (min-frac 0) -- thresholds at median + k*sigma of the slice's
    own background. Multiplying scales peak, median and sigma together, so the
    inequality is unchanged and the detected set is invariant BY CONSTRUCTION.
    Near-flat here; residual drift is the 255 ceiling clipping bright nuclei.

  production (min-frac %.2f) -- tools/z_trace.py adds an absolute floor at
    lo + min_frac*(hi-lo). These stacks ALREADY contain saturated pixels, so hi is
    pinned at 255 and the floor stops scaling with the image. Multiplying then
    lifts pixels over a FIXED bar and the count climbs -- here it more than
    doubles, at gains far too small to be recovering anything. That rise is an
    artifact of the floor, not nuclei.

  The second is the dangerous one: it looks like a result. Anyone simulating a
  ramp with the production detector would report that gain recovers twice the
  nuclei, and be entirely wrong.

  Both are silent on the real question, because real gain is applied at the PMT
  BEFORE digitisation. No arithmetic on 8-bit data recovers what the ADC
  discarded.""" % args.min_frac)
        print("\n  Read this as: no post-hoc arithmetic can answer the question.")
        print("  Only --pair on a real corrected/uncorrected pair can. See FINDINGS 4c.")
        return 0

    if args.self_test:
        spec = _spec(args.stacks.split(",")[0])
        vols, reg = _slices(spec, zs, ch)
        if not vols:
            raise SystemExit("no slices downloaded for that stack")
        print(f"\nSELF-TEST -- plumbing only, on {spec['specimen']}/{reg}/{spec['image']}")
        print("Stands in for a real pair. 'Uncorrected' is modelled as the same")
        print("signal attenuated, PLUS read noise, then re-quantised to 8-bit:")
        print("")
        print("    uncorrected = floor( a / atten  +  N(0, read_noise) )")
        print("")
        print("Attenuation alone would prove nothing -- the detector is scale-")
        print("invariant, so dividing by a constant leaves the detected set almost")
        print("untouched (that is the finding in FINDINGS 4c, not a bug). Read noise")
        print("is what a PMT gain ramp actually fights: gain lifts signal above the")
        print("noise floor added downstream of it. So the noise term is the whole")
        print("point of the model.")
        print("")
        print("This validates the plumbing and the persistence discriminator. It is")
        print("a MODEL, not evidence about the real ramp -- only --pair on Louise's")
        print("corrected/uncorrected pair can provide that.\n")
        rng = np.random.default_rng(0)          # fixed: the test must not drift
        dim = {z: np.clip(np.floor(a / args.atten + rng.normal(0, args.read_noise, a.shape)),
                          0, 255)
               for z, a in vols.items()}
        rp = _radius(vols)
        a_rows = _table("as acquired            (stands in for CORRECTED)",
                        vols, args, rp)
        print()
        b_rows = _table(f"/{args.atten:g} + {args.read_noise:g} DN noise  "
                        f"(stands in for UNCORRECTED)", dim, args, rp)
        ga = sum(v[0] for v in a_rows.values()); gb = sum(v[0] for v in b_rows.values())
        pa = np.mean([v[2] for v in a_rows.values()])
        pb = np.mean([v[2] for v in b_rows.values()])
        print(f"\n  detections  {gb} -> {ga}   ({ga - gb:+d} recovered)")
        print(f"  persistence {pb:.1f}% -> {pa:.1f}%")
        print("\n  Expected: detections rise AND persistence holds or improves --")
        print("  the signature this tool calls REAL.")

        # A discriminator that only ever says REAL is worthless. Check it also
        # fires the other way, on slices where the signal is genuinely gone:
        # amplifying those must NOT look like recovery.
        print("\n  --- negative control: can it still say COSMETIC? ---")
        print(f"  Amplifying {args.empty_stack}, where signal is already gone.")
        print("  Detections may climb; persistence must not.\n")
        try:
            esp = _spec(args.empty_stack)
            ez = [int(v) for v in args.empty_range.split(",")]
            ev, ereg = _slices(esp, list(range(ez[0], ez[1] + 1)), ch)
        except SystemExit as e:
            print(f"    skipped: {e}"); return 0
        if len(ev) < 3:
            print("    skipped: need at least 3 downloaded slices "
                  f"(have {len(ev)}); tools/fetch_sources.py")
            return 0
        erp = _radius(ev)
        for g in (1.0, 4.0, 16.0):
            sv = {z: np.clip(a * g, 0, 255) for z, a in ev.items()}
            per, keep = _profile(sv, args, erp)
            n = sum(len(v) for v in per.values()); k = sum(keep.values())
            pc = 100.0 * k / n if n else 0.0
            print(f"    gain x{g:<5.0f} p99 {np.percentile(sv[min(sv)], 99):>5.0f}  "
                  f"detections {n:>5}   persistence {pc:>5.1f}%")
        print("\n  Persistence staying LOW here while it is high above is what makes")
        print("  the discriminator usable: real nuclei persist across slices,")
        print("  amplified noise does not. If both come out alike, do not trust a")
        print("  --pair verdict.")
        return 0

    if not args.pair:
        raise SystemExit("choose --simulate, --self-test, or --pair CORRECTED UNCORRECTED")

    cs, us = _spec(args.pair[0]), _spec(args.pair[1])
    cv, creg = _slices(cs, zs, ch)
    uv, ureg = _slices(us, zs, ch)
    shared = sorted(set(cv) & set(uv))
    if not shared:
        raise SystemExit("the two stacks share no downloaded slices")
    cv = {z: cv[z] for z in shared}; uv = {z: uv[z] for z in shared}

    print(f"\nPAIRED COMPARISON  (same field, correction on vs off)")
    print(f"  corrected   {cs['specimen']}/{creg}/{cs['image']}")
    print(f"  uncorrected {us['specimen']}/{ureg}/{us['image']}\n")
    rp = _radius(cv)
    c_rows = _table("CORRECTED", cv, args, rp)
    print()
    u_rows = _table("UNCORRECTED", uv, args, rp)

    print("\n  verdict per slice -- read persistence, not count")
    print(f"    {'z':>3}{'depth':>9}{'det u->c':>12}{'persist% u->c':>18}  reading")
    for z in shared:
        cn, _ck, cp = c_rows[z]; un, _uk, up = u_rows[z]
        gain_n = cn - un
        if abs(gain_n) <= max(3, 0.05 * max(un, 1)):
            reading = "no countable change"
        elif gain_n > 0 and cp >= up - 5:
            reading = "REAL -- recovered nuclei"
        elif gain_n > 0:
            reading = "COSMETIC -- noise amplified"
        else:
            reading = "fewer detections (check saturation)"
        print(f"    {z:>3}{z*B.Z_UM:>8.1f}u{un:>6} ->{cn:>4}"
              f"{up:>8.1f}% ->{cp:>6.1f}%  {reading}")
    print("\n  'REAL' means extra detections persist across slices as nuclei do.")
    print("  Persistence collapsing while counts rise is the signature of gain")
    print("  turning noise into plausible nuclei -- the failure this tool exists")
    print("  to catch. Confirm any 'REAL' verdict by eye before relying on it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
