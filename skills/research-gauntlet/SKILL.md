---
name: research-gauntlet
description: Run an important research question through two or three independent models, keep their work separate until each is saved, then merge with a skeptical critique and a sourced verdict. Use when someone says "research gauntlet", "deep research this", "compare these options properly", or when a decision is costly enough that one model's first answer is not enough. Read-only research; it never sends, buys, installs or publishes.
---

# Research gauntlet

One model's research answer tends to agree with whatever the question assumed. This skill gets two or three independent reads of the same evidence, then a final critic who tries to break the merged answer before you act on it.

## 1. Write the brief first

Before anyone researches, write `BRIEF.md` with:

- **The question**, in one sentence, and the decision it feeds.
- **Timeframe**, for example "sources from the last 12 months".
- **Audience** for the answer.
- **Decision criteria**: what would make option A beat option B.
- **Source budget**: for example up to 20 sources or videos.
- **What you already have** (tools, assets, prior notes) so the answer is applied, not generic.
- **What would prove the hypothesis wrong.** If nobody can name this, the research is a search for confirmation.

## 2. Keep the roles separate

| Role | Who | Job |
|---|---|---|
| Finder | Any model with web search | Collect public source URLs and metadata, with an opened date for each. |
| Extractor | A script where possible | Pull transcripts or page text and keep timestamps and URLs beside each excerpt. Missing transcripts stay "not scored"; never summarize from a description alone. |
| Analyst A | Model 1 | Answers the brief from the raw sources only. |
| Analyst B | Model 2 (a different model family if you have one) | Answers the same brief from the same raw sources, without seeing Analyst A. |
| Critic | The strongest model available | Reads the raw evidence and the question **before** reading either analysis, then attacks the merged draft. |

Give each analyst the brief and the raw sources, never another analyst's output. Save each result to its own file before any merging starts. If you only have one model, run the analysts as separate fresh sessions and say so in the report. That is weaker independence, not the same thing.

## 3. Evidence rules

- Every material finding carries a URL, an opened or as-of date, and a timestamp or quote location.
- Separate what a creator **claims** from what was **independently verified**.
- Note commercial incentives, such as affiliate links or a speaker who sells the tool.
- Disagreements between analysts are resolved by going back to the source, not by vote. Unresolved ones stay in the report as open uncertainty.

## 4. The critic pass

Ask the critic to look for unsupported claims, skipped counter-evidence, selection bias in the sources, missing tests, and drift from what the brief actually asked. The critic returns PASS or a numbered list of fixes.

## 5. Stop rule

At most **three** revise-and-critique rounds, or the budget in the brief, whichever comes first. A missing analyst or an unfinished extraction is **incomplete**, never PASS. After round three, stop and report the remaining gap.

## 6. Deliverable

`VERDICT.md` with:

1. Ranked answer and the single first action.
2. A stop condition: what result would tell you to abandon the plan.
3. Source index (URL, opened date, what it supported).
4. Critique receipt: which models ran which role, rounds used, final verdict.

Never claim a model ran a role that it did not. Research approval is not approval to send, buy, install, schedule or publish anything.

---
Part of the [Claude Skills Library](https://github.com/joshuasun26/claude-skills-library). Free to use and adapt under the MIT license.
