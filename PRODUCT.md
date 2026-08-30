# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Solo user: a contractor building and administering this CRM on behalf of **ISYN (Internacional de Subastas y Negocios)**, a real, operating Panamanian company (isynsubastas.com) specialized in public auctions, tenders, government contracting, and international business brokerage — vehicles, real estate, RAEE/scrap, and other asset categories. ISYN is the client and the true owner of the project and its brand; the person operating this tool day-to-day manages prospección of buyers on ISYN's behalf. Single-user tool for now; the data model and auth are already prepared to extend to more users later, but no second user exists yet. Design should stay lean for one operator, not anticipate team/role complexity prematurely.

## Product Purpose

A mini-CRM that centralizes, searches, filters, and lets the owner quickly contact potential buyers (national and international) for warehouse products. Success means shortening the loop from "found a prospect" to "sent them a personalized message" — no re-typing contact info, no juggling spreadsheets, no separate tools for tracking outreach history.

**Resolved:** the user confirmed ISYN's actual brief is "a way to find companies worldwide" with AI integration specifically requested — which is exactly the "Buscar con IA" feature already built (Gemini + Google Search grounding, not limited to any country or region). No further functional rescoping toward auction-specific terminology was requested; the buyer-prospecting model (search → draft review → approve into pipeline) already fits the brief as stated.

## Positioning

The edge over a spreadsheet or a generic CRM (e.g. HubSpot) is the tight, single-tool loop: search/filter a buyer → the same screen fires a pre-filled, templated email or WhatsApp message using that buyer's data → the contact and its history live right there, updated in one click — with no per-seat CRM licensing and none of the row-count unmanageability a spreadsheet hits. Confirmed by the user as the real differentiator ("velocidad de prospecto a contacto").

## Operating Context

- Real-prospect sourcing is manual: CSV/Excel import from Procolombia, cámaras de comercio, LinkedIn Sales Navigator exports, and Apollo.io web-app search exports (free plan; Apollo's Organization Search API is confirmed paid-tier-only per their own docs, so no API integration exists for it).
- Pipeline states per buyer: por contactar → contactado → interesado / descartado / cliente.
- Message templates support `{nombre_empresa}` and `{producto}` variables for email and WhatsApp.
- Every buyer has a contact-history log (bitácora): date, channel, outcome.
- Quick-contact actions open the user's own mail client (`mailto:`) or WhatsApp (`wa.me`) pre-filled — sending is always a manual, deliberate action by the user, never automated.
- Deploy target: Railway. SQLite locally, PostgreSQL in production via `DATABASE_URL`.

## Capabilities and Constraints

- Django + server-rendered Django templates + Bootstrap. No SPA/React.
- No automated mass email sending, ever — by explicit product decision.
- No automated scraping of social networks or websites — explicit exclusion, to avoid legal risk.
- One paid external API is now wired up: Gemini (Google) with Google Search grounding, used for the "Buscar con IA" feature (search real companies by category/sector, review as drafts, approve into the CRM). Costs real money — the user explicitly funded a small prepaid balance for this after confirming they understood the billing model. A hard daily cap (`BUSQUEDA_IA_LIMITE_DIARIO`, default 20 searches/day) exists specifically to prevent runaway cost. A Hunter.io integration endpoint also exists as a stub for a possible future paid integration, but nothing is wired up there.
- Auth exists (Django's built-in), scoped to a single active user today; the `Comprador.responsable` field anticipates more users later without any multi-user UI built yet.
- The product category currently being prospected is electronics — the first category the app has real screens and demo data for. Other product categories (whatever else sits in the bodega) are expected to follow the same model.

## Brand Commitments

Confirmed and binding: the product now carries **ISYN**'s real, existing brand identity — the actual logo asset (`static/img/isyn-logo.png`, a cropped version of the client-provided lockup), and a color palette sampled directly from that logo (Azul ISYN `#046cb3`, Marino ISYN `#014b72`, Gris ISYN `#595959`). "CenterComp" is retired as the product-facing name; it survives only as the internal Python package/folder name (`centercomp/`), an implementation detail with no user-visible presence. ISYN's own live site (isynsubastas.com) was reviewed as a reference but this CRM's own established Operate-mode system (stage meter, contact-row, single-shadow rule, etc. — see DESIGN.md) was kept and re-colored rather than rebuilt from scratch, since the user's request was specifically about visual identity, not a functional rebuild.

## Evidence on Hand

No real buyer/contact data exists yet. The buyer records currently in the database (~55, sector: electrónica) are explicitly fictitious demo data — marked in each record's `notas` field and using the reserved `@example.com` email domain — generated only to test the UI with realistic volume. Future design and content work must treat them as disposable placeholders, never as real customers, testimonials, or case studies. No real product photography, press, or testimonials exist.

## Product Principles

1. Every screen should shorten the path from "found a buyer" to "sent them a message" — that loop is the product's whole reason to exist.
2. Never automate outbound sending or scraping. The user stays the one who decides what leaves the building.
3. Design for one operator first. Don't build in multi-user role/permission complexity until a second real user shows up.
4. Default to zero paid dependencies unless the user explicitly and knowingly funds one. The Gemini AI search is the one confirmed exception, and it ships with a hard daily cap for exactly this reason.
5. Treat all current buyer records as disposable demo content — never as evidence of real customers or a claim about traction.
