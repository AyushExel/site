# ayushexel/site

Personal website — pure static files, no framework, no build step. Hosted on GitHub Pages
at **https://batchnorm.com/** (custom domain on this repo; `ayushexel.github.io/site` redirects).

```
index.html               home: intro, highlights, side quests, what I'm working on
oss/index.html           open source: co-created (live ★ from GitHub API) + contributions
publications/index.html  papers (Scholar data), in-progress, blog posts, talks
blog/
  index.html             blog listing
  <slug>/index.html      one folder per post (images in <slug>/img/)
tutorials/index.html     videos page (playable lite YouTube embeds)
assets/style.css         the entire design system (tokens, light/dark, components)
assets/site.js           theme toggle + video renderer
data/committer_to.json   OSS contributions — AUTO-refreshed weekly by GitHub Action;
                         hand-written "contrib" blurbs are preserved across refreshes
data/cocreated.json      co-created projects — edit by hand
data/scholar.json        Google Scholar numbers — edit by hand (see below)
data/videos.json         video list — edit by hand
scripts/refresh_data.py  regenerates committer_to.json from the GitHub API
scripts/port_post.py     ports an external article into a site-styled blog post
.github/workflows/       the weekly refresh Action (Mondays 06:17 UTC + manual runs)
```

Width system: listing pages use `.page-wide` (66rem); article pages use `.page`
(50rem reading measure). Every page is one or the other.

---

## ⚠️ The one rule: bump `?v=` when you change assets or data

GitHub Pages caches everything for 10 minutes. If you edit `style.css`, `site.js`, or any
`data/*.json`, visitors can get **new HTML with old CSS/data** (broken layout or stale
numbers) for up to 10 minutes — we've been bitten by this twice.

The fix baked into the site: every asset link and every `fetch()` carries a version query
(`style.css?v=9`, `scholar.json?v=9`, …). **After editing any CSS/JS/JSON, bump the number
everywhere in one go:**

```bash
sed -i '' 's/?v=9/?v=10/g' index.html blog/index.html tutorials/index.html blog/*/index.html
```

(Adjust the old/new numbers. New blog posts you create should use the current version.)
Editing only HTML text needs no bump.

---

## Adding a blog post

Each post is a folder under `blog/` with a single `index.html`.

1. **Copy the template post:**
   ```bash
   cp -r blog/rope-prior-art blog/my-new-post
   ```
2. **Edit `blog/my-new-post/index.html`:**
   - `<title>` and `<meta name="description">` in the head.
   - Everything inside `<div class="page">` below the `<nav>`: the header block
     (eyebrow / `<h1>` / dek / byline) and the article sections.
   - Keep the `<nav>` and the `<link rel="stylesheet" href="../../assets/style.css?v=N">`
     as they are (relative paths matter: posts sit two levels deep).
   - Post-specific styles live in the inline `<style>` block — the template already has
     styled components for displayed math (`.math`, `.mtx`), code blocks (`pre`, with
     `.cm` comment / `.kw` keyword spans), tables, pull quotes, and the claim-scoreboard
     cards. Delete what you don't need.
3. **List the post in two places:**
   - `blog/index.html` — add a `.card.post` entry (date, linked title, one-paragraph teaser).
   - `publications/index.html` — add a matching card under "Blog posts".
4. Commit and push. Done — no build step.

**Porting an article from elsewhere** (Medium, etc.): write a markdown file with a
`---META---` header (title/date/venue/canonical) and `---BODY---` content, then
`python3 scripts/port_post.py input.md <slug>`. It downloads images locally and emits the
styled page. For scraper-walled sources (Medium 403s bots), save the page from a logged-in
browser as "Webpage, Complete" — text, images, and even embedded gists are recoverable
from the saved folder (see git history of blog/comparing-hyperparameter-tuning-methods).

Writing tip: the design is calibrated for long-form technical writing — displayed equations
in `.math` blocks, real code in `pre` with muted comments, tables inside
`<div class="tablewrap">` so wide content scrolls without breaking the page.

## Adding / editing videos

Append to `data/videos.json`:

```json
{ "title": "My new talk", "url": "https://www.youtube.com/watch?v=VIDEO_ID", "tag": "RAG" }
```

The tutorials page automatically renders the YouTube thumbnail with a play button and swaps
in the real player on click — any `watch?v=` or `youtu.be/` URL works. `tag` is the small
topic pill (keep it to 1–3 words). Order in the file = order on the page. Bump `?v=`.

## Editing co-created projects

`data/cocreated.json` — one object per card:

```json
{
  "name": "Project", "url": "https://github.com/org/repo", "stars": "10.8k",
  "role": "co-author",
  "desc": "One or two sentences; the card clamps to 2 lines (full text on hover).",
  "paper": { "label": "arXiv:XXXX.XXXXX", "url": "https://arxiv.org/abs/..." }
}
```

`stars` is a display string (update it occasionally by hand); `paper` may be `null`.
Bump `?v=`.

## Updating Google Scholar numbers

Scholar has **no API and blocks all scripted access** (CAPTCHA), so this is deliberately
manual — takes about a minute:

1. Open your profile in a logged-in browser:
   https://scholar.google.com/citations?user=4XbcwOAAAAAJ&hl=en
2. Read the numbers from the sidebar table (Citations / h-index / i10-index, "All" column).
3. Edit `data/scholar.json`: update `citations`, `h_index`, `i10_index`, per-paper
   `citations` if they've moved, and set `updated` to today's date (shown on the site as
   "as read on …").
4. Bump `?v=` and push.

The publications list is curated by hand because Scholar splits the YOLO software citation
across ~20 duplicate variants — list only the distinct entries; the header totals cover all.

## OSS contribution stats (auto)

`data/committer_to.json` is regenerated **every Monday** by the `refresh-data` Action
(also runnable on demand: repo → Actions → "Refresh site data" → Run workflow). It
re-aggregates merged PRs by repo and refreshes star counts.

The per-repo one-liners (`"contrib"` fields — "what this contribution actually added")
are **hand-written and preserved across refreshes**. To add one for a new repo, add
`"contrib": "..."` to its entry; to reword, just edit it. Rows without `contrib` fall
back to showing the PR count. The section's summary line ("N+ merged PRs across M
repositories…") is computed from this file at render time.

## Design system

Everything visual lives in `assets/style.css`, driven by CSS custom properties at the top
(`--ground`, `--ink`, `--accent`, …) defined three times: light default, `@media
(prefers-color-scheme: dark)`, and explicit `[data-theme]` overrides for the toggle.
**Change a color once in the tokens, all three blocks.** Type is system-stack: Iowan Old
Style/Palatino serif for text, SF Mono for labels and numbers. The rotating phase-plane
brandmark (nav) and the blog's header figure are the site's identity motif — RoPE frequency
planes, a nod to the first post.

## Local preview

```bash
cd site && python3 -m http.server 8000
# open http://localhost:8000  — data fetches need a server; file:// won't work
```

## Deploys

Push to `main` → Pages redeploys automatically (usually ~1 min, occasionally up to 10).
Check status: repo → Settings → Pages, or
`gh api repos/AyushExel/site/pages/builds/latest`. Remember the 10-minute edge cache when
verifying: `curl -s "https://ayushexel.github.io/site/?x=$RANDOM"` bypasses it.
