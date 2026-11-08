import urllib.parse
# -*- coding: utf-8 -*-
"""Free, keyless daily income-radar refresh. Runs inside GitHub Actions."""
import json, urllib.request, urllib.error, datetime, io

QUERIES = [
    "side project revenue",
    "indie hacker MRR",
    "micro saas",
    "passive income automation",
]
HITS = []
for q in QUERIES:
    url = ("https://hn.algolia.com/api/v1/search_by_date?query="
           + urllib.parse.quote(q) + "&tags=story&hitsPerPage=8")
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            d = json.load(r)
        for h in d.get("hits", []):
            HITS.append({
                "title": (h.get("title") or "").strip(),
                "url": h.get("url") or ("https://news.ycombinator.com/item?id=" + str(h.get("objectID"))),
                "points": h.get("points") or 0,
                "date": (h.get("created_at") or "")[:10],
                "q": q,
            })
    except Exception as e:
        HITS.append({"title": "[fetch failed: " + q + "]", "url": "", "points": 0, "date": "", "q": q})

seen = set()
uniq = []
for h in HITS:
    if h["title"] and h["title"] not in seen:
        seen.add(h["title"])
        uniq.append(h)
uniq.sort(key=lambda x: -x["points"])

today = datetime.date.today().isoformat()
out = io.StringIO()
out.write("# Daily Income Radar - " + today + "\n\n")
out.write("Auto-generated from free public APIs (Hacker News Algolia). Zero cost, no keys.\n\n")
out.write("## Screening rules (all five must pass)\n")
out.write("1. Agent independently produces >=70% of the deliverable\n")
out.write("2. First SKU listable within 14 days\n")
out.write("3. Subscription / per-use / per-call revenue, not one-off\n")
out.write("4. Marketplace with built-in traffic and payouts preferred\n")
out.write("5. Compliance risk stays off the operator\n\n")
out.write("## Rejected by default\n")
out.write("AI content farms, Etsy bulk AI, KDP AI books, C-end Skill retail, ")
out.write("large enterprise custom builds, AI bug bounty, pure affiliate.\n\n")
out.write("## Latest signals (" + str(len(uniq)) + ")\n\n")
for h in uniq[:30]:
    out.write("- [%s](%s) - %s pts - %s - query: %s\n" % (
        h["title"].replace("|", "/"), h["url"], h["points"], h["date"], h["q"]))
out.write("\n---\n*Only signals, not verified revenue. Verify before acting.*\n")

with open("OPPORTUNITIES.md", "w", encoding="utf-8") as f:
    f.write(out.getvalue())
print("wrote OPPORTUNITIES.md with", len(uniq), "signals")
