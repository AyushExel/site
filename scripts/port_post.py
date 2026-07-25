#!/usr/bin/env python3
"""Port an external article (markdown with ---META---/---BODY--- header) into a
site-styled blog post at blog/<slug>/index.html, downloading images locally.

Usage: python3 scripts/port_post.py input.md <slug> [--asset-version N]
Input format:
  ---META---
  title: ...
  date: ...           (original publish date, e.g. "April 10, 2025")
  canonical: URL      (where it was originally published)
  venue: ...          (e.g. "the LanceDB blog", "Towards Data Science")
  ---BODY---
  <markdown>
"""
import html
import pathlib
import re
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent


def parse(src):
    meta_raw, body = src.split("---BODY---", 1)
    meta = {}
    for line in meta_raw.splitlines():
        if ":" in line and not line.startswith("---"):
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, body.strip()


def dl_images(body, outdir):
    outdir.mkdir(parents=True, exist_ok=True)
    n = [0]

    def grab(m):
        cap, url = m.group(1), m.group(2)
        n[0] += 1
        ext = re.sub(r"[?#].*", "", url).rsplit(".", 1)[-1].lower()
        if ext not in ("png", "jpg", "jpeg", "gif", "webp", "svg", "avif"):
            ext = "png"
        fn = f"img/{n[0]:02d}.{ext}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            (outdir / f"{n[0]:02d}.{ext}").write_bytes(urllib.request.urlopen(req, timeout=30).read())
            return f"![{cap}]({fn})"
        except Exception as e:
            print(f"  ! image failed ({e}): {url}", file=sys.stderr)
            return f"![{cap}]({url})"  # keep remote URL as fallback

    return re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)", grab, body)


def inline_md(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    return t


def md_to_html(body):
    out, lines, i = [], body.splitlines(), 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("```"):
            lang, i, buf = ln[3:].strip(), i + 1, []
            while i < len(lines) and not lines[i].startswith("```"):
                buf.append(lines[i]); i += 1
            i += 1
            out.append(f"<pre><code>{html.escape(chr(10).join(buf))}</code></pre>")
        elif m := re.match(r"^(#{1,4}) +(.*)", ln):
            lvl = min(len(m.group(1)) + 1, 4)  # article h2..h4
            out.append(f"<h{lvl}>{inline_md(m.group(2))}</h{lvl}>"); i += 1
        elif m := re.match(r"^!\[([^\]]*)\]\(([^)\s]+)\)\s*$", ln):
            cap = inline_md(m.group(1)) if m.group(1) else ""
            fig = f'<figure><img src="{m.group(2)}" alt="{html.escape(m.group(1))}" loading="lazy">'
            fig += f"<figcaption>{cap}</figcaption>" if cap else ""
            out.append(fig + "</figure>"); i += 1
        elif re.match(r"^\|.*\|\s*$", ln):
            rows = []
            while i < len(lines) and re.match(r"^\|.*\|\s*$", lines[i]):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")]); i += 1
            body_rows = [r for r in rows[1:] if not all(re.match(r"^:?-+:?$", c) for c in r)]
            thead = "".join(f"<th>{inline_md(c)}</th>" for c in rows[0])
            tbody = "".join("<tr>" + "".join(f"<td>{inline_md(c)}</td>" for c in r) + "</tr>" for r in body_rows)
            out.append(f'<div class="tablewrap"><table><thead><tr>{thead}</tr></thead><tbody>{tbody}</tbody></table></div>')
        elif re.match(r"^\s*([-*]|\d+\.) +", ln):
            ordered = bool(re.match(r"^\s*\d+\.", ln)); items = []
            while i < len(lines) and re.match(r"^\s*([-*]|\d+\.) +", lines[i]):
                item = re.sub(r"^\s*([-*]|\d+\.) +", "", lines[i]); i += 1
                while i < len(lines) and re.match(r"^\s{2,}\S", lines[i]) and not re.match(r"^\s*([-*]|\d+\.) +", lines[i]):
                    item += " " + lines[i].strip(); i += 1
                items.append(f"<li>{inline_md(item)}</li>")
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>{''.join(items)}</{tag}>")
        elif ln.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].startswith(">"):
                buf.append(lines[i].lstrip("> ")); i += 1
            out.append(f"<blockquote><p>{inline_md(' '.join(buf))}</p></blockquote>")
        elif re.match(r"^(---+|\*\*\*+)\s*$", ln):
            out.append("<hr>"); i += 1
        elif ln.strip() == "":
            i += 1
        else:
            buf = []
            while i < len(lines) and lines[i].strip() and not re.match(r"^(#{1,4} |```|\||!\[|> |\s*([-*]|\d+\.) |---)", lines[i]):
                buf.append(lines[i].strip()); i += 1
            if not buf:  # unmatched special-prefix line: consume as-is, never stall
                buf.append(lines[i].strip()); i += 1
            out.append(f"<p>{inline_md(' '.join(buf))}</p>")
    return "\n".join(out)


PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} · Ayush Chaurasia</title>
  <meta name="description" content="{title}">
  <link rel="canonical" href="{canonical}">
  <link rel="stylesheet" href="../../assets/style.css?v={ver}">
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 28 28'><circle cx='14' cy='14' r='6.5' fill='none' stroke='%238a94a3' stroke-width='1.4' stroke-dasharray='2 2.4'/><circle cx='14' cy='14' r='11.5' fill='none' stroke='%238a94a3' stroke-width='1.4' stroke-dasharray='2 2.4'/><line x1='14' y1='14' x2='19.5' y2='10.5' stroke='%232b50d8' stroke-width='2.2' stroke-linecap='round'/><line x1='14' y1='14' x2='10' y2='4.5' stroke='%232b50d8' stroke-width='2.2' stroke-linecap='round'/><circle cx='14' cy='14' r='1.6' fill='%232b50d8'/></svg>">
</head>
<body>
<div class="page">

  <nav class="nav">
    <a class="brand" href="../../">Ayush Chaurasia</a>
    <a class="item" href="../../">Home</a>
    <a class="item" href="../../oss/">Open Source</a>
    <a class="item" href="../../publications/">Publications</a>
    <a class="item" href="../">Blog</a>
    <a class="item" href="../../tutorials/">Videos</a>
    <button class="theme-toggle" onclick="toggleTheme()" aria-label="Toggle color theme">◐</button>
  </nav>

  <header class="hero">
    <span class="eyebrow">Blog</span>
    <h1>{title}</h1>
    <div class="byline small-mono">Ayush Chaurasia · {date}</div>
  </header>

  <article class="post-body">
{body}
  </article>

  <footer class="site">
    <span>© <span id="y"></span> Ayush Chaurasia</span>
    <span><a href="../">← all posts</a></span>
  </footer>

</div>
<script src="../../assets/site.js?v={ver}"></script>
<script>document.getElementById("y").textContent = new Date().getFullYear();</script>
</body>
</html>
"""


def main():
    src_path, slug = sys.argv[1], sys.argv[2]
    ver = sys.argv[4] if len(sys.argv) > 4 and sys.argv[3] == "--asset-version" else "11"
    meta, body = parse(pathlib.Path(src_path).read_text())
    outdir = ROOT / "blog" / slug
    body = dl_images(body, outdir / "img")
    page = PAGE.format(
        title=html.escape(meta["title"], quote=False), date=meta.get("date", ""),
        canonical=meta.get("canonical", "#"), venue=meta.get("venue", "the original site"),
        ver=ver, body=md_to_html(body),
    )
    (outdir / "index.html").write_text(page)
    print(f"wrote blog/{slug}/index.html ({len(page)} bytes)")


if __name__ == "__main__":
    main()
