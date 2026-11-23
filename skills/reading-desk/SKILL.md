---
name: reading-desk
description: Run a Reading Desk, a separate, calm session that shows a numbered list of what needs your attention (emails that need an answer, reports, briefs) and walks through them one at a time, waiting for "next". Drafts replies, never sends. Use when someone says "reading desk", "walk me through my emails", "one at a time", "go through my inbox with me", or after inbox triage has produced its list.
---

# Reading Desk

A long list of emails or reports is easy to avoid. One item at a time, with a short summary and a suggested next step, is easy to get through. That is the whole design: you see a list, read one, say "next", read the next.

## Shape
- **Run it in its own session,** named `Reading Desk MM-DD`, so the conversation stays short and focused. Your main working session hands it the list; the desk only reads, talks and drafts.
- **The list lives in a file:** `~/.reading-desk/YYYY-MM-DD-READ-NOW.md`, one line per item with a title and where it lives (an email thread link or id, or a file path).
- **If there is no list yet, build it** from Inbox Triage's last run (`~/.inbox-triage/plan.json`): one line per item in the "replied", "needs an answer" and "waiting on" buckets, newest first. If triage has not run, run it first.
- **Order:** what someone is waiting on first, then new questions, then reading material. When the user asks for something specific, it jumps the queue.

## How the desk presents
1. Post the numbered menu, titles only, grouped by section. Mark items as done as you go.
2. For the current item, read it fully first (the whole email thread or the whole file), then give:
   - **What it is** (one line: who, what, when)
   - **What they need** (bullets: the actual ask, any deadline, anything you promised before)
   - **Suggested move:** reply now / reply later / no reply needed / hand off, plus one next step
   - **Draft reply** when a reply is needed, in the user's voice, short. If you have a profile from the `voice-profile` skill, load it first. Facts you do not know go in [brackets] for the user to fill. Never invent a date, a number or a commitment.
   - **Flags:** anything that needs checking before it goes out (a number, a promise, a sensitive topic)
3. Stop and wait for "next", a question, or an edit to the draft. Answer only from what you read.
4. Save approved drafts as email drafts. Never send. The user sends.
5. If the user mentions a new task while reading, write it to `~/.reading-desk/CAPTURED.md` so nothing gets lost, then go back to the list.

## Honest limits
- It only knows what is in the list you give it. Anything the triage missed, the desk misses too.
- Drafts are a starting point. Read before you send.

## Voice
Plain words, short paragraphs, headers and bullets. Phone-readable. No walls of text.

---
Part of the [Claude Skills Library](https://github.com/joshuasun26/claude-skills-library). Free to use and adapt under the MIT license.
