"""Build the site: copy every page folder and generate index.html and feed.xml.

    python3 scripts/build_site.py _site

A page folder is any top-level folder named <YYYY-MM-DD>-<slug> that holds
index.html and meta.json. Standard library only.
"""
from __future__ import annotations

import html
import json
import re
import shutil
import sys
from email.utils import format_datetime
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://dwudka.github.io/camera-lucida/"
SITE_TITLE = "camera lucida"
TAGLINE = "Charts and write-ups on how Medicare pays for care, made from public data."
DISCLAIMER = "Views are my own and do not represent my employer."
NAME = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9][a-z0-9-]*$")
KINDS = {"long-read": "Long read", "interactive": "Interactive", "post": "Post"}

CSS = """
:root{--ink:#16181B;--graphite:#4A4F57;--muted:#6B7078;--hairline:#D9D4C7;--paper:#FAF7F0;--white:#FFFFFF;--fixative:#0E4F5C;--amber:#BB731B}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font:400 17px/1.55 'IBM Plex Sans',Arial,sans-serif}
main{max-width:720px;margin:0 auto;padding:56px 16px 40px}
.eyebrow{font:500 12px 'IBM Plex Mono',Consolas,monospace;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}
h1{font:300 44px/1.06 'Spectral',Georgia,serif;letter-spacing:-.015em;margin:12px 0 10px}
.deck{color:var(--graphite);max-width:560px;margin:0 0 40px}
ul{list-style:none;margin:0;padding:0}
li{background:var(--white);border:1px solid var(--hairline);border-radius:6px;margin:0 0 16px}
li a{display:block;padding:20px 24px;color:inherit;text-decoration:none}
li a:hover h2,li a:focus h2{color:var(--fixative);text-decoration:underline}
h2{font:400 24px/1.2 'Spectral',Georgia,serif;margin:6px 0 6px}
li p{margin:0;color:var(--graphite)}
.kind{color:var(--amber)}
.empty{color:var(--muted);border-top:1px solid var(--hairline);padding-top:24px}
footer{border-top:1px solid var(--hairline);margin-top:48px;padding-top:16px;display:flex;flex-wrap:wrap;gap:8px 24px;justify-content:space-between;font:400 12px 'IBM Plex Mono',Consolas,monospace;color:var(--muted)}
footer a{color:var(--muted)}
"""
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;600'
         '&family=Spectral:wght@300;400&display=swap" rel="stylesheet">')


def pages(root: Path) -> list[dict]:
    out = []
    for d in sorted(root.iterdir()):
        if d.is_dir() and NAME.match(d.name) and (d / "index.html").exists() and (d / "meta.json").exists():
            meta = json.loads((d / "meta.json").read_text())
            meta["slug"] = d.name
            meta.setdefault("date", d.name[:10])
            meta.setdefault("title", d.name)
            out.append(meta)
    return sorted(out, key=lambda m: (m["date"], m["slug"]), reverse=True)


def _date(iso: str) -> str:
    return datetime.strptime(iso, "%Y-%m-%d").strftime("%b %-d, %Y")


def index_html(items: list[dict]) -> str:
    e = html.escape
    if items:
        rows = "\n".join(
            f'<li><a href="{e(m["slug"])}/"><div class="eyebrow">{e(_date(m["date"]))} · '
            f'<span class="kind">{e(KINDS.get(m.get("kind", ""), "Page"))}</span></div>'
            f'<h2>{e(m["title"])}</h2>' + (f'<p>{e(m["description"])}</p>' if m.get("description") else "") + "</a></li>"
            for m in items)
        body = f"<ul>\n{rows}\n</ul>"
    else:
        body = '<p class="empty">Nothing posted yet. The first few are in progress.</p>'
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{SITE_TITLE}</title>
<meta name="description" content="{e(TAGLINE)}">
<link rel="alternate" type="application/rss+xml" title="{SITE_TITLE}" href="feed.xml">
{FONTS}
<style>{CSS}</style>
</head>
<body>
<main>
<div class="eyebrow">Specimen index</div>
<h1>{SITE_TITLE}</h1>
<p class="deck">{e(TAGLINE)}</p>
{body}
<footer><span>DANNY · <a href="https://www.linkedin.com/in/dwudka/">LinkedIn</a> · <a href="feed.xml">RSS</a></span><span>{DISCLAIMER}</span></footer>
</main>
</body>
</html>
"""


def feed_xml(items: list[dict]) -> str:
    e = html.escape

    def pub(iso: str) -> str:
        return format_datetime(datetime.strptime(iso, "%Y-%m-%d").replace(tzinfo=timezone.utc))

    entries = "\n".join(
        f"<item><title>{e(m['title'])}</title><link>{BASE_URL}{e(m['slug'])}/</link>"
        f"<guid>{BASE_URL}{e(m['slug'])}/</guid><pubDate>{pub(m['date'])}</pubDate>"
        f"<description>{e(m.get('description', ''))}</description></item>"
        for m in items)
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>{SITE_TITLE}</title>'
            f"<link>{BASE_URL}</link><description>{e(TAGLINE)}</description>\n{entries}\n</channel></rss>\n")


def not_found_html() -> str:
    return (f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f"<title>Not found · {SITE_TITLE}</title>{FONTS}<style>{CSS}</style><main><div class=\"eyebrow\">404</div>"
            f'<h1>Page not found</h1><p class="deck">Nothing lives at this address. It may have been taken down. <a href="{BASE_URL}">Back to the index</a>.</p>'
            f"<footer><span>DANNY</span><span>{DISCLAIMER}</span></footer></main></html>\n")


def build(root: Path, out: Path) -> list[dict]:
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    items = pages(root)
    for m in items:
        shutil.copytree(root / m["slug"], out / m["slug"])
    (out / "index.html").write_text(index_html(items))
    (out / "feed.xml").write_text(feed_xml(items))
    (out / "404.html").write_text(not_found_html())
    return items


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    items = build(ROOT, (ROOT / sys.argv[1]).resolve())
    print(f"built {len(items)} page(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
