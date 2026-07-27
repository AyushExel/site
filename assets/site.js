/* Shared site behavior: theme toggle + data-driven sections. */

(function themeInit() {
  const MODES = ["light", "dark", "funky"];
  const GLYPH = { light: "◐", dark: "◑", funky: "✿" };
  const saved = localStorage.getItem("theme");
  if (MODES.includes(saved)) {
    document.documentElement.setAttribute("data-theme", saved);
  }
  function paintButtons(mode) {
    document.querySelectorAll(".theme-toggle").forEach(b => { b.textContent = GLYPH[mode]; });
  }
  function currentMode() {
    return (
      document.documentElement.getAttribute("data-theme") ||
      (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light")
    );
  }
  window.toggleTheme = function () {
    const next = MODES[(MODES.indexOf(currentMode()) + 1) % MODES.length];
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("theme", next);
    paintButtons(next);
  };
  addEventListener("DOMContentLoaded", () => paintButtons(currentMode()));
})();

const fmt = (n) =>
  n >= 1000 ? (n / 1000).toFixed(n >= 10000 ? 0 : 1) + "k" : String(n);

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
