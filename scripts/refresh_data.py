#!/usr/bin/env python3
"""Refresh data/committer_to.json from the GitHub API.

Aggregates merged PRs authored by USER across all repos, fetches star counts,
and writes the JSON the landing page renders. Run locally or via the weekly
GitHub Action (which has GITHUB_TOKEN for higher rate limits).

Google Scholar has no API and blocks automated scraping, so data/scholar.json
is maintained manually — update the numbers there when they change.
"""
import json
import os
import time
import urllib.request
from collections import Counter
from datetime import date
from pathlib import Path

USER = "AyushExel"
ROOT = Path(__file__).resolve().parent.parent
TOKEN = os.environ.get("GITHUB_TOKEN", "")


def api(url):
    headers = {"Accept": "application/vnd.github+json"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers)) as r:
        return json.load(r)


def main():
    # 1) aggregate merged PRs by repo (search API caps at 1000 results)
    counts = Counter()
    for page in range(1, 11):
        d = api(
            f"https://api.github.com/search/issues"
            f"?q=author:{USER}+type:pr+is:merged&per_page=100&page={page}"
        )
        items = d.get("items", [])
        for it in items:
            counts["/".join(it["repository_url"].split("/")[-2:])] += 1
        if len(items) < 100:
            break
        time.sleep(3 if TOKEN else 8)  # search rate limit

    # 2) star counts for external repos (own repos belong in "co-created", not here)
    # preserve hand-written "contrib" blurbs across refreshes
    path = ROOT / "data" / "committer_to.json"
    old = {r["repo"]: r for r in json.loads(path.read_text())} if path.exists() else {}
    out = []
    external = [r for r in counts if not r.startswith(f"{USER}/")]
    for full in sorted(external, key=counts.get, reverse=True):
        try:
            d = api(f"https://api.github.com/repos/{full}")
        except Exception as e:  # repo renamed/deleted — skip
            print(f"skip {full}: {e}")
            continue
        entry = {
            "repo": full,
            "stars": d["stargazers_count"],
            "desc": (d["description"] or "")[:140],
            "lang": d.get("language"),
            "prs": counts[full],
            "url": d["html_url"],
        }
        if full in old and old[full].get("contrib"):
            entry["contrib"] = old[full]["contrib"]
        out.append(entry)
        time.sleep(0.2 if TOKEN else 1)

    out.sort(key=lambda x: -x["stars"])
    path.write_text(json.dumps(out, indent=1) + "\n")
    print(f"wrote {path} ({len(out)} repos, {sum(counts.values())} merged PRs, {date.today()})")


if __name__ == "__main__":
    main()
