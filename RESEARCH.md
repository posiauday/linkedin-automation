# Research audit — September 2026

A strict pass over what actually works, scored against what this repo does.
Sources at the bottom. Anything marked *estimate* is reasoning, not a cited number.

## What the evidence says

### LinkedIn ranking

| Finding | Number |
|---|---|
| Dwell time is the primary ranking signal, ahead of likes | 61s+ dwell → **15.6%** engagement vs **1.2%** at 0-3s |
| Document carousels beat every other format | **+596%** engagement vs text-only, +303% vs image, +278% vs video |
| Formatted content holds attention longer than wall-of-text | **+40%** dwell |
| Posts containing external links are suppressed | **~-60%** reach |
| Carousel slide count sweet spot | **6-10 slides** |

### Outreach

| Finding | Number |
|---|---|
| Good cold reply rate, broad B2B | **3-6%** |
| Well-executed targeted | **6-8%** |
| Signal-triggered / highly segmented | **8%+** |
| Advanced personalisation vs generic template | **18%** vs **9%** reply |
| Optimal sequence length | **2-3 touches**; beyond 7, returns collapse |
| Value of the first follow-up alone | **+40-50%** replies |

### What retains ghostwriting clients

Clients in 2026 ask for pipeline metrics — conversations started, inbound
enquiries, demo requests — not impressions and followers. **Agencies that cannot
show impact are losing clients.** The agencies with the best retention pair
content with systematic commenting rather than posting alone.

## Scoring this repo against that

Honest grades. Anything below B is a gap worth fixing.

| Area | Before | Why |
|---|---|---|
| Post format coverage | **D** | Text-only. The single highest-performing format on the platform was entirely absent. |
| Dwell-time optimisation | **C** | Hook rules were good; nothing about structure holding a reader to the end. |
| Link penalty awareness | **F** | Not mentioned anywhere. A client posting links would quietly lose 60% of reach. |
| Outreach personalisation | **B** | Five bespoke posts is strong, but not *signal*-triggered — no "why now". |
| Sequence length | **C** | Two touches. Evidence says three. The follow-up is the highest-yield message and there was only one. |
| Proof of results | **F** | Published and forgot. No metrics, no reporting — the exact thing that retains clients and unlocks higher pricing. |
| Voice fidelity | **B** | Per-client tone and banned phrases, but the profile is guessed by hand rather than learned from their real writing. |
| Safety / compliance | **A** | Official API only, approval gate, credential isolation, no DM automation. |
| Engagement beyond posting | **D** | Comments are left entirely manual with no support. |

The two F grades were the important ones: **no carousels** and **no
measurement**. One caps the product's ceiling, the other caps the price.

## What was implemented in response

Ranked by expected effect on revenue, highest first.

1. **Document carousels** (`engine/carousel.py`, `run.py carousel`) — generates
   slide content, renders a designed PDF, uploads it via LinkedIn's Documents
   API as a native document post. Addresses the +596% format gap.
2. **Results tracking** (`run.py metrics`, dashboard) — pulls reactions and
   comments per published post from the socialActions endpoint and stores them
   on the post record, so client reporting is real rather than asserted.
3. **Signal-triggered outreach** — a "why now" trigger per prospect, carried
   into the message. Targets the 9% → 18% reply gap.
4. **Three-touch sequence** — a second follow-up, taking the sequence to the top
   of the evidence-backed range instead of the bottom.
5. **Writing rules** (`SKILL.md`, generator prompt) — the link penalty, and
   dwell-oriented structure.

## What is still open

Listed honestly rather than quietly dropped.

- **Voice learning from real writing.** The client profile is still hand-written.
  Reading 20 of their actual posts and deriving the profile would beat it.
- **Comment drafting.** Evidence says commenting materially affects results.
  Deliberately not automated — auto-commenting is the fastest way to sound like
  a bot — but drafting support would help.
- **Pipeline attribution.** Reactions and comments are vanity-adjacent. What
  clients actually want is "this post produced three inbound enquiries", which
  needs the client to report back. No API gives it.
- **Cold email as a second channel.** Real APIs, legitimate to automate, needs
  2-3 weeks of domain warmup first.

## Sources

- [LinkedIn algorithm 2026, dwell time — Stackmatix](https://www.stackmatix.com/blog/linkedin-algorithm-how-it-works)
- [Dwell time optimisation — Linkmate](https://linkmate.io/blog/linkedin-dwell-time-optimization-2026/)
- [Algorithm: documents, newsletters, video — Dataslayer](https://www.dataslayer.ai/blog/linkedin-algorithm-february-2026-whats-working-now)
- [Carousel performance and structure — ViralBrain](https://www.viralbrain.ai/blog/linkedin-carousel-post)
- [How to post a carousel — Feedboss](https://www.feedboss.ai/blog/how-create-carousel-post-linkedin)
- [Documents API — Microsoft Learn](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/documents-api)
- [Analytics API and socialActions — Ayrshare](https://www.ayrshare.com/blog/how-to-post-and-get-analytics-with-the-linkedin-api/)
- [Cold outreach reply benchmarks — Apollo](https://www.apollo.io/insights/what-is-a-good-benchmark-for-reply-rates-in-cold-outreach)
- [Cold email statistics and sequence length — Martal](https://martal.ca/b2b-cold-email-statistics-lb/)
- [State of LinkedIn ghostwriting 2026 — Windmill Growth](https://windmillgrowth.com/blogseo/state-of-linkedin-ghostwriting-2026)
- [ROI of a LinkedIn ghostwriter — Leaders Social](https://www.leaders.social/linkedin-basics-training/the-roi-of-hiring-a-linkedin-ghostwriter-for-business-leaders-in-2026)
