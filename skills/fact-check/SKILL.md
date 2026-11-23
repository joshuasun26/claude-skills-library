---
name: fact-check
description: Verify every factual claim in outbound content before it ships. Use before anything containing numbers, dates, statistics, percentages, prices, names or credentials goes to another person, such as client emails and texts, newsletters, social captions, flyers, proposals, reports and market updates. Trigger on "fact check", "verify these numbers", "is this accurate", "check my stats", "before I send this", or whenever you draft outbound content that asserts a fact. Also use to audit something already sent.
---

# Fact Check

Your credibility is the asset. One wrong number a reader can check costs more trust than ten good emails build.

## The failure this prevents
The most common way a bad number ships: an AI reuses a figure from an earlier conversation, a summary, or its own memory, and treats it as a source. It is not. Those are leads. Only a primary source opened in this session is evidence.

## The one rule
> **Every number that leaves this machine must be traceable, in this session, to a primary source actually opened with a tool call.**

If the source cannot be produced, the number does not ship. Not softened into "roughly" or "about". Removed.

## Source hierarchy
**Tier 1: your own systems of record.** Check these first. They usually hold the answer. Fill in this table once for your business:

| Kind of claim | Where the truth lives |
|---|---|
| Sales, revenue, client counts | your CRM or accounting system |
| Prices, fees, rates | your current dated price sheet |
| Market or industry data | the report or database you trust, by date |
| Credentials, license numbers | the issuing body's public lookup |
| Content performance | your analytics export |

**Tier 2: primary external sources fetched live this session.** Government data, the original study, the official report. Fetched now, not remembered.

**Tier 3: reputable secondary reporting**, cited by name and date, only when no primary exists.

**Never a source:** a previous AI session, a chat summary, a memory file, an earlier message in this conversation, or the model's trained knowledge.

## Procedure
1. **Extract.** Pull every checkable claim into a table: any number, percentage, date, dollar figure, count, ranking, superlative ("most", "fastest", "1 in 3"), named entity, credential, or cause-and-effect claim.
2. **Classify.** Name the system of record for each one.
3. **Verify.** Open it: query the table, read the file, fetch the URL. At least one tool call per claim. For long documents, split the claims across parallel subagents, each required to return the source it actually opened.
4. **Cross-check the basis.** Numbers shown side by side must come from the same report, the same definition and the same date. Flag mixed bases even when each number is right on its own.
5. **Verdict per claim:**
   - **VERIFIED:** source opened this session, figure matches. Record source and as-of date.
   - **STALE:** source found but older than the claim implies. Re-date it or drop it.
   - **UNSUBSTANTIATED:** no primary source found. Remove it.
   - **CONTRADICTED:** your own records disagree. Stop and show the conflict to the owner before shipping either version.
6. **Report before shipping.** Show the claim table with verdicts and sources. Anything UNSUBSTANTIATED or CONTRADICTED goes at the top, above the draft.
7. **Log.** Append every verified claim to a running `claim-ledger.md` with date, claim, source, as-of date and where it was published. Later, "where did this number come from" takes seconds.

## Rules that follow
- **Attach an as-of date to every stat that ships.** "41 days on market (source, June 2026)" survives scrutiny. A bare "41 days" does not.
- **A defensible qualitative claim beats a precise one you cannot back up.**
- **Round honestly.** Never in the direction that helps the argument.
- **Derived numbers show their work.** A "2.7x" must be reproducible from two verified inputs, and the math gets re-run.
- **Regulated figures get a second check** by whoever is responsible for compliance in your business.
- **Already sent?** Say so right away, propose the correction, and check every place it is live: web pages, PDFs, scheduled emails, posts.

## If the owner wants to ship it anyway
Say once, plainly, that the claim cannot be sourced and what the exposure is. If they still choose to ship, that is their call. Log it as **UNVERIFIED: shipped at owner's direction** so the record stays honest.

---
Part of the [Claude Skills Library](https://github.com/joshuasun26/claude-skills-library). Free to use and adapt under the MIT license.
