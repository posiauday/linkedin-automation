# Getting to $1,000

Read this part first, because it is the part that decides everything.

## The honest math

You asked for $1,000 by morning. Here is what is actually true.

**You are selling ghostwriting, not software.** The market pays $500-$10,000 a
month for LinkedIn ghostwriting, and most founders pay $2,000-$5,000. Your cost
to deliver is about $1.30 a month in API fees. [GTM.md](GTM.md) has the research
behind that number and the full channel plan.

So the target is not 35 strangers buying a template. It is **two people paying
$500 for a test month.** Two. And they should come from people who already know
you, because that converts roughly ten times better than cold.

| Timeframe | Realistic outcome |
|---|---|
| Tonight | Engine running on your own profile, 10-15 warm samples generated |
| Days 1-2 | Warm messages sent, first replies |
| Days 3-7 | **First test month sold, $500** |
| Days 7-14 | Second sale, $1,000 reached |
| Day 30 | Test months convert to $1,500/mo retainers |

**You will not have $1,000 in your account when you wake up.** I am not going to
tell you otherwise so the plan sounds better. Anyone promising guaranteed
overnight money is selling you something. The fastest honest path is 3-7 days,
it runs through your warm list, and it depends on you sending messages tomorrow.

## Pricing

Sell the test month. Never open with the retainer.

| Tier | Price | What they get |
|---|---|---|
| **Test month** | **$500** | 12 posts, published to their account, one month |
| **Retainer** | **$1,500/mo** | 20 posts/mo, voice tuning, monthly strategy call |
| **Executive** | **$3,000/mo** | Retainer plus comment drafting and quarterly positioning |

A paid test at roughly one-third of the package is the pattern that closes in
this market. It removes their risk and gives you a clean exit if the fit is bad.
Then you convert it to the retainer with three weeks of their own results in
front of you.

**Two test months is the $1,000.**

Never offer a free trial. It attracts people who were never going to pay, and it
prices your work at zero in their head before you start.

Do not discount below $350. A cheap price makes people trust the work less, not
more, and it attracts the clients who take the most handling.

### What it costs you to deliver

| | Test month | Retainer |
|---|---|---|
| Revenue | $500 | $1,500/mo |
| API cost | ~$0.50 | ~$1.30/mo |
| Your time | ~3 hrs setup, then 1 hr/wk | ~2 hrs/mo |
| Effective rate | ~$70/hr | ~$750/hr |

A normal ghostwriter caps out around 8-10 clients because delivery costs them
hours. Yours costs API fees. Price at market, keep the margin, and do not think
of yourself as an hourly freelancer.

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
   writing it, they can expense $500 without asking anyone.
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
> it publishes on the schedule you want.
>
> Rather than talk you into a retainer, do a paid test month: $500, twelve posts,
> published to your account. If it's working at the end of it we move to the
> monthly and if it isn't you walk, no argument.
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
> The system isn't really the product — the voice profile behind it is, and that
> takes me a few hours with you to build. The test month is $500 and includes it.
> If you'd genuinely rather run the software yourself I'll set it up on your own
> accounts for $997 and hand you the keys.

**"That seems expensive."**
> Ghostwriters for founders run $2,000-5,000 a month, and most of them are one
> person who can take eight clients. The test month is $500 and it's twelve posts
> published, not a proposal. If it doesn't move anything you've lost one month.

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
> in new topics as you go. $1,500 a month, cancel whenever.

About a third of test-month clients convert. Ten retainer clients is $15,000 a
month against roughly $13 of API cost, and your delivery time barely moves,
because the engine does not care how many clients it writes for.

The constraint is never delivery. It is how many conversations you have.

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
