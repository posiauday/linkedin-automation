#!/usr/bin/env python3
"""Batch sample generator — turn a prospect list into a night's outreach.

Reads a CSV, writes one sample page per prospect plus a single worksheet with
every DM in send order, so the morning's job is copy, paste, send.

  python batch.py prospects.csv

CSV columns: name,niche  (required)  role,company,audience  (optional)

  name,role,company,niche,audience
  Sarah Chen,Fractional CMO,,demand gen for B2B SaaS,Series A founders

Sends are capped by default. LinkedIn restricts accounts that message in bulk,
and a restricted account ends the business before it starts.
"""

from __future__ import annotations

import argparse
import csv
import html
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engine.config import Client, Settings  # noqa: E402
from engine.generator import Generator  # noqa: E402
from sample import DM, FOLLOW_UP, SAMPLES_DIR, build_page, slugify  # noqa: E402

DAILY_CAP = 25


def read_prospects(path: Path) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"error: no CSV at {path}")
    with path.open(newline="") as handle:
        rows = [
            {(k or "").strip().lower(): (v or "").strip() for k, v in row.items()}
            for row in csv.DictReader(handle)
        ]
    prospects = [r for r in rows if r.get("name") and r.get("niche")]
    skipped = len(rows) - len(prospects)
    if skipped:
        print(f"note: skipped {skipped} row(s) missing name or niche")
    if not prospects:
        raise SystemExit("error: no usable rows. Needs at least 'name' and 'niche' columns.")
    return prospects


def worksheet(entries: list[dict]) -> str:
    rows = "".join(
        f"""<tr>
  <td class="n">{i}</td>
  <td><strong>{html.escape(e['name'])}</strong><br><span class="m">{html.escape(e['niche'])}</span></td>
  <td><a href="{html.escape(e['file'])}">sample page</a></td>
  <td><textarea readonly rows="7">{html.escape(e['dm'])}</textarea></td>
  <td><input type="checkbox" aria-label="sent"></td>
</tr>"""
        for i, e in enumerate(entries, 1)
    )
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Outreach Worksheet</title><style>
 :root{{--paper:#EAEDE6;--surface:#fff;--ink:#161A16;--muted:#5C665C;--line:#D2D8CB;--signal:#C0402A}}
 @media(prefers-color-scheme:dark){{:root{{--paper:#11140F;--surface:#181C16;--ink:#E8EDE3;
   --muted:#8B9488;--line:#2E352B;--signal:#E4785F}}}}
 *{{box-sizing:border-box}}
 body{{margin:0;background:var(--paper);color:var(--ink);
   font:400 15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}}
 .wrap{{max-width:1100px;margin:0 auto;padding:44px 22px 80px}}
 h1{{font:400 34px/1.15 Georgia,serif;margin:0 0 8px;letter-spacing:-.02em}}
 .lede{{color:var(--muted);margin:0 0 28px;max-width:60ch}}
 .warn{{border-left:3px solid var(--signal);padding-left:16px;color:var(--muted);margin:0 0 28px}}
 table{{width:100%;border-collapse:collapse;background:var(--surface);
   border:1px solid var(--line);border-radius:4px;overflow:hidden}}
 th,td{{padding:14px 12px;border-bottom:1px solid var(--line);vertical-align:top;text-align:left}}
 th{{font:500 11px/1 ui-monospace,SFMono-Regular,Menlo,monospace;letter-spacing:.12em;
   text-transform:uppercase;color:var(--muted)}}
 td.n{{font-variant-numeric:tabular-nums;color:var(--muted);width:38px}}
 .m{{color:var(--muted);font-size:13px}}
 a{{color:var(--signal)}}
 textarea{{width:100%;min-width:320px;font:400 13px/1.5 ui-monospace,monospace;
   background:transparent;color:var(--ink);border:1px solid var(--line);border-radius:3px;
   padding:9px;resize:vertical}}
 input[type=checkbox]{{width:20px;height:20px;accent-color:var(--signal)}}
 tr:last-child td{{border-bottom:0}}
</style></head><body><div class="wrap">
<h1>Outreach worksheet</h1>
<p class="lede">{len(entries)} prospects. Host each sample page, paste its link into the
   DM where it says PASTE LINK, send, tick the box.</p>
<p class="warn">Stop at {DAILY_CAP} sends in a day. LinkedIn restricts accounts that
   message in bulk, and getting restricted ends this.</p>
<table><thead><tr><th></th><th>Prospect</th><th>Asset</th><th>Message</th><th>Sent</th></tr></thead>
<tbody>{rows}</tbody></table>
</div></body></html>"""


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("csv", help="prospect list")
    parser.add_argument("--count", "-n", type=int, default=5, help="posts per prospect")
    parser.add_argument("--limit", "-l", type=int, default=DAILY_CAP,
                        help=f"max prospects to process (default {DAILY_CAP})")
    args = parser.parse_args()

    prospects = read_prospects(Path(args.csv))
    if len(prospects) > args.limit:
        print(f"note: {len(prospects)} rows, processing the first {args.limit}")
        prospects = prospects[: args.limit]

    settings = Settings()
    try:
        generator = Generator(settings)
    except RuntimeError as exc:
        print(f"error: {exc}")
        return 1

    SAMPLES_DIR.mkdir(exist_ok=True)
    entries: list[dict] = []
    failed: list[str] = []

    for index, row in enumerate(prospects, 1):
        name, niche = row["name"], row["niche"]
        print(f"[{index}/{len(prospects)}] {name}...", flush=True)

        profile = Client(
            slug=slugify(name),
            name=name,
            role=row.get("role", "Founder")
            + (f" at {row['company']}" if row.get("company") else ""),
            niche=niche,
            audience=row.get("audience") or f"buyers and peers in {niche}",
            tone="direct, specific, experienced, sounds like a practitioner not a marketer",
            goal="build authority and attract inbound interest",
        )

        try:
            posts = generator.generate(profile, count=args.count)
        except Exception as exc:  # one bad prospect must not lose the batch
            print(f"    failed: {exc}")
            failed.append(name)
            continue

        page = SAMPLES_DIR / f"{profile.slug}.html"
        page.write_text(build_page(name, niche, posts))
        dm = DM.format(first=name.split()[0], niche=niche, link="<PASTE LINK HERE>")
        entries.append({"name": name, "niche": niche, "file": page.name, "dm": dm})
        time.sleep(0.5)  # stay clear of API rate limits on long batches

    if not entries:
        print("\nNothing generated.")
        return 1

    sheet = SAMPLES_DIR / "worksheet.html"
    sheet.write_text(worksheet(entries))
    followups = SAMPLES_DIR / "followups.txt"
    followups.write_text(
        "\n\n".join(
            f"--- {e['name']} (send 2 days after the first message) ---\n"
            + FOLLOW_UP.format(first=e["name"].split()[0])
            for e in entries
        )
    )

    print(f"\n{len(entries)} sample pages in {SAMPLES_DIR}")
    print(f"Worksheet: {sheet}")
    print(f"Follow-ups: {followups}")
    if failed:
        print(f"Failed ({len(failed)}): {', '.join(failed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
