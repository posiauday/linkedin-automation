# Getting to $1,000

Read this part first, because it is the part that decides everything.

## The honest math

You asked for $1,000 by morning. Here is what is actually true.

Selling a $29 template needs ~35 strangers to buy from a cold start with no
audience and no reviews. That does not happen overnight. Nothing does.

Selling **done-for-you setup at $350 needs three people to say yes.** Three is a
number you can actually reach. That is the entire strategy: fewer buyers, higher
price, and something valuable handed over before you ask for anything.

What is realistically achievable:

| Timeframe | Realistic outcome |
|---|---|
| Tonight | 20-30 samples generated, 20-30 DMs sent |
| Tomorrow | 4-8 replies, 1-2 calls booked |
| 48-72 hours | First 1-2 sales, $350-700 |
| 7 days | $1,000-1,500 if you keep sending daily |

**You will most likely not have $1,000 in your account when you wake up.** I am
not going to tell you otherwise so the plan sounds better. Anyone promising
guaranteed overnight money is selling you something. What you can have by
morning is 25 pieces of personalized outreach already sent, which is the only
thing that makes the $1,000 happen this week instead of never.

If you need money faster than that, the honest answer is that selling to people
who already know you beats selling to strangers by an enormous margin. Start
with your warm list. See "Hour 1" below.

## Pricing

Three tiers. Quote the middle one by default.

| Tier | Price | What they get |
|---|---|---|
| **Setup** | $297 | Engine configured to their voice, 30 posts generated, they publish manually |
| **Done-for-you** | $497 | Everything above, plus connected to their LinkedIn, publishing on a schedule, 30 days of adjustments |
| **Managed** | $297/mo | Ongoing, you review posts weekly and tune the voice |

Two Done-for-you sales is $994. That is the target. Do not discount below $250;
a cheap price makes people trust it less, not more, and it attracts the clients
who take the most work.

The monthly tier is the real prize. Three managed clients is $891/month
recurring, which pays your subscription every month instead of once.

## Hour 1: the warm list (do this before any cold outreach)

Open your LinkedIn connections. Write down every person who fits **all three**:

1. Posts on LinkedIn, or has said they should post more
2. Sells something where credibility matters — consultants, agencies,
   recruiters, coaches, founders, fractional execs
3. Would recognize your name

Aim for 10 names. These people convert 10-20x better than strangers because the
trust already exists. Message them first, tonight, before anything else.

## Hour 2-4: the cold list

Who to target, in priority order:

1. **Fractional executives** (CMO, CFO, COO). Their entire pipeline comes from
   LinkedIn presence. They have budget and they know it.
2. **Agency owners** (10-50 people). They understand content value, they hate
   writing it, they can expense $497 without a meeting.
3. **Recruiters at boutique firms.** Post constantly, always short on time.
4. **B2B consultants and coaches.** Presence is the product.

Who to avoid: anyone with under 500 followers, anyone whose profile is empty,
big-company employees (no budget authority), and people already posting daily
with high engagement — they have this handled.

Find them: LinkedIn search for "fractional CMO", filter to 2nd degree, sort by
recent activity. Take the ones who posted in the last month but not last week —
they want to be consistent and are failing at it. That gap is your entire pitch.

## The sequence

For each prospect:

```bash
python sample.py --name "Sarah Chen" --role "Fractional CMO" \
    --niche "demand generation for B2B SaaS" \
    --audience "Series A founders without a marketing leader"
```

This writes `samples/sarah-chen.html` and `samples/sarah-chen-dm.txt`.

Host the HTML anywhere that gives you a link — Netlify Drop, GitHub Pages, or
Google Drive with link sharing. Paste the link into the DM. Send.

**Never send more than 25-30 DMs in a day.** LinkedIn restricts accounts that
blast messages, and a restricted account ends this business before it starts.
Twenty-five thoughtful messages beat a hundred that get you flagged.

## What to say

The DM script is generated for each prospect. The shape of it matters more than
the words:

- **No pitch in message one.** You are handing over five free posts. That is it.
- **Name the specific thing** they work on. Generic outreach reads as automated,
  which is fatal when you are selling automation.
- **Give them an easy out.** "Use them or don't" removes the pressure that makes
  people ignore messages.
- **One follow-up, two days later. Then stop.** Chasing burns the relationship
  and your reputation.

When they reply positively, do not send a proposal document. Send this:

> Happy to set it up on your account. It takes me about a day: I configure it to
> your voice, generate the first 30 posts for you to approve, then connect it so
> it publishes on the schedule you want. $497, and I'll refund it if the first
> ten posts aren't something you'd actually publish.
>
> Want me to start?

That refund line closes deals. It costs you almost nothing because if the posts
are good, nobody asks for it, and if they are bad you should refund anyway.

## Objections

**"How is this different from ChatGPT?"**
> It isn't the writing, it's that it runs without you. ChatGPT needs you to show
> up and prompt it. This publishes on Tuesday whether you remembered or not. The
> five posts I sent were generated without me touching them.

**"Will people know it's AI?"**
> They'd know if it opened with "In today's fast-paced world." That's why the
> generator is explicitly blocked from writing like that. You saw five posts —
> did they read as AI to you? And you approve everything before it publishes.

**"Can I just buy the code?"**
> Yes, $297 and you set it up yourself, needs about two hours and three API keys.
> Most people would rather I did it. Which do you want?

**"That seems expensive."**
> A freelance ghostwriter charges $1,500-3,000 a month for the same output. This
> is one payment. If you post twice a week for a year, it costs you about four
> dollars a post in API fees.

**"Let me think about it."**
> Fair. I'll leave the five posts with you either way. If you publish one and it
> does nothing, you have your answer and you've lost nothing.

## Delivering without losing money

When someone pays, this is the checklist. It takes about 90 minutes, not a day —
quote a day so you look good.

1. Get their LinkedIn access token and person ID (`python run.py whoami`).
2. Copy `clients/_template.yaml` to `clients/<their-slug>.yaml`.
3. Fill in name, role, niche, audience, tone, topics. Spend real time on `tone`
   and `banned_phrases` — that is where voice actually lives.
4. `python run.py generate --client <slug> -n 30`
5. Read all 30. Delete the weak ones. Regenerate. **Never send unread output to
   a paying client.**
6. Send the batch for approval, then enable publishing.
7. Add their env vars as GitHub secrets and their slug to the workflow matrix.

Charge for a rush setup ($150 extra for same-day). Some people will pay it.

## After the first $1,000

The one-time sales are how you start. The recurring revenue is the business.
When you deliver a setup, say this at handover:

> I'll check in monthly to tune the voice as your positioning shifts, and swap
> in new topics as you go. $297 a month, cancel whenever.

About a third of setup clients take it. Ten managed clients is $2,970/month,
and at that point your subscription fee is not a question you think about.

---

## Assets in this repo

| Asset | Where | What it's for |
|---|---|---|
| Sales page | `sales/index.html` | Send to warm leads and anyone who replies. Also published as an Artifact. |
| Sample generator | `sample.py` | The cold outreach tool. One page + DM per prospect. |
| DM scripts | generated per prospect | First message and the single follow-up |
| Delivery checklist | above | What to do the moment someone pays |

Before sending the sales page anywhere, replace `REPLACE-WITH-YOUR-EMAIL@example.com`
in `sales/index.html` with a real address, and share the Artifact so the link works
for people other than you.
