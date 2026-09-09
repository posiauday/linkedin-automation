# Go-to-market

Everything here is built on the same finding: **you are not selling software.**
You are selling LinkedIn ghostwriting, at ghostwriting prices, delivered by an
engine that costs you $1.30 a month to run. That gap is the whole business.

Research date: September 2026. Sources at the bottom. Where a number is my
estimate rather than a cited figure, it says so.

---

## 1. What the market actually pays

| What you sell | Market rate | Source |
|---|---|---|
| LinkedIn ghostwriting retainer | $500-$10,000/mo, most pay $2,000-$5,000 | Windmill Growth 2026 |
| AI automation freelance | $60-150/hr | Ciela AI 2026 |
| General Upwork average | ~$39/hr ($29-54) | Upwork In-Demand Skills 2026 |

The $497 one-time setup price in the first version of this playbook was wrong by
roughly 4-10x against what this market pays. It has been corrected below.

Why the gap exists: a normal ghostwriter's cost of delivery is their own hours,
so they cap out around 8-10 clients. Yours is API fees. You can hold 20+ clients
at a delivery cost under $30/month total. **Do not price like a freelancer with
an hourly cost.** Price at market and keep the margin.

---

## 2. Paths I evaluated and rejected

Recording these so you do not spend a week rediscovering them.

| Path | Why it fails for a $1,000 target | Evidence |
|---|---|---|
| Gumroad / template sales | Median **6-12 months** to $500/mo with no audience. Email drives 42% of sales and you have no list. | insightraider, mydesigns 2026 |
| Upwork / Fiverr bidding | **2-8 weeks** to first client. Beginner-open postings fell 15% → **under 9%**. | giguphq, Upwork 2025 data |
| Cold email at volume | Domain warmup alone takes 2-3 weeks before you can send safely. | standard deliverability practice |
| Ten products in ten niches | No distribution on any of them. Ten times zero. | — |

The common failure in all four: they need an audience or a reputation you do not
have yet. The service path is the only one where **one conversation with one
person** can produce $500 tomorrow.

---

## 3. The offer

Three tiers. The middle one is what you quote.

| Tier | Price | What it is |
|---|---|---|
| **Test month** | **$500** | 12 posts, published to their account, one month. The thing you actually sell first. |
| **Retainer** | **$1,500/mo** | 20 posts/mo, voice tuning, monthly strategy call. Where they land after the test. |
| **Executive** | **$3,000/mo** | Retainer plus comment-reply drafting and a quarterly positioning session. |

**Sell the test month, never the retainer.** The research is unambiguous: close a
paid test at roughly one-third of the package before proposing the retainer. It
removes the client's risk and gives you a clean exit if the fit is bad.

**Two test months is your $1,000.** That is the whole target. Two people.

Never do free trials. A free trial attracts people who were never going to pay
and it prices your work at zero in their head. $500 is small enough to say yes to
without a procurement process and large enough that they show up.

### Unit economics

| | Test month | Retainer |
|---|---|---|
| Revenue | $500 | $1,500/mo |
| API cost | ~$0.50 | ~$1.30/mo |
| Your time | ~3 hrs setup + 1 hr/wk | ~2 hrs/mo after setup |
| Effective rate | ~$70/hr | ~$750/hr |

At 10 retainer clients that is $15,000/mo against roughly $13 of API cost. The
constraint is not delivery capacity — it is how many conversations you have.

---

## 4. The funnel

```
  Target list (fractional execs, agency owners, consultants)
        │
        │  free sample: 5 posts written for them, no ask
        ▼
  Reply  ──────────────────────────────────  2-5% cold, far higher warm
        │
        │  15-min call, or just a DM thread
        ▼
  Test month $500  ─────────────────────────  this is the sale
        │
        │  they see 12 posts published, engagement moves
        ▼
  Retainer $1,500/mo  ──────────────────────  ~1/3 convert (my estimate)
```

Benchmarks for the top of that funnel: a free audit converts **2-5% on cold ICP
traffic**, 5-15% broadly, and **above 40% on targeted warm traffic**. A lead
magnet in the first message outperforms a pitch for a call by **3-5x on
click-through**.

That is why `sample.py` exists and why message one contains no pitch. You are
not asking for a call. You are handing over five posts.

### What the numbers mean for you

To close two test months, working backwards with the cold rate:

- 2 sales needed
- ~30% of qualified conversations close (estimate) → ~7 real conversations
- ~4% of cold sample sends produce a conversation → **~175 cold sends**
- At a safe 25/day, that is **7 days of sending**

Same math on your warm list at ~40%: **~18 warm sends**. This is why the warm
list is not a nice-to-have. It is 10x cheaper in time than cold, and it is the
entire difference between "this week" and "next month."

---

## 5. Channels, ranked by time-to-first-dollar

**1. Warm network DMs — days.** Everyone who already knows you and posts, or
says they should. First 1-3 clients in this business almost always come from the
extended network. Start here tonight.

**2. Public teardowns — 1-2 weeks.** Pick a well-known person in your niche,
publicly rewrite one of their posts, explain why the rewrite works. Post it. It
demonstrates skill instead of claiming it, and it is content *and* outreach at
once. This is the highest-leverage thing you can post.

**3. Comment-first outreach — 1-2 weeks.** Leave genuinely useful comments on
target prospects' posts for a week before any DM. When the DM comes, you are not
a stranger. Slow, but it converts far above cold.

**4. Niche communities — 2-4 weeks.** Founder Slacks, indie Discords, local
business groups. Be useful, never pitch. Answer content questions with real
answers.

**5. Cold DMs with the sample — ongoing.** The volume channel. Cap at 25-30/day
or LinkedIn restricts you, which ends the business.

**6. Your own LinkedIn, run by your own engine — 30-90 days.** Slowest to pay
and the most valuable long-term. You are selling LinkedIn presence; an empty
profile is the objection you cannot argue past. **Turn the engine on yourself
tonight, before you sell it to anyone.** It is also your only real proof.

### Paid ads: not yet

Do not run ads to a $500 offer with no case studies. LinkedIn ads run $8-15 CPC
in B2B; at a 2% landing conversion you would pay $400-750 per lead to sell a
$500 product. Revisit at 5+ clients and testimonials, and then only retarget
people who already saw a sample.

### Ad concepts, for when you get there

Written now so they exist, to be used after you have proof.

- **The fold.** Static image of a post cut at "see more" with the hidden 90%
  greyed. Copy: *"94% of your post is never read. The first line is the whole
  post."* → sample page.
- **Side by side.** Their real post next to your rewrite, permission granted.
  Copy: *"Same idea. Same person. One got read."* Strongest concept, needs a
  consenting client.
- **The empty calendar.** A month grid with two posts on it. Copy: *"You meant
  to post twice a week. This was March."* Speaks to the actual pain, which is
  guilt, not writing ability.
- **Cost frame.** Copy: *"A ghostwriter is $2,000 a month. Skipping it costs
  more."* For retargeting warm traffic only.

---

## 6. First 30 days

**Days 1-2 — make yourself the proof.** Configure the engine on your own
account. Generate 30 posts, read them, fix your `tone` and `banned_phrases`
until they sound like you. Publish the first one. You cannot sell LinkedIn
presence from a dead profile.

**Days 3-5 — warm list.** 10-15 people who already know you. Run `sample.py` for
each. Personal message, no pitch. Expect 4-6 replies.

**Days 6-10 — first teardown + first sales.** Post one public teardown. Convert
warm replies into test months. **This is where the first $1,000 realistically
lands.**

**Days 11-20 — cold at safe volume.** 25/day with samples. Second teardown.
Comment daily on 10 target prospects' posts.

**Days 21-30 — convert.** Test-month clients are 3 weeks in. Ask for the
retainer with their actual numbers in front of them. Ask every happy client for
one referral — referrals are the channel that eventually replaces all of this.

---

## 7. What I will not claim

- That this produces $1,000 overnight. The fastest realistic path to first money
  is **3-7 days**, through the warm list, and it depends on you sending messages.
- That the conversion estimates marked "estimate" are measured. They are
  reasoned from the cited benchmarks. Track your real numbers and replace them.
- That any of it works if the posts are bad. Everything above is distribution.
  Distribution multiplies quality; it does not substitute for it. Read the output
  before it goes anywhere near a client.

---

## Sources

- [LinkedIn ghostwriter cost 2026 — Windmill Growth](https://windmillgrowth.com/blogseo/linkedin-ghostwriter-cost)
- [Freelance AI automation rates 2026 — Ciela AI](https://ciela.ai/blogs/freelance-ai-automation-rates-2026)
- [Ghostwriter hourly rates — Upwork](https://www.upwork.com/hire/ghostwriters/cost/)
- [How to find ghostwriting clients 2026 — River](https://rivereditor.com/blogs/how-to-find-ghostwriting-clients-2026)
- [LinkedIn ghostwriting: build and scale — MagicPost](https://magicpost.in/blog/linkedin-ghostwriting)
- [How long to get your first Upwork client — GigUp](https://giguphq.com/blog/how-long-does-it-take-to-get-your-first-upwork-client)
- [Lead magnet conversion benchmarks 2026 — Digital Applied](https://www.digitalapplied.com/blog/lead-magnet-conversion-benchmarks-2026-b2b-data-reference)
- [Selling digital products on Gumroad 2026 — MyDesigns](https://mydesigns.io/blog/gumroad-for-selling-digital-products/)
- [What sells best on Gumroad 2026 — InsightRaider](https://insightraider.com/en/answers/what-digital-products-sell-best-on-gumroad)
