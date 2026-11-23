---
name: carousel-readability
description: Mandatory pre-ship check for any fixed-canvas social image with text on it (Instagram carousel slides at 1080x1350, story cards, flyers viewed on phones). Spins a fresh critic that judges text size, spacing, overlap and contrast the way a viewer sees it, as a phone thumbnail at a glance, not zoomed in on a desktop. Use whenever a carousel or slide is about to be delivered, and again after any redesign or resize.
---

# Carousel readability check

Text that reads fine at 100% zoom on a desktop while you build a slide often comes out unreadable on a phone. Those are different tasks. Building means studying a full-resolution render up close. The viewer scrolls past a thumbnail at arm's length in under a second. Checking the first does not check the second.

**When to run it:** every time a carousel is built, and every time one is edited and reshipped. A fix that has not been re-checked is a guess.

## The check

Do not eyeball it yourself and call it done. After rendering, start a fresh subagent (or a separate model) with no context from the build. Give it only the rendered PNG files and this prompt:

```
Review this social carousel slide for READABILITY ONLY, as if you were scrolling past it
on a phone at a glance, not studying it at full resolution. Do not comment on taste, copy
or color, only whether a person can read every word without zooming in.

Check:
1. Any text under about 28px equivalent on a 1080x1350 canvas. Quote it.
2. Any text crossing, overlapping or touching another element (a line, another text
   block, a photo edge).
3. Weak contrast: light text on a light background, or text on a busy photo with no
   scrim or card behind it.
4. Uneven spacing that reads as a mistake even if nothing overlaps.
5. Anything that looks right at 100% but would be illegible shrunk to a ~350px-wide
   phone thumbnail. If in doubt, say so.

Return PASS, or a numbered list of concrete fixes, each naming the slide element and the
property to change (font-size, line-height, position, scrim opacity), not just
"make it bigger".
```

Make sure the critic actually looked at the image, not just the HTML or CSS. Readability is visual: a 31px font can still read small if the line-height is cramped or the color is close to the background.

## Starting floors (1080x1350 canvas)

These have tested readable with a serif headline and a clean sans-serif body. They are a floor, not a ceiling, and not a substitute for the check.

| Element | Too small in practice | Start at |
|---|---|---|
| Body or caption copy | 25px | 31px+ |
| Small-caps label | 19px | 22px+ |
| Data value next to a label | 25px | 30px+ |
| Section headline | 58px | 62px+ |

A different font, canvas size or busier photo changes what reads. Start here, then verify.

## Spacing, not just size

- **Compute centering instead of eyeballing offsets.** If a block sits between a divider and a footer, calculate its top from the real pixel gap. Bottom-anchored blocks drift into footers when content changes.
- **Recompute when content length changes.** Adding a row or a sentence moves everything below it. A pixel value copied from a slide with different content will not fit.

## Report

For each slide: PASS or the fix list, what was changed, and confirmation that the changed slide was re-rendered and re-checked. Ship only when every slide passes.

---
Part of the [Claude Skills Library](https://github.com/joshuasun26/claude-skills-library). Free to use and adapt under the MIT license.
