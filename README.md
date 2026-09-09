# LinkedIn Content Engine

Generates LinkedIn posts in a specific person's voice and publishes them on a
schedule through LinkedIn's official API. Built to run for **multiple accounts**
out of one repo, so it works as a product you sell, not just a script you use.

Running cost: about **$1.30/month** per account. GitHub Actions does the hosting
for free.

> **Start with [RESEARCH.md](RESEARCH.md)** — what the evidence says works, and an
> honest scoring of this repo against it, including what is still missing.
>
> **Trying to make money with this?** [GTM.md](GTM.md) has the market research,
> pricing, funnel and channel plan for both revenue tracks — selling to
> individuals, and licensing to agencies who run many client accounts. [SALES_PLAYBOOK.md](SALES_PLAYBOOK.md) has the
> target list, scripts and delivery checklist. Read GTM first — it explains why
> this is priced as ghostwriting and not as software.

---

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env          # add your CLAUDE_API_KEY
cp clients/_template.yaml clients/me.yaml   # then edit it
```

Generate five posts without publishing anything:

```bash
python run.py generate --client me -n 5
```

Read them. Adjust `tone`, `topics`, and `banned_phrases` in your YAML until the
output sounds like you. This is the step that matters — everything else is
plumbing.

### Going live on LinkedIn

1. Create an app at <https://www.linkedin.com/developers/apps> and request the
   **Share on LinkedIn** and **Sign In with OpenID Connect** products.
2. Generate an access token with scopes `openid`, `profile`, `w_member_social`.
3. Put it in `.env` as `LINKEDIN_ACCESS_TOKEN`, then:

```bash
python run.py whoami --client me     # prints your LINKEDIN_PERSON_ID
```

4. Set `ENABLE_LINKEDIN_POSTING=true` and run `python run.py run --client me`.

Tokens expire after 60 days. Refresh them or publishing stops silently.

---

## Commands

| Command | What it does |
|---|---|
| `run.py clients` | List configured clients and their post counts |
| `run.py generate -c SLUG -n 5` | Write 5 posts to `linkedin_posts/SLUG/`, publish nothing |
| `run.py carousel -c SLUG` | Generate a document carousel and render it to PDF |
| `run.py metrics -c SLUG` | Pull reactions and comments for published posts |
| `run.py list -c SLUG` | Show queued, published and failed posts |
| `run.py approve -c SLUG --id ID` | Approve a post (omit `--id` to approve all queued) |
| `run.py reject -c SLUG --id ID` | Un-approve a post |
| `run.py publish -c SLUG` | Publish the oldest queued post |
| `run.py run -c SLUG` | Generate one and publish it |
| `run.py whoami -c SLUG` | Look up the LinkedIn person ID for a token |
| `sample.py --name ... --niche ...` | Generate a free sample page for a prospect |
| `teardown.py --file post.txt` | Rewrite an existing post and explain what changed |
| `batch.py prospects.csv` | Generate samples + DMs for a whole prospect list at once |
| `dashboard.py --rate 297` | Ops view of every client: pipeline, approval queue, margin |

Publishing is off unless `ENABLE_LINKEDIN_POSTING=true`. Every command is a dry
run until you flip that.

Set `REQUIRE_APPROVAL=true` and nothing publishes until a human approves it. Turn
this on whenever you are posting to someone else's account.

### Running this for an agency

The engine is already multi-tenant, which is the expensive part of what agencies
pay for. `dashboard.py` is the operator view — every client, what is published,
what is waiting on approval, and what it cost:

```bash
python dashboard.py --rate 297     # margin at $297/client/month
```

It writes `dashboard.html` from the post archive. No server and no database:
regenerate it whenever you want a current picture.

---

## The outreach desk

`console/index.html` is the hosted version of the outreach workflow, published as
an Artifact. It keeps your pipeline, drafts each prospect's free posts, writes the
message, times the follow-up, and drafts your reply when they answer. You copy and
send by hand.

**Nothing is sent automatically, on purpose.** LinkedIn has no API for connection
requests or direct messages. Every tool that automates them drives a browser
against LinkedIn's terms, and that is the most common way accounts get permanently
restricted. Automate the drafting; send it yourself.

`batch.py` is the offline equivalent if you would rather work from files.

## Selling this as a service

`sample.py` is the outreach tool. It takes a prospect, writes five posts for
them, and produces a shareable page plus a DM script:

```bash
python sample.py --name "Sarah Chen" --role "Fractional CMO" \
    --niche "demand generation for B2B SaaS"
```

Host the resulting HTML anywhere with a link, paste the link into the DM, send.
Giving away real work before asking for money is what makes cold outreach work.

`teardown.py` is the other half: paste in a post someone already published and it
returns a rewrite plus a breakdown of each change. Use it in a DM as proof, or
publish the teardown yourself as content.

`batch.py` runs the sample generator over a whole list at once and produces a
worksheet with every message in send order:

```bash
cp prospects.example.csv prospects.csv    # then fill it in
python batch.py prospects.csv
```

It caps at 25 prospects per run on purpose. LinkedIn restricts accounts that
message in bulk.

Adding a paying client:

```bash
cp clients/_template.yaml clients/acme.yaml    # edit voice, topics, tone
```

Point `linkedin_token_env` and `linkedin_person_env` at that client's own
environment variables so accounts never cross. Add those as GitHub secrets and
the scheduled workflow picks the client up automatically.

---

## How it works

```
clients/<slug>.yaml   voice, topics, audience, credentials to use
        ↓
engine/generator.py   Claude writes posts against a forced JSON schema,
                      with recent post openings fed back in to avoid repeats
        ↓
engine/images.py      DALL-E image (optional — failure never blocks a post)
        ↓
engine/store.py       saved to linkedin_posts/<slug>/ as JSON
        ↓
engine/linkedin.py    initializeUpload → PUT bytes → create post
```

The image upload is three separate API calls. Scripts that skip the first two
post text only and never tell you — that is the most common way this breaks.

### Carousels

Document carousels are the highest-performing format on LinkedIn — roughly **6x
the engagement of a text-only post**, because swiping is dwell time and dwell
time is what the ranking measures.

```bash
python run.py carousel --client me --topic "what a price increase actually costs"
```

Claude writes 6-10 slides, Chromium renders them to a square PDF, and publishing
uploads it through LinkedIn's Documents API as a native document post. Rendering
needs Playwright (`pip install playwright && playwright install chromium`);
everything else in the engine works without it.

### Measuring results

```bash
python run.py metrics --client me
```

Pulls reactions and comments per published post and stores them on the record.
`dashboard.py` then shows engagement per client and the measured carousel-vs-text
lift **from your own account**, not from a blog post.

This matters commercially: clients in 2026 drop providers who cannot show
impact, and your own measured numbers are what move you up the pricing ladder in
[SALES_PLAYBOOK.md](SALES_PLAYBOOK.md).

### Post quality

Quality lives in two places, and neither is the code:

- **`engine/generator.py`'s system prompt** bans the tells that make AI posts
  obvious: emoji bullet lists, "Let's be honest", "unpopular opinion", claims
  without numbers. Edit it if you disagree with any rule.
- **The client YAML** carries the voice. `tone` and `banned_phrases` do more
  work than anything else in the file.

Recent post openings are sent back to the model on every run so it does not
write the same post twice.

---

## Costs

| Service | Per post | 30 posts |
|---|---|---|
| Claude (Sonnet) | ~$0.006 | $0.18 |
| DALL-E 3 | $0.04 | $1.20 |
| LinkedIn API | free | free |
| GitHub Actions | free tier | free |

Set `ENABLE_IMAGE_GENERATION=false` and it costs under 20 cents a month.
`CLAUDE_MODEL=claude-opus-5` raises quality and cost roughly 5x.

---

## Compliance

Uses LinkedIn's official API only. No scraping, no browser automation, no fake
engagement, no connection bots — all of which get accounts banned. Posting on
your own behalf with your own token is within LinkedIn's terms.

When you run this for a client, they must generate their own token from their
own account. Never ask for anyone's password.

---

## Repo layout

```
run.py                  CLI
sample.py               prospect sample generator (outreach)
teardown.py             rewrite someone's post + explain the changes
batch.py                whole prospect list -> samples + send worksheet
dashboard.py            agency ops view across all clients
engine/
  carousel.py           carousel generation + PDF rendering
  config.py             settings + client profile loading
  generator.py          Claude post generation
  images.py             DALL-E
  linkedin.py           publishing, image upload, whoami
  store.py              post archive and dedup history
clients/                one YAML per account
linkedin_posts/<slug>/  generated posts
samples/                prospect sample pages and teardowns
sales/index.html        the service sales page
console/index.html      outreach desk (pipeline + drafting, hosted as an Artifact)
RESEARCH.md             evidence audit + self-scoring + open gaps
GTM.md                  market research, pricing, funnel, channels, ads
SALES_PLAYBOOK.md       targeting, scripts, objections, delivery checklist
SKILL.md                the writing rules, as a Claude skill
```

MIT licensed.
