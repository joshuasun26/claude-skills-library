---
name: realtor-showcase-page
description: Build a mobile-friendly one-page get-to-know-your-agent showcase and QR asset for an open-house flyer, using approved realtor facts, photos and public contact details.
---

# Realtor showcase page

Create a realtor introduction page, not an invented biography or a full property portal. Work locally until the user approves a specific publication destination.

## Inputs and sources

Ask for the realtor's approved name, portrait, public business contact details, brokerage disclosures, service areas, short bio, specialties, preferred action and chosen style. Get a live domain/path if one exists. Ask which supplied photos, videos, testimonials and social links may be used publicly. For a loan officer helping a realtor, do not imply the realtor endorses the lender or agrees to a referral arrangement.

Open the supplied sources and save an as-of fact list in `SOURCES.md`. Label firsthand user statements as such. Do not invent years in business, sales totals, credentials, awards, specialties, recent closings or testimonials. Obtain permission for attributed quotes and headshots. Use public business contacts, never a client list or personal account details. Flag requested but unverified claims for review without silently dropping them.

## Compose one useful page

Use semantic HTML/CSS with separate local assets. A self-contained HTML file is fine for a small page. If file creation is unavailable, provide the HTML in chat and explain how to save and preview it. Do not require a private template, framework, paid service or another installed skill.

Build these sections only when there is source content:

1. Portrait, name and a concrete one-sentence introduction.
2. A short story about how the agent helps clients, drawn from the approved bio.
3. Verified specialties or service areas, using welcoming language without demographic steering.
4. A small selection of approved photos, testimonials or useful resources.
5. One primary action, such as contact the agent, with verified public business links.
6. Brokerage disclosures and a brief privacy explanation if anything is collected.

Design for a visitor arriving from a printed QR on a phone. Use readable type, strong contrast, compressed images, descriptive alt text, keyboard focus and a clear contact action. Avoid autoplay sound. Respect reduced-motion preferences and show useful content with JavaScript disabled. No trackers, hidden form destinations or embedded secrets.

Default to `mailto:` and `tel:` links that open the visitor's own app. If the user requests a lead form, collect only necessary fields, explain where data goes, separate resource delivery from marketing opt-in, and require an approved backend. Never display a success message on a timeout or failed response. A static form without a receiver is a prototype; label it clearly in the handoff.

## Verify and prepare the QR

Preview locally at roughly 375 px and 1440 px widths. Check overflow, text size, image crops, links, keyboard access and reduced motion. Inspect actual screenshots and review every public fact. Deliver `index.html`, assets, source notes and a deployment handoff. Do not deploy or change DNS without explicit authorization.

Generate the production QR only for the user-approved live public HTTPS URL. Decode it from the exported flyer-size image and require an exact match. Verify an anonymous visitor reaches the intended agent page on mobile, without a sign-in or private preview requirement. If the destination is not live, provide a clearly labeled preview QR separately and explain that the production QR is unfinished. Never substitute localhost or an internal preview in print-ready materials.

## Try it

"Use realtor-showcase-page with this approved bio, portrait and public business information. Build a local phone-friendly page for my open-house QR. Show the preview and list what must be verified before publication."
