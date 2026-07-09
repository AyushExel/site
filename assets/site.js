/* Shared site behavior: theme toggle + data-driven sections. */

(function themeInit() {
  const saved = localStorage.getItem("theme");
  if (saved === "light" || saved === "dark") {
    document.documentElement.setAttribute("data-theme", saved);
  }
  window.toggleTheme = function () {
    const root = document.documentElement;
    const current =
      root.getAttribute("data-theme") ||
      (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    const next = current === "dark" ? "light" : "dark";
    root.setAttribute("data-theme", next);
    localStorage.setItem("theme", next);
  };
})();

const fmt = (n) =>
  n >= 1000 ? (n / 1000).toFixed(n >= 10000 ? 0 : 1) + "k" : String(n);

/* "Committer to" — renders data/committer_to.json (refreshed by GitHub Action).
   Top N visible; the rest collapse behind a <details>. */
async function renderCommitterTo(mountId, dataUrl, visibleCount = 6) {
  const mount = document.getElementById(mountId);
  if (!mount) return;
  let repos;
  try {
    repos = await (await fetch(dataUrl)).json();
  } catch {
    mount.innerHTML = '<p class="small-mono">Could not load repository data.</p>';
    return;
  }
  repos.sort((a, b) => b.stars - a.stars);
  const row = (r) => `
    <div class="card repo">
      <span class="name"><a href="${r.url}">${r.repo}</a></span>
      <span class="desc">${r.desc || ""}</span>
      <span class="stats"><span class="stars">★ ${fmt(r.stars)}</span> · ${r.prs} PR${r.prs > 1 ? "s" : ""}</span>
    </div>`;
  const head = repos.slice(0, visibleCount).map(row).join("");
  const tail = repos.slice(visibleCount).map(row).join("");
  mount.innerHTML =
    `<div class="stack">${head}</div>` +
    (tail
      ? `<details class="more"><summary>${repos.length - visibleCount} more repositories</summary><div class="stack">${tail}</div></details>`
      : "");
}

/* Google Scholar — renders data/scholar.json (no public API; refreshed by script/manually). */
async function renderScholar(mountId, dataUrl) {
  const mount = document.getElementById(mountId);
  if (!mount) return;
  let s;
  try {
    s = await (await fetch(dataUrl)).json();
  } catch {
    mount.innerHTML = "";
    return;
  }
  const stat = (n, k) =>
    n == null ? "" : `<div class="card stat"><div class="n">${fmt(n)}</div><span class="k">${k}</span></div>`;
  const pubs = (s.publications || [])
    .map(
      (p) => `
    <div class="card pub">
      <span class="title"><a href="${p.url}">${p.title}</a><br><span class="venue">${p.venue || ""}${p.year ? " · " + p.year : ""}</span></span>
      ${p.citations != null ? `<span class="cites">${fmt(p.citations)} citations</span>` : ""}
    </div>`
    )
    .join("");
  mount.innerHTML = `
    <div class="stats-row">
      ${stat(s.citations, "citations")}
      ${stat(s.h_index, "h-index")}
      ${stat(s.i10_index, "i10-index")}
    </div>
    ${pubs ? `<div class="stack pubs">${pubs}</div>` : ""}
    <p class="small-mono" style="margin-top:0.8rem">Source: <a href="${s.profile_url}">Google Scholar</a> · updated ${s.updated}</p>`;
}

/* Videos — renders data/videos.json as lite YouTube embeds:
   thumbnail + play button; clicking swaps in the real player (fast page load,
   playable in place). Falls back to a plain link card if no video id. */
function ytId(url) {
  const m = url.match(/[?&]v=([\w-]{6,})/) || url.match(/youtu\.be\/([\w-]{6,})/);
  return m ? m[1] : null;
}
function playVideo(el, id) {
  el.outerHTML = `<iframe class="ytframe" src="https://www.youtube.com/embed/${id}?autoplay=1"
    title="YouTube video" frameborder="0" allowfullscreen
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe>`;
}
async function renderVideos(mountId, dataUrl) {
  const mount = document.getElementById(mountId);
  if (!mount) return;
  let vids;
  try {
    vids = await (await fetch(dataUrl)).json();
  } catch {
    mount.innerHTML = "";
    return;
  }
  mount.innerHTML = `<div class="grid-2">${vids
    .map((v) => {
      const id = ytId(v.url);
      const thumb = id
        ? `<button class="thumb" onclick="playVideo(this, '${id}')" aria-label="Play: ${v.title.replace(/"/g, "&quot;")}">
             <img src="https://i.ytimg.com/vi/${id}/hqdefault.jpg" alt="" loading="lazy">
             <span class="playbtn" aria-hidden="true">▶</span>
           </button>`
        : "";
      return `
    <div class="card vidcard">
      ${thumb}
      <div class="vidbody">
        <span class="title"><a href="${v.url}">${v.title}</a></span>
        <span class="tag">${v.tag || "video"}</span>
      </div>
    </div>`;
    })
    .join("")}</div>`;
}
