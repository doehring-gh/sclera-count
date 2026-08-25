# Reply to Torsten — his second answer

He answered both questions and added the 3D analysis point. This reply does three
things: concedes that one of my two questions was aimed at the wrong hazard, tells
him the one thing we found that he could not have known (that the ramp cannot be
validated from existing images), and engages properly with the ImageJ suggestion
rather than deflecting it a second time.

Short. He has given us what we need and does not need another essay.

---

**Subject:** Re: — that settles it, and one thing we found that you should know

Dear Torsten,

Thank you — that settles the acquisition, and Louise now has a written protocol
based on it.

**One of my two questions was aimed at the wrong thing, and your answer is better
than my request.** I asked whether both channels could share one gain schedule. On
reflection that was wrong: our dead/live call is not a red-to-blue intensity ratio,
it is presence or absence of EthD-1 at a nucleus found in Hoechst. What that needs
is each channel's *sensitivity* to be steady with depth — which is exactly what
aiming each channel at its own surface brightness gives, and a shared schedule
would not. So we will do it your way.

The hazard I should have asked about is the one your offset advice already covers:
gain lifts each channel's background as well as its signal, and if the EthD-1
background creeps up with depth then live nuclei acquire a faint apparent
EthD-1 signal and get miscalled as dead. That would recreate our artefact by a new
route and in the same direction, which would be an unpleasant way to find out. So
we will record the background level per channel per slice alongside the gain, not
just the gain.

**On whether the ramp buys countability — we tried to settle it in advance and
found that we cannot, which I think is worth passing on.** We attempted to simulate
a ramp on the existing stacks. It is structurally impossible: our detector
thresholds against each slice's own noise, so multiplying an image scales the peak,
the background and the noise together and the detected set does not change at all —
we got an identical object count from gain x1 to x8. Of course we did: real gain
happens at the PMT, before digitisation, and no arithmetic on an 8-bit image
recovers what the ADC has already thrown away.

Which means **the control stack is not a nice-to-have, it is the only evidence
available**. I had been treating it as good practice. It is actually the single
comparison that can distinguish "we made it brighter" from "we made it countable",
and I am glad you independently landed on it. It is now flagged in the protocol as
the item not to drop.

One consequence for us: our depth tool judged a slice countable by absolute
brightness, which a ramp is designed to hold constant — so on the new data it would
have passed every slice by construction and gone quietly blind. It now measures
contrast against the local background instead. Your advice broke our instrument in
a way we would probably not have noticed until the numbers looked suspiciously good.

**On 3D Analyse — you are right, and I gave you a poor answer last time.** For the
automated side it is the correct approach, and it is close to what we already do:
we detect per slice and link between slices rather than thresholding the volume,
because signal decay meant one threshold was too high at the top of the stack and
too low at the bottom. **But that objection is exactly what your gain ramp
removes.** If brightness is equalised with depth, a single 3D threshold becomes
defensible for the first time — your two suggestions fit together better than
either does on its own, and I had not seen that until I wrote it down.

Where it does not help is the human side: our counters work on 2D tiles, so if a
person is shown two depths they may meet the same nucleus twice whatever we do in
3D afterwards. But it gives us something better than the workaround we had. We were
choosing depth separations from the *median* height of a nucleus — a rule of thumb.
With 3D linking we can simply measure, for any two candidate depths in that
specimen, what fraction of nuclei genuinely appear in both. That turns an
assumption into a measurement, and it applies whether or not the ramp reaches 90 µm.
We will do that.

The interface changes you prompted are also live: greyscale nuclei is now the
default counting view rather than something to discover, and live/dead/unsure are
now different *shapes* as well as different colours. Two small images attached
showing both — you were right that hue alone was not good enough.

Thank you — genuinely the most useful set of replies I have had on this.

Best wishes,
Daniela

---

## Notes — not for the email

- Attach `for_torsten/1_three_views.png` and `2_marker_key.png` if this goes out
  instead of the separate short note; if that note has already gone, drop the
  penultimate paragraph.
- The concession on channels is real and should not be softened: a shared schedule
  would have been actively worse, and asking for it revealed we had the wrong model
  of our own measurement.
- The "your advice broke our instrument" point is worth keeping. It costs nothing,
  it is true, and it shows the advice was acted on rather than filed.
- Do not promise a date for the 3D overlap measurement — it needs the new stacks.
- Recorded in FINDINGS §4c.
