---
name: send-critic
description: Have a separate agent check an important email or text for accuracy and mistakes before it goes out. Use before any client, partner, group, money, legal or deal message, and anything that would go out under a standing approval the user already set up. The critic reads the full thread, checks the reply answers the latest message, recipients, facts (through fact-check), attachments, private info, promises, voice, dates and names, duplicate sends and text opt-outs, then returns PASS, FIX or HOLD. Trigger on "critique this before it goes", "check this email", "send critic", "is this ready to send", "review before sending", or automatically before sending any high-stakes message. Never grants permission to send.
---

# Send critic

A second pair of eyes on anything important before it leaves. The writer of a draft is the worst person to check it, because it reads what it meant to say. So a different agent, one that did not write the draft, reads the whole thread and the draft and looks for the mistakes that cost trust: wrong person, wrong number, missing attachment, a promise you never made.

This skill checks. It never sends. Sending requires the user's explicit approval for this message or an applicable standing approval set up outside this skill.

## First run: set your lists (one time)
Ask the user these questions, then save the answers to `~/.claude/send-critic/config.json` (start from `config/send-critic.example.json` in this folder). Show the file and get an OK before saving.

1. **High-stakes list.** "Which messages should always get the full check?" Offer examples: anything with money, prices, rates or fees; legal or contract topics; a first message to someone important to you; group emails; anything to a client about their deal; anything sent under a standing approval.
2. **Never-send list.** "What private info must never leave in a message?" Default: bank and card numbers, routing and wire details, Social Security or tax IDs, dates of birth, account or loan numbers, home addresses of private people, passwords and codes.
3. **Banned words.** "Any words or phrases that do not sound like you?" Default list in the example config. The user can add or remove any of them.
4. **Style limits.** Em dashes allowed or not, how many exclamation marks per message, emojis allowed or not.
5. **Opt-out list.** "Where do you keep people who asked not to be texted?" A file path or the CRM field to check. Use one email or phone per line; a CSV export also works.
6. **Send log.** Where to keep the log of what went out (default `~/.claude/send-critic/send-log.jsonl`).

If the user skips setup, use the example config and say so once.

## Pick the tier
Decide before doing anything else. When unsure, go one tier up.

| Tier | What | Check |
|---|---|---|
| **Skip** | Routine one-liners with nothing at stake: "Thanks, got it", "On my way", a reaction to a photo | None. Still never send without the user's go. |
| **Fast** | Normal messages: scheduling, a friendly follow-up, a short answer with no facts or money | The writer runs the helper scan and the checklist once, quickly. |
| **Full** | Anything on the user's high-stakes list, anything with a number, date or claim, anything with an attachment, any group message, and anything sent under a standing approval | A separate critic agent runs the whole checklist. |

## Who the critic is
- **A separate agent that did not write the draft.** In Claude Code, spawn a fresh subagent. If the user has another model available (another AI app or a second CLI), that is even better for high-stakes messages, because a different model misses different things.
- **Never the writer checking itself.** If no second agent is available, say "no independent critic available" and give the user the critic prompt below to paste into another model. Do not call your own review a PASS.

## What the writer hands the critic
Give the critic everything it needs and nothing that tilts it.
- The **full thread**: every message, oldest to newest, with dates and senders. For texts, include the last messages on any channel you can see.
- The **latest inbound message quoted word for word**, with its date.
- The **draft**: subject, body, and the exact **To, Cc and Bcc** lists.
- The **attachment list** with file names, plus the files themselves or their text.
- **What the user said** in chat this session about this message, quoted word for word, each line labeled "per owner". The user's own word is a source for what they did, said, decided or want included.
- The user's config (high-stakes list, never-send list, banned words, style limits).
- The **send log** and opt-out list, or the helper output from them.

Do not give the critic the writer's opinion of the draft, a hoped-for verdict, or "this should be fine." Let it judge cold.

## The checklist
The critic works through every item and writes a short note on each.

1. **Answers the real ask.** Does it reply to the latest message, not an older topic already handled? Does it answer every question the person asked? If the ask is unclear, say so; the draft goes back.
2. **Recipients.** Right person, right address (no look-alike or old address). To and Cc make sense. Nobody on it who should be off, and nobody missing who should be on. Reply versus reply-all is the right call. Group texts: is every number meant to see this?
3. **Facts and numbers.** List every number, date, price, name, credential and claim. First separate exact current-session quotes labeled "per owner" about what the user did, said, decided or wants included. Record those as sourced to the owner, retaining the quote; do not pass them to `fact-check`, whose source rules exclude chat. Pass all other claims to `fact-check` and use its verdicts. Memory, summaries and earlier sessions never qualify as "per owner". Anything that is a rate, price, legal term or regulated claim still needs a primary source, even if the user mentioned it; flag it rather than pass it.
4. **Attachments.** Every document the body mentions ("attached", "see the contract", "the flyer") is actually attached or linked, and it is the right file and the latest version. Open each one. Nothing attached that the body does not explain.
5. **Private info.** Nothing from the never-send list, in the body or inside any attachment. Nothing about one client in a message to another. Nothing internal (notes, other people's numbers, strategy) that should not leave.
6. **Promises and volunteering.** No commitments, deadlines, prices or favors the user did not say. No "I'll call you", "happy to hop on a call" or "I'll take care of that" unless the user's own words include it. Asking a named person to do something the user asked for is fine.
7. **Voice and tone.** Sounds like the user. No banned words. Style limits respected (em dashes, exclamation marks, emojis). Tone fits the moment: no cheerfulness on bad news, no stiffness with a friend.
8. **Dates, times and names.** Day of week matches the date. Time zone is stated when people are in different zones. Every name is spelled the way that person spells it in the thread.
9. **Duplicate send.** Was this already sent? Check the send log and the sent folder for the same recipient and the same or nearly the same message.
10. **Text opt-outs.** For texts and group texts, nobody on the opt-out list. Respect quiet hours if the user has them.

## Verdict
The critic returns exactly one of these, first line of its reply:

- **PASS**: no problems found. List what was checked.
- **FIX**: small, clear problems. Give each one as an exact edit: the old text, the new text, and why. The writer applies them. Re-run the critic after any change bigger than a typo, because a fixed draft is a new draft.
- **HOLD**: needs the user. Use for a missing fact only the user knows, an unclear ask, a possible wrong recipient, private info that might need to go, a contradiction between the draft and the records, or anything on the high-stakes list the critic cannot clear.

A clean helper scan is not a PASS. The scan catches typing patterns; the critic catches judgment mistakes.

## After the verdict
If the user has set up their own standing approval for a kind of message (outside this skill), PASS lets that approved pattern go. Without that, nothing goes until the user says yes to this message. A PASS is never a yes. The final-text approval steps below apply when there is no matching standing approval.
- Show the user the **final text exactly as it will go**, the recipients, the attachments and the verdict. Then ask one question: "Send it?"
- **Answering a detail question is not approval.** If the user replies "make it 10 AM" or "use my work email", apply it, show the final again and ask again. Only a clear yes ("send it", "yes, send", "go") sends.
- **Wording the user dictates is draft content**, not a send instruction. "Tell her thanks" means draft it and ask, unless they also said to send.
- If the user says to send without a check, it is their call. Send, run the critic right after, and tell them about anything it finds so they can correct it.
- After a send, log it (see the helper below) so the next duplicate check works.

## Optional helper
`scripts/send_check.py` (Python 3.9+, standard library only) does the mechanical parts so the critic can spend its attention on judgment.

```bash
# Scan a draft for banned words, em dashes, too many exclamation marks, emojis,
# long digit runs that look like account numbers, and attachment mentions.
python scripts/send_check.py scan draft.txt --attached contract.pdf --config ~/.claude/send-critic/config.json

# Before sending: was this already sent to this person? Is the number opted out?
python scripts/send_check.py dupe draft.txt --to priya@example.com
python scripts/send_check.py optout --to 5550100123

# After sending: record it. Stores a short hash and the recipients, never the message body.
python scripts/send_check.py log draft.txt --to priya@example.com --channel email --ref <provider id>
```

Exit code 0 means nothing flagged, 1 means something to look at, 2 means a usage error. The helper output goes to the critic as one input; it never decides the verdict.

## Critic prompt (paste into another model if you have no subagent)
> You are an independent critic. You did not write this draft. Read the full thread, the latest message, the draft with its To, Cc and Bcc lists, the attachments, and the owner's own statements (quoted word for word from this session and labeled "per owner", which count as sources for the owner's own actions, statements, decisions or requested inclusions; evaluate these separately from fact-check. Memory and summaries do not qualify. Rates, prices, legal terms and regulated claims still need primary sources). Check, and write one short note on each: (1) does it answer what the person actually asked in their latest message; (2) are the recipients right, and is reply versus reply-all right; (3) is every number, date, name and claim backed by a source in front of you, and which are not; (4) is every document the body mentions attached, and is it the right file; (5) is there any private info that should not leave, such as account numbers, ID numbers or someone else's details; (6) does it promise or volunteer anything the owner did not say; (7) does the voice match, with none of these banned words: [list]; (8) are dates, days of the week, time zones and name spellings right; (9) could this be a duplicate of something already sent; (10) for texts, is anyone opted out. First line: PASS, FIX or HOLD. For FIX, give exact old text and new text. For HOLD, say exactly what the owner must decide. Say what you could not check. "Looks good" is not a review.

## Example (fictional)
Draft reply to Priya Shah: "Hi Priya, attached is the updated proposal. The fee is 2% like we discussed. I'll call you Friday to go over it."

Critic returns **HOLD**:
- Ask: Priya's latest message asked whether the start date can move to March. The draft does not answer it.
- Attachments: body says "attached", nothing is attached.
- Facts: "2%" has no source in the thread or from the owner; fact-check marks it UNSUBSTANTIATED.
- Promises: "I'll call you Friday" was not in the owner's words. Remove it or confirm with the owner.

The writer brings the owner one question (the fee and the March date), attaches the proposal, drops the call line, and runs the critic again.

---
Part of the [Claude Skills Library](https://github.com/joshuasun26/claude-skills-library). Free to use and adapt under the MIT license.
