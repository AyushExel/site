# ayushexel/site

Personal website — static, no framework, hosted on GitHub Pages.

## Structure

```
index.html               landing: intro, committer-to, co-created, scholar stats
blog/                    blog index + posts (each post is a folder with index.html)
tutorials/               tutorials & videos page
assets/style.css         the design system (tokens, light/dark theming)
assets/site.js           theme toggle + JSON-driven section renderers
data/committer_to.json   repos contributed to (auto-refreshed weekly by Action)
data/cocreated.json      curated projects — edit by hand to add/remove
data/scholar.json        Google Scholar stats — edit by hand (Scholar has no API)
data/videos.json         curated video list — edit by hand
scripts/refresh_data.py  regenerates committer_to.json from the GitHub API
```

## Editing content

- **New blog post**: copy `blog/rope-prior-art/` as a template, edit, then add a card
  to `blog/index.html` and the "Latest writing" section of `index.html`.
- **Add a video**: append `{ "title": ..., "url": ..., "tag": ... }` to `data/videos.json`.
- **Add a co-created project**: append to `data/cocreated.json`.
- **Scholar numbers drifted**: update `data/scholar.json` (citations, h-index, per-paper counts).

## Hosting

Settings → Pages → Deploy from branch → `main` / root. The site is pure static files;
no build step. The weekly `refresh-data` Action keeps contribution stats current.
