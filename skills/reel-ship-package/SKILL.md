---
name: reel-ship-package
description: Pre-delivery checklist for any finished short vertical video (talking head, b-roll, showcase) before it counts as shipped. Produces the video plus a size-safe copy, a paste-ready caption, a thumbnail, audio options, a fact-check on anything numeric, a face and permission check, and a readability check on any stills, then delivers the package to the owner for review. Use the moment a reel finishes rendering, or when someone asks "is this ready", "package this reel" or "ship the reel". It never posts or schedules anything.
---

# Reel ship package

A reel is not done when the mp4 renders. It is done when the owner can post it without doing any more work. Finished renders that sit on disk with no caption, no thumbnail and no music are the most common way good content never goes out.

**The hard line:** this skill ends at the owner's own review channel (their phone, a shared folder, a private message to themselves). It never posts to a social account, never schedules and never publishes. The owner releases it in a separate step.

## The checklist (all eight before it counts as shipped)

### 1. The video, plus a copy that actually transmits
- Messaging apps and bots cap file size. Find the limit of the delivery channel you use and target well under it (for a 50 MB cap, aim under 40 MB).
- If the master is over the target, make a compressed copy at the same 1080x1920 geometry.
- Check the byte size of the exact file you are about to deliver, on disk, right before delivery, and state the number. A command that exited cleanly is not proof of output size.

### 2. Caption
- Write it in the owner's voice. If they have a voice profile skill, load it first.
- Add something the video does not already say: context, the human turn, a local detail. Never recap what is on screen.
- Make it paste-ready: save it alone in `CAPTION.txt` next to the video, with no title line, notes or character counts inside it.
- Check the platform's caption and hashtag limits and count before calling it final.

### 3. Thumbnail
- Use the owner's saved thumbnail template if there is one. Swap the image and words; do not redesign the look each time.
- Never put text across a face. Check where the face sits in this specific frame.

### 4. Audio
- Suggest five searchable track options with a one-line reason each, tied to this cut's pacing and energy.
- Never claim a track exists or is licensed unless you have the file and the license. Adding a track is a separate step.

### 5. Fact-check
- Any number, price, date or credential in the caption or burned into the video needs a primary source opened in this session. Run the `fact-check` skill on the caption.

### 6. Faces and permission
- No caption or thumbnail text over a face during the whole time the text is on screen. Sample frames across that window and say how many you checked.
- Check any frame with a child in it specifically.
- Permission to show a person is per piece and per person. A yes for one reel does not carry over to a new cut or a new face.

### 7. Readability of stills
- If the package includes slides, end cards or cover images, run the `carousel-readability` skill on them.

### 8. Delivery and read-back
- Send a short summary first (what this is, what is included, what is still open), then the video, the thumbnail and the caption as separate deliveries, so one failure does not hide the rest.
- Read the actual result of each delivery before saying it arrived. The absence of an error is not proof of delivery.

## Report back

In one place: what was delivered (video, thumbnail, caption, each confirmed), what is still open (no track chosen, a permission question, an unsourced number), and where the files live. Never say "shipped" while any item above has a gap. Say what is missing instead.

---
Part of the [Claude Skills Library](https://github.com/joshuasun26/claude-skills-library). Free to use and adapt under the MIT license.
