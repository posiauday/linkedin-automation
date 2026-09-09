#!/usr/bin/env python3
"""Agency dashboard — one view of every client's content pipeline.

  python dashboard.py                       # all clients
  python dashboard.py --rate 297            # margin at $297/client/month
  python dashboard.py --open                # print the path to open

Reads the post archive and writes a static HTML page. No server, no database:
it is regenerated whenever you want a current picture.
"""

from __future__ import annotations

import argparse
import html
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engine.config import Client  # noqa: E402
from engine.store import Post, Store  # noqa: E402

OUT = Path(__file__).resolve().parent / "dashboard.html"
STATES = ("queued", "approved", "published", "error")


def collect(rate: float) -> dict:
    rows, awaiting, spend, totals = [], [], 0.0, Counter()

    for client in Client.load_all():
        posts = Store(client).load_all()
        counts = Counter(p.state for p in posts)
        cost = sum(p.cost_usd for p in posts)
        published = [p for p in posts if p.published]
        last = max((p.created_at for p in published), default="")
        measured = [p for p in published if p.measured_at]
        engagement = sum(p.engagement for p in measured)
        carousels = [p for p in published if p.kind == "carousel"]

        rows.append({
            "name": client.name,
            "slug": client.slug,
            "niche": client.niche,
            "counts": counts,
            "cost": cost,
            "total": len(posts),
            "last": last[:10] if last else "never",
            "engagement": engagement,
            # Averaged over measured posts only; dividing by all published ones
            # understates the client-facing number until every post is measured.
            "per_post": engagement / len(measured) if measured else 0.0,
            "measured": len(measured),
            "carousels": len(carousels),
        })
        awaiting += [(client, p) for p in posts if p.state == "queued"]
        spend += cost
        totals.update(counts)

    awaiting.sort(key=lambda pair: pair[1].created_at)
    revenue = rate * len(rows)

    # Format comparison, measured from this account rather than asserted from a
    # blog post. Only meaningful once both formats have been measured.
    every = [p for c in Client.load_all() for p in Store(c).published()]
    car = [p for p in every if p.kind == "carousel" and p.measured_at]
    txt = [p for p in every if p.kind != "carousel" and p.measured_at]
    compare = None
    if car and txt:
        ca = sum(p.engagement for p in car) / len(car)
        ta = sum(p.engagement for p in txt) / len(txt)
        # With a zero text average the ratio is undefined, not zero. Rendering
        # "0.0x" would read as carousels losing, which is the opposite claim.
        compare = {"carousel": ca, "text": ta,
                   "ratio": (ca / ta) if ta else None,
                   "n_car": len(car), "n_txt": len(txt)}

    return {
        "rows": rows,
        "awaiting": awaiting,
        "spend": spend,
        "totals": totals,
        "revenue": revenue,
        "margin": revenue - spend,
        "engagement": sum(r["engagement"] for r in rows),
        "compare": compare,
        "measured": sum(1 for p in every if p.measured_at),
        "published_total": len(every),
    }


def tile(label: str, value: str, note: str = "") -> str:
    return (f'<div class="tile"><p class="tl">{html.escape(label)}</p>'
            f'<p class="tv">{html.escape(value)}</p>'
            f'<p class="tn">{html.escape(note)}</p></div>')


def bar(counts: Counter, total: int) -> str:
    if not total:
        return '<div class="bar"><span class="seg empty" style="width:100%"></span></div>'
    segs = "".join(
        f'<span class="seg {s}" style="width:{counts[s] / total * 100:.1f}%" '
        f'title="{counts[s]} {s}"></span>'
        for s in STATES if counts[s]
    )
    return f'<div class="bar">{segs}</div>'


def client_row(row: dict) -> str:
    c = row["counts"]
    return f"""<tr>
  <td><strong>{html.escape(row['name'])}</strong><br>
      <span class="m">{html.escape(row['niche'])}</span></td>
  <td class="w">{bar(c, row['total'])}
      <span class="m">{row['total']} total</span></td>
  <td class="num">{c['published']}</td>
  <td class="num">{c['approved']}</td>
  <td class="num{' warn' if c['queued'] else ''}">{c['queued']}</td>
  <td class="num{' bad' if c['error'] else ''}">{c['error']}</td>
  <td class="num">{row['last']}</td>
  <td class="num">{row['engagement']}</td>
  <td class="num">{row['per_post']:.1f}<br><span class="m">{row['measured']} measured</span></td>
  <td class="num">${row['cost']:.4f}</td>
</tr>"""


def awaiting_row(client: Client, post: Post) -> str:
    return f"""<tr>
  <td class="mono">{html.escape(post.id)}</td>
  <td>{html.escape(client.name)}</td>
  <td>{html.escape(post.hook[:88])}</td>
  <td class="mono sm">run.py approve -c {html.escape(client.slug)} --id {html.escape(post.id)}</td>
</tr>"""


PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Content Pipeline</title><style>
 :root{{--paper:#EAEDE6;--surface:#fff;--raise:#F4F6F1;--ink:#161A16;--body:#2C332C;
   --muted:#5C665C;--line:#D2D8CB;--signal:#C0402A;--ok:#2F6B4F;--wait:#9A6B12;--idle:#A8B0A4}}
 @media(prefers-color-scheme:dark){{:root{{--paper:#11140F;--surface:#181C16;--raise:#1F241D;
   --ink:#E8EDE3;--body:#C6CDC0;--muted:#8B9488;--line:#2E352B;--signal:#E4785F;
   --ok:#7FBF9B;--wait:#D9A94E;--idle:#4A5246}}}}
 *{{box-sizing:border-box}}
 body{{margin:0;background:var(--paper);color:var(--body);
   font:400 14px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}}
 .wrap{{max-width:1180px;margin:0 auto;padding:40px 22px 72px}}
 header{{display:flex;justify-content:space-between;align-items:baseline;gap:20px;
   flex-wrap:wrap;margin-bottom:26px}}
 h1{{font:400 30px/1.1 Georgia,"Times New Roman",serif;color:var(--ink);
   letter-spacing:-.02em;margin:0}}
 .stamp{{font:400 12px/1 ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--muted)}}
 h2{{font:400 20px/1.2 Georgia,serif;color:var(--ink);margin:40px 0 12px}}
 .tiles{{display:grid;grid-template-columns:repeat(auto-fit,minmax(158px,1fr));gap:12px}}
 .tile{{background:var(--surface);border:1px solid var(--line);border-radius:4px;padding:16px 18px}}
 .tl{{font:500 10px/1 ui-monospace,monospace;letter-spacing:.13em;text-transform:uppercase;
   color:var(--muted);margin:0 0 9px}}
 .tv{{font:400 27px/1 Georgia,serif;color:var(--ink);margin:0;font-variant-numeric:tabular-nums}}
 .tn{{font-size:12px;color:var(--muted);margin:7px 0 0;min-height:16px}}
 .scroll{{overflow-x:auto;border:1px solid var(--line);border-radius:4px;background:var(--surface)}}
 table{{width:100%;border-collapse:collapse;min-width:760px}}
 th,td{{padding:12px 14px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}
 th{{font:500 10px/1 ui-monospace,monospace;letter-spacing:.13em;text-transform:uppercase;
   color:var(--muted);white-space:nowrap}}
 tr:last-child td{{border-bottom:0}}
 td.num,th.num{{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}}
 td.warn{{color:var(--wait);font-weight:600}} td.bad{{color:var(--signal);font-weight:600}}
 .m{{color:var(--muted);font-size:12px}}
 .mono{{font:400 12px/1.5 ui-monospace,monospace}}
 .sm{{font-size:11px;color:var(--muted)}}
 td.w{{min-width:180px}}
 .bar{{display:flex;height:7px;border-radius:4px;overflow:hidden;background:var(--raise);
   margin-bottom:6px}}
 .seg{{display:block;height:100%}}
 .seg.published{{background:var(--ok)}} .seg.approved{{background:var(--wait)}}
 .seg.queued{{background:var(--idle)}} .seg.error{{background:var(--signal)}}
 .seg.empty{{background:var(--raise)}}
 .key{{display:flex;gap:16px;flex-wrap:wrap;margin:10px 0 0;font-size:12px;color:var(--muted)}}
 .key i{{display:inline-block;width:9px;height:9px;border-radius:2px;margin-right:6px}}
 .empty-note{{background:var(--surface);border:1px solid var(--line);border-radius:4px;
   padding:22px;color:var(--muted)}}
</style></head><body><div class="wrap">
<header><h1>Content pipeline</h1><span class="stamp">{stamp}</span></header>
<div class="tiles">{tiles}</div>

<h2>Clients</h2>
<div class="scroll"><table>
<thead><tr><th>Client</th><th>Pipeline</th><th class="num">Published</th>
<th class="num">Approved</th><th class="num">Queued</th><th class="num">Errors</th>
<th class="num">Last post</th><th class="num">Engagement</th>
<th class="num">Per post</th><th class="num">Spend</th></tr></thead>
<tbody>{clients}</tbody></table></div>
<p class="key">
  <span><i style="background:var(--ok)"></i>published</span>
  <span><i style="background:var(--wait)"></i>approved</span>
  <span><i style="background:var(--idle)"></i>queued</span>
  <span><i style="background:var(--signal)"></i>error</span>
</p>

<h2>Waiting on you{awaiting_count}</h2>
{awaiting}
</div></body></html>"""


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--rate", type=float, default=0.0,
                        help="what you bill per client per month, for the margin figure")
    parser.add_argument("--out", default=str(OUT), help="where to write the HTML")
    args = parser.parse_args()

    data = collect(args.rate)
    if not data["rows"]:
        print("No client profiles in clients/. Nothing to report.")
        return 1

    t = data["totals"]
    tiles = [
        tile("Clients", str(len(data["rows"]))),
        tile("Published", str(t["published"]), "all time"),
        tile("Awaiting review", str(t["queued"]),
             "needs approval" if t["queued"] else "all clear"),
        tile("Errors", str(t["error"]), "check the logs" if t["error"] else "none"),
        tile("Engagement", str(data["engagement"]),
             f"{data['measured']} of {data['published_total']} measured"
             if data["published_total"] else "run: metrics"),
        tile("Generation spend", f"${data['spend']:.4f}", "all time, API only"),
    ]
    if data["compare"]:
        c = data["compare"]
        tiles.append(tile(
            "Carousel lift",
            f"{c['ratio']:.1f}x" if c["ratio"] else "—",
            f"{c['carousel']:.0f} vs {c['text']:.0f} per post"
            if c["ratio"] else "no text engagement to compare",
        ))
    if args.rate:
        tiles.append(tile("Monthly margin", f"${data['margin']:,.2f}",
                          f"at ${args.rate:,.0f}/client"))

    awaiting = data["awaiting"]
    if awaiting:
        body = ("<div class=\"scroll\"><table><thead><tr><th>ID</th><th>Client</th>"
                "<th>Opening line</th><th>Approve with</th></tr></thead><tbody>"
                + "".join(awaiting_row(c, p) for c, p in awaiting)
                + "</tbody></table></div>")
    else:
        body = '<p class="empty-note">Nothing waiting. Every generated post has been reviewed.</p>'

    page = PAGE.format(
        stamp=datetime.now(timezone.utc).strftime("%d %b %Y, %H:%M UTC"),
        tiles="".join(tiles),
        clients="".join(client_row(r) for r in data["rows"]),
        awaiting_count=f" ({len(awaiting)})" if awaiting else "",
        awaiting=body,
    )

    out = Path(args.out)
    out.write_text(page)
    print(f"{len(data['rows'])} client(s), {t['published']} published, "
          f"{t['queued']} awaiting review, ${data['spend']:.4f} spent")
    print(f"Dashboard: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
