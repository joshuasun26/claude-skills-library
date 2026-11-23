---
name: comment-to-dm-funnel
description: Design and stage an Instagram comment-keyword to DM-link to landing-page capture funnel for any CRM that supports the required integrations, with consent and duplicate-send checks.
---

# Comment to DM funnel

Prepare one campaign with one resource, keyword, post and landing page. Default to a disabled draft. This instruction file does not connect accounts, send DMs or create a background automation by itself.

## Confirm the path

Get the resource and audience, approved Instagram account, exact post or draft, keyword, landing-page domain, CRM, consent text and resource-delivery method. Ask the user to connect the accounts personally through an official integration. Never request passwords or place API tokens in browser code, URLs, exports or chat.

Check the selected provider's current official documentation for account eligibility, comment triggers, private replies, messaging windows and supported permissions. Do not assume every CRM can automate Instagram. If unsupported, deliver a provider-neutral workflow specification and a manual handoff; do not pretend an integration exists or bypass a restriction with scraping.

Inventory existing active workflows before adding one. Choose a distinctive keyword related to the resource; avoid short strings that match ordinary words. Confirm whether matching is whole-word, exact phrase or substring. Scope the trigger to the intended account and exact post identifier. A draft post cannot supply its final identifier yet. Leave the automation disabled until that mapping is verified.

## Draft the visitor journey

Write the post's keyword call to action, any public acknowledgment, one private reply with the resource landing link, landing-page copy and a form confirmation. Use only claims supported by the actual resource. Do not imply approval for a loan, savings, guaranteed results or a paid commitment.

Use a public HTTPS link with a campaign tag that contains no personal identifier. Build the page locally with a clear resource promise, minimal name/email fields, privacy information and separate optional marketing consent. Make clear whether the resource is available immediately or delivered later. A comment requests this resource, not blanket consent to future marketing.

Use a supported CRM form or an approved server-side receiver. Keep credentials server-side. Validate submissions; handle invalid addresses, provider failures and duplicate submissions. Show confirmation only after an acknowledged successful save, or verified delivery when the message promises delivery. Do not treat an opaque browser response as acceptance. Without a receiver, label the form as a local prototype.

## Stage the workflow

Create a readable workflow map:

`exact post + keyword -> eligibility/deduplication -> permitted private reply -> landing page -> validated form -> CRM record -> requested resource`

Use the provider's stable event identifier to suppress repeated webhook deliveries. Define a per-person, per-post, per-campaign send key and a persistent state for attempted, confirmed and uncertain sends. On timeout, check provider delivery state before retrying. Respect opt-outs and provider limits. Do not enroll a contact in marketing merely because a record was created. Never clone a live workflow and leave its inherited trigger or follow-up sequence enabled.

## Test, review and activate separately

Run local/sandbox tests with synthetic data: matching keyword, near-match that should not fire, wrong post, repeated comment/event, existing contact, opt-out, failed form save and uncertain DM delivery. Inspect the actual draft message, links and resource. A live test DM is still a send and needs approval for its test account and copy.

Deliver the workflow specification, copy, landing-page files, field mapping and test results, including what was not tested. Before activation, obtain explicit approval of the audience, final post, message, resource, form consent and enabled workflow. Leave it disabled if any prerequisite is missing. If separately authorized to activate, verify the enabled trigger and a permitted end-to-end test using provider evidence. Record real message IDs only when available; never claim delivery from a button click.

## Try it

"Use comment-to-dm-funnel. Plan a CHECKLIST resource funnel for my Instagram post and CRM. Draft the page and messages, map the fields, and test with synthetic data. Keep all automation disabled and send nothing."
