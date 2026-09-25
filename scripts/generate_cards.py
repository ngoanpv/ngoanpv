"""Regenerates the live cards in assets/generated/ (run daily by GitHub Actions).

  * apps-{dark,light}.svg     – every app on the App Store, icons embedded, pulled
                                 from Apple's public iTunes lookup API
  * stats-{dark,light}.svg    – followers, repos, contributions, top languages
  * repo-<name>-{mode}.svg    – cards for the open-source projects in PROJECTS

No third-party stats service is involved, so nothing gets rate-limited.
Every network call has an offline fallback, so the script never leaves the
README with broken images: if a call fails the last good data is reused.

Env:  GITHUB_TOKEN (Actions provides it)  ·  GH_LOGIN (default: ngoanpv)
Run locally with --offline to render from the fallback data only.
"""
import base64
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from theme import MONO, SANS, SERIF, THEMES, calm_sequence, esc, svg_open  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "generated"
CACHE = OUT / "data.json"
LOGIN = os.environ.get("GH_LOGIN", "ngoanpv")
OFFLINE = "--offline" in sys.argv

# ------------------------------------------------------------------ config
APPSTORE_DEVELOPER_ID = 1711897094
APPSTORE_COUNTRY = "vn"
# Apple's developer lookup sometimes omits newer / Mac apps, so list them too.
APPSTORE_EXTRA_IDS = [6761550597, 6768528910, 6791887642]

# Short display names, one-line pitches and a tag. Anything not listed here
# falls back to the App Store name + first sentence of the description,
# so a brand-new app shows up automatically.
APP_COPY = {
    6791887642: ("Mochi", "A tiny pixel pet for your Mac", "macOS"),
    6768528910: ("Mochiba", "Clock-in that feels like a friend", "Productivity"),
    6761550597: ("HyperLens", "Perp PnL & alerts, in real time", "Finance"),
    6761322457: ("Narabi", "Japanese words as a zen puzzle", "Education"),
    6759525787: ("MojiZen", "Find the links between emojis", "Puzzle game"),
    6759248526: ("Dhammapada", "423 verses, calm and practical", "Reference · Watch"),
    6759195225: ("Shiba Island", "Habits with a Shiba companion", "Habits"),
    6758035029: ("Lô Tô AI", "Vietnamese Lô Tô, AI caller", "Party game"),
    6757269201: ("AI Đu Đỉnh", "Stocks + a roasting AI coach", "Finance"),
}

PROJECTS = ["DeepInterview", "llama2_vietnamese", "albert_vi", "zaloqa2019"]

FALLBACK = {
    "apps": [
        {"id": i, "name": n, "icon": None, "rating": r, "count": k, "released": d}
        for i, n, r, k, d in [
            (6791887642, "Mochi — Desk Companion", 0, 0, "2026-09-01"),
            (6768528910, "Mochiba", 0, 0, "2026-07-01"),
            (6761550597, "HyperLens · Perp PnL Tracker", 0, 0, "2026-04-01"),
            (6761322457, "Narabi: Learn Japanese Words", 5, 1, "2026-04-01"),
            (6759525787, "MojiZen: Emoji Connections", 5, 1, "2026-03-01"),
            (6759248526, "Dhammapada: Buddha Teachings", 5, 14, "2026-02-01"),
            (6759195225, "Shiba Island: Habit Tracker", 0, 0, "2026-02-01"),
            (6758035029, "Lô Tô AI - Số Zì Đây?", 5, 2, "2026-01-01"),
            (6757269201, "AI Đu Đỉnh", 5, 7, "2025-12-01"),
        ]
    ],
    "stats": {
        "stars": 639, "followers": 78, "repos": 67, "contributions": 0,
        "languages": [],  # filled in on the first Actions run
    },
    "repos": {
        "DeepInterview": {"desc": "Open-source, voice-first AI mock interviewer. Upload your CV + a job description and practice out loud.", "lang": "Python", "color": "#3572A5", "stars": 17, "forks": 5},
        "llama2_vietnamese": {"desc": "A fine-tuned Large Language Model for the Vietnamese language based on Llama 2", "lang": "Python", "color": "#3572A5", "stars": 18, "forks": 3},
        "albert_vi": {"desc": "ALBERT for Vietnamese", "lang": "Python", "color": "#3572A5", "stars": 95, "forks": 40},
        "zaloqa2019": {"desc": "1st place solution for Zalo AI 2019 - Vietnamese Wiki Question Answering", "lang": "Python", "color": "#3572A5", "stars": 47, "forks": 15},
    },
}


# ------------------------------------------------------------------ fetching
def http(url, data=None, headers=None, raw=False):
    req = urllib.request.Request(url, data=data, headers={"User-Agent": f"{LOGIN}-profile", **(headers or {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        body = r.read()
    return body if raw else json.loads(body)


def fetch_apps():
    q = f"https://itunes.apple.com/lookup?id={APPSTORE_DEVELOPER_ID}&entity=software,macSoftware&country={APPSTORE_COUNTRY}&limit=200"
    results = http(q)["results"]
    ids = ",".join(map(str, APPSTORE_EXTRA_IDS))
    if ids:
        results += http(f"https://itunes.apple.com/lookup?id={ids}&country={APPSTORE_COUNTRY}")["results"]
    apps, seen = [], set()
    for r in results:
        if r.get("wrapperType") != "software" or r["trackId"] in seen:
            continue
        seen.add(r["trackId"])
        icon = None
        art = r.get("artworkUrl512") or r.get("artworkUrl100")
        if art:
            art = re.sub(r"/\d+x\d+bb\.(jpg|png)$", "/144x144bb.jpg", art)
            try:
                icon = base64.b64encode(http(art, raw=True)).decode()
            except Exception as e:  # keep going without this icon
                print("icon failed", r["trackId"], e)
        apps.append({
            "id": r["trackId"], "name": r["trackName"], "icon": icon,
            "rating": r.get("averageUserRating") or 0, "count": r.get("userRatingCount") or 0,
            "released": (r.get("releaseDate") or "")[:10], "genre": r.get("primaryGenreName", ""),
            "blurb": (r.get("description") or "").split("\n")[0],
        })
    return apps


GQL = """query($login:String!, $after:String){ user(login:$login){
  followers{totalCount}
  contributionsCollection{ contributionCalendar{ totalContributions } }
  repositories(ownerAffiliations:OWNER, privacy:PUBLIC, first:100, after:$after){
    totalCount pageInfo{hasNextPage endCursor}
    nodes{ name isFork description stargazerCount forkCount
      primaryLanguage{name color}
      languages(first:10, orderBy:{field:SIZE, direction:DESC}){ edges{ size node{name color} } } } } } }"""


def fetch_github():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GITHUB_TOKEN not set")
    after, repos, user = None, [], None
    while True:
        body = json.dumps({"query": GQL, "variables": {"login": LOGIN, "after": after}}).encode()
        res = http("https://api.github.com/graphql", data=body,
                   headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"})
        if "errors" in res:
            raise RuntimeError(res["errors"])
        user = res["data"]["user"]
        repos += user["repositories"]["nodes"]
        page = user["repositories"]["pageInfo"]
        if not page["hasNextPage"]:
            break
        after = page["endCursor"]
    own = [r for r in repos if not r["isFork"]]
    langs = {}
    for r in own:
        for e in r["languages"]["edges"]:
            n = e["node"]["name"]
            langs.setdefault(n, [e["node"]["color"] or "#8b949e", 0])
            langs[n][1] += e["size"]
    total = sum(v[1] for v in langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: -kv[1][1])[:5]
    lang_list = [[n, c, round(s / total * 100, 1)] for n, (c, s) in top]
    rest = round(100 - sum(x[2] for x in lang_list), 1)
    if rest > 0.5:
        lang_list.append(["Other", "#8b949e", rest])
    stats = {
        "stars": sum(r["stargazerCount"] for r in repos),
        "followers": user["followers"]["totalCount"],
        "repos": user["repositories"]["totalCount"],
        "contributions": user["contributionsCollection"]["contributionCalendar"]["totalContributions"],
        "languages": lang_list,
    }
    by_name = {r["name"]: r for r in repos}
    repo_cards = {}
    for name in PROJECTS:
        r = by_name.get(name)
        if r:
            pl = r["primaryLanguage"] or {"name": "", "color": "#8b949e"}
            repo_cards[name] = {"desc": r["description"] or "", "lang": pl["name"], "color": pl["color"] or "#8b949e",
                                "stars": r["stargazerCount"], "forks": r["forkCount"]}
    return stats, repo_cards


# ------------------------------------------------------------------ helpers
def fit(text, max_chars):
    text = text.strip()
    return text if len(text) <= max_chars else text[: max_chars - 1].rstrip(" ,.-—") + "…"


def wrap(text, width, lines):
    words, out, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + (1 if cur else 0) <= width:
            cur = f"{cur} {w}".strip()
        else:
            out.append(cur)
            cur = w
            if len(out) == lines:
                break
    if len(out) < lines and cur:
        out.append(cur)
    if len(out) == lines and " ".join(out) != " ".join(words):
        out[-1] = fit(out[-1] + " …", width)
    return out


def fade_in(delay, dur=0.6, rise=10):
    """Kept for compatibility: cards are static so they always render, even
    where an image's animation timeline never starts (e.g. lazy-loaded)."""
    return ""


# ------------------------------------------------------------------ apps shelf
def apps_svg(apps, mode):
    c = THEMES[mode]
    cols, cw, ch, gap = 3, 322, 104, 17
    rows = (len(apps) + cols - 1) // cols
    W, H = 1000, rows * ch + (rows - 1) * gap + 2
    newest = max((a["released"] for a in apps), default="")
    s = [svg_open(W, H, f"{len(apps)} apps shipped on the App Store")]
    s.append(
        "<defs>"
        + "".join(f'<clipPath id="ic{i}"><rect x="16" y="16" width="72" height="72" rx="17"/></clipPath>' for i in range(len(apps)))
        + '<linearGradient id="sheen" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
        '<stop offset="0.5" stop-color="#fff" stop-opacity="0.3"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
        "</defs>"
    )
    tile_cols = calm_sequence(c)[:5]
    for i, a in enumerate(apps):
        name, pitch, tag = APP_COPY.get(a["id"], (None, None, None))
        name = fit(name or re.split(r"[:·—-]", a["name"])[0], 22)
        pitch = fit(pitch or a.get("blurb", ""), 34)
        tag = tag or a.get("genre", "")
        x = (i % cols) * (cw + gap)
        y = (i // cols) * (ch + gap)
        s.append(f'<g transform="translate({x},{y})"><g>')
        s.append(f'<rect x="0.5" y="0.5" width="{cw-1}" height="{ch-1}" rx="16" fill="{c["panel"]}" stroke="{c["border"]}"/>')
        # icon (floats gently, sheen sweeps across every few seconds)
        s.append(f'<g><animateTransform attributeName="transform" type="translate" values="0 0;0 -2;0 0" dur="7s" begin="{i*0.45:.2f}s" repeatCount="indefinite"/>')
        if a.get("icon"):
            s.append(f'<image href="data:image/jpeg;base64,{a["icon"]}" x="16" y="16" width="72" height="72" clip-path="url(#ic{i})" preserveAspectRatio="xMidYMid slice"/>')
        else:
            col = tile_cols[i % len(tile_cols)]
            s.append(
                f'<rect x="16" y="16" width="72" height="72" rx="17" fill="{col}" fill-opacity="0.9"/>'
                f'<text x="52" y="63" text-anchor="middle" font-family="{SERIF}" font-size="34" font-weight="600" fill="{c["bg"]}">{esc(name[:1])}</text>'
            )
        s.append(
            f'<g clip-path="url(#ic{i})"><rect x="-60" y="10" width="40" height="90" fill="url(#sheen)" transform="skewX(-20)">'
            f'<animate attributeName="x" values="-60;-60;150" keyTimes="0;0.85;1" dur="10s" begin="{i*0.6:.1f}s" repeatCount="indefinite"/></rect></g>'
            f'<rect x="16.5" y="16.5" width="71" height="71" rx="16.5" fill="none" stroke="{c["text"]}" stroke-opacity="0.08"/>'
        )
        s.append("</g>")
        s.append(
            f'<text x="104" y="40" font-family="{SERIF}" font-size="19" font-weight="600" fill="{c["text"]}">{esc(name)}</text>'
            f'<text x="104" y="61" font-family="{SANS}" font-size="12.5" fill="{c["muted"]}">{esc(pitch)}</text>'
        )
        tw = int(len(tag) * 6.4 + 18)
        s.append(
            f'<rect x="104.5" y="72.5" width="{tw}" height="19" rx="9.5" fill="none" stroke="{c["faint"]}"/>'
            f'<text x="{104 + tw/2}" y="86" text-anchor="middle" font-family="{SANS}" font-size="11" fill="{c["muted"]}">{esc(tag)}</text>'
        )
        if a.get("count"):
            s.append(
                f'<text x="{104 + tw + 10}" y="86" font-family="{SANS}" font-size="11.5" font-weight="600" fill="{c["amber"]}">★ {a["rating"]:.1f}'
                f'<tspan fill="{c["muted"]}" font-weight="400"> ({a["count"]})</tspan></text>'
            )
        if a["released"] and a["released"] == newest:
            s.append(
                f'<g><rect x="{cw-58.5}" y="12.5" width="44" height="19" rx="9.5" fill="none" stroke="{c["pink"]}"/>'
                f'<text x="{cw-36}" y="26" text-anchor="middle" font-family="{SANS}" font-size="10.5" font-weight="600" letter-spacing="1" fill="{c["pink"]}">NEW</text>'
                f'<animate attributeName="opacity" values="1;0.5;1" dur="5s" repeatCount="indefinite"/></g>'
            )
        s.append(f"{fade_in(0.15 + i * 0.12)}</g></g>")
    s.append("</svg>")
    return "".join(s)


# ------------------------------------------------------------------ stats card
def stats_svg(st, mode):
    c = THEMES[mode]
    W, H = 1000, 170
    s = [svg_open(W, H, f"GitHub stats: {st['followers']} followers, {st['repos']} public repos")]
    s.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="16" fill="{c["panel"]}" stroke="{c["border"]}"/>')
    items = [
        ("○", st["followers"], "followers", c["muted"]),
        ("○", st["repos"], "public repos", c["muted"]),
        ("○", st["contributions"], "contributions", c["muted"]),
    ]
    for i, (ico, val, lab, col) in enumerate(items):
        x = 40 + i * 160
        s.append(
            f'<g>'
            f'<text x="{x}" y="96" font-family="{SERIF}" font-size="36" font-weight="600" fill="{c["text"]}">{f"{val:,}" if val else "—"}</text>'
            f'<text x="{x}" y="120" font-family="{SANS}" font-size="12" fill="{c["muted"]}">{esc(lab)}</text>'
            f"{fade_in(0.1 + i * 0.15)}</g>"
        )
    # languages
    lx, lw = 560, 408
    s.append(f'<line x1="530" y1="32" x2="530" y2="{H-32}" stroke="{c["border"]}"/>')
    s.append(f'<text x="{lx}" y="50" font-family="{SERIF}" font-size="17" font-weight="600" fill="{c["text"]}">Most used languages</text>')
    s.append(f'<clipPath id="lb"><rect x="{lx}" y="66" width="{lw}" height="10" rx="5"/></clipPath>')
    s.append(f'<rect x="{lx}" y="66" width="{lw}" height="10" rx="5" fill="{c["faint"]}" opacity="0.4"/>')
    s.append('<g clip-path="url(#lb)">')
    seq = calm_sequence(c)
    st = dict(st, languages=[[n, seq[i % len(seq)], p] for i, (n, _c, p) in enumerate(st["languages"])])
    x = lx
    for i, (name, col, pct) in enumerate(st["languages"]):
        w = lw * pct / 100
        s.append(
            f'<rect x="{x:.1f}" y="66" height="10" width="{w:.1f}" fill="{col}"/>'
        )
        x += w
    s.append("</g>")
    if not st["languages"]:
        s.append(f'<text x="{lx}" y="110" font-family="{SANS}" font-size="12.5" fill="{c["muted"]}">Syncing on the first GitHub Actions run…</text>')
    for i, (name, col, pct) in enumerate(st["languages"][:6]):
        gx = lx + (i % 3) * 136
        gy = 106 + (i // 3) * 26
        s.append(
            f'<g><circle cx="{gx+5}" cy="{gy-4}" r="5" fill="{col}"/>'
            f'<text x="{gx+16}" y="{gy}" font-family="{SANS}" font-size="12.5" fill="{c["text"]}">{esc(fit(name, 12))} '
            f'<tspan fill="{c["muted"]}">{pct:g}%</tspan></text>{fade_in(0.6 + i * 0.1, rise=4)}</g>'
        )
    s.append("</svg>")
    return "".join(s)


# ------------------------------------------------------------------ repo card
def repo_svg(name, r, mode):
    c = THEMES[mode]
    W, H = 490, 132
    s = [svg_open(W, H, f"{name}: {r['desc']}")]
    s.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="14" fill="{c["panel"]}" stroke="{c["border"]}"/>')
    s.append(
        f'<path transform="translate(22,21) scale(1.05)" fill="{c["muted"]}" d="M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5a.75.75 0 0 1 0-1.5h1.75v-2h-8a1 1 0 0 0-.714 1.7.75.75 0 1 1-1.072 1.05A2.495 2.495 0 0 1 2 11.5Zm10.5-1h-8a1 1 0 0 0-1 1v6.708A2.486 2.486 0 0 1 4.5 9h8ZM5 12.25a.25.25 0 0 1 .25-.25h3.5a.25.25 0 0 1 .25.25v3.25a.25.25 0 0 1-.4.2l-1.45-1.087a.249.249 0 0 0-.3 0L5.4 15.7a.25.25 0 0 1-.4-.2Z"/>'
        f'<text x="46" y="37" font-family="{SERIF}" font-size="19" font-weight="600" fill="{c["text"]}">{esc(name)}</text>'
    )
    for j, line in enumerate(wrap(r["desc"], 70, 2)):
        s.append(f'<text x="22" y="{64 + j*20}" font-family="{SANS}" font-size="13" fill="{c["muted"]}">{esc(line)}</text>')
    y = 112
    s.append(
        f'<circle cx="28" cy="{y-4}" r="5" fill="{ {"Python": c["cyan"], "Swift": c["pink"], "TypeScript": c["violet"]}.get(r["lang"], c["amber"]) }"/>'
        f'<text x="40" y="{y}" font-family="{SANS}" font-size="12.5" fill="{c["text"]}">{esc(r["lang"])}</text>'
        f'<text x="{60 + len(r["lang"])*7}" y="{y}" font-family="{SANS}" font-size="12.5" fill="{c["text"]}">'
        f'<tspan fill="{c["amber"]}">★</tspan> {r["stars"]}   <tspan fill="{c["muted"]}">⑂</tspan> {r["forks"]}</text>'
    )
    s.append("</svg>")
    return "".join(s)


# ------------------------------------------------------------------ main
def main():
    OUT.mkdir(parents=True, exist_ok=True)
    data = json.loads(CACHE.read_text()) if CACHE.exists() else json.loads(json.dumps(FALLBACK))
    if not OFFLINE:
        try:
            apps = fetch_apps()
            if apps:
                # keep an old icon if Apple's CDN hiccups today
                old = {a["id"]: a for a in data.get("apps", [])}
                for a in apps:
                    if not a["icon"] and old.get(a["id"], {}).get("icon"):
                        a["icon"] = old[a["id"]]["icon"]
                data["apps"] = apps
        except Exception as e:
            print("App Store fetch failed, keeping cached apps:", e)
        try:
            data["stats"], repos = fetch_github()
            data["repos"].update(repos)
        except Exception as e:
            print("GitHub fetch failed, keeping cached stats:", e)
    data["apps"].sort(key=lambda a: (a.get("released", ""), a["id"]), reverse=True)
    CACHE.write_text(json.dumps(data, ensure_ascii=False, indent=1))
    for mode in ("dark", "light"):
        (OUT / f"apps-{mode}.svg").write_text(apps_svg(data["apps"], mode), encoding="utf-8")
        (OUT / f"stats-{mode}.svg").write_text(stats_svg(data["stats"], mode), encoding="utf-8")
        for name in PROJECTS:
            if name in data["repos"]:
                (OUT / f"repo-{name}-{mode}.svg").write_text(repo_svg(name, data["repos"][name], mode), encoding="utf-8")
    print(f"wrote cards for {len(data['apps'])} apps, {len(PROJECTS)} repos")


if __name__ == "__main__":
    main()
