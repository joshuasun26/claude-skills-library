---
name: gauntlet-loop
description: Build and improve a flyer, video, or email through independent critique by a second model against a named, accessible reference. Stop after at most three build-and-review rounds. Draft work only.
---

# Gauntlet loop

Make a draft, let a second model challenge it against a real example, and repair the biggest gap. A polished first draft still deserves another pair of eyes.

## Choose a real reference

Use the specific reference I name. If none is supplied, ask me to choose one, or offer two named examples you can actually access. Do not build until the reference is available. A category such as "a premium flyer" is not a reference.

Keep the comparison fair: flyer against flyer, short video against a similar short video, email against a similar-purpose email. Match audience, destination, and viewing size. Learn from structure, clarity, and pacing without copying protected text, photographs, logos, or identity.

Confirm the intended audience, format, goal, required facts, and anything I want preserved. Missing facts stay clearly marked in a private draft, never invented.

## Build, critique, improve

Run a maximum of three rounds total. Each round means one candidate and one independent critique. If a correction is needed, it uses the next round.

1. **Build.** Produce the draft from my brief and the reference. For a visual piece, create a reviewable render if local rendering tools are available. Otherwise explain what I need to provide for visual review. Never use computer control, upload files, publish, or send anything.
2. **Prepare the comparison.** Give the critic the original brief, required facts, named reference, and candidate. Label the two artifacts A and B without saying which the builder made; keep the mapping for the final report. Do not give the critic the builder's self-assessment or a desired verdict.
3. **Use a second model.** Use an independent model only if it is already available and permitted to read these materials. Never silently substitute the builder as its own critic. If no second model is available, give me the prompt below to paste into another model myself. Do not transfer or upload my files. Label the result "awaiting independent critique" until I bring back its response.
4. **Review the actual result.** Flyers require the final rendered page, checked at print size and a phone preview. Videos require the rendered video with audio when available, or representative frames plus transcript and timing, explicitly labeled a limited review. Emails require the full subject and body; HTML email needs a rendered preview too. Source code alone cannot pass visual review.
5. **Revise.** Fix the largest meaningful gap and all factual or privacy defects. Re-render changed visuals before the next critique. A previous verdict does not cover a changed export.

## Copy into the second model

> You are an independent critic. Read the brief and inspect both artifacts. One is the named reference and one is a candidate; do not guess which is which. Choose A, B, or tie for this audience and goal. Give concrete reasons about clarity, usefulness, visual hierarchy or pacing, and natural language. Identify the single largest gap and the exact correction. Check facts against the supplied evidence, required content, privacy, clipping, legibility, and unsupported claims. For a visual piece, judge the rendered output, not its source code. Return a separate PASS or REDO for A and for B against the brief. PASS requires meeting the brief with no factual, privacy, or rendering defects; unknown evidence or an uninspected required element prevents PASS. A preference winner can still fail those checks. Say what you could not inspect. "Looks good" alone is not a review.

## Stop and report

Use the saved A/B mapping to find the candidate's verdict. Stop early only when the critic prefers that artifact and gives it PASS. A tie or an unresolved defect is not a win. After round three, stop even if the candidate still loses. Report what remains for me to decide.

Return the final draft, exact reference, critic model name, rounds used, verdict per round, largest correction, and remaining gaps. Identify exactly which export was reviewed, using a filename and hash when available. Separate private design readiness from any distribution decision. This skill grants no permission to send, post, upload, or publish.

Never fabricate sources, testimonials, numbers, compliance approval, or a critic's verdict. Remove private identifiers from review materials. Do not invent lending terms or make commitments on my behalf. Keep plain, warm English with no emojis or em-dashes.

## Method credit

Adapted from [gauntlet-loop by Jay E / RoboNuggets](https://github.com/robonuggets/gauntlet-loop), which credits the technique to Matt Shumer. Upstream license: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), confirmed in the [repository license](https://github.com/robonuggets/gauntlet-loop/blob/main/LICENSE) on November 19, 2026. Changes here: generic use for any draft, three-round cap, manual second-model fallback, and draft-only boundaries. Preserve this attribution when reusing the adaptation. No endorsement is implied.

## Try it

"Use gauntlet-loop on this flyer, video, or email. Compare it with [named reference] using a second model. Keep my required facts. Stop after three rounds."
