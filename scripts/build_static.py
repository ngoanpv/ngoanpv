"""Builds the hand-designed animated SVGs (banner, terminal, focus panels, stillness).

Edit the text in CONFIG below and run:  python scripts/build_static.py
Animations use SMIL + inline styles only, which GitHub renders inside <img>.
"""
import math
import random
from pathlib import Path

from theme import MONO, SANS, SERIF, THEMES, calm_sequence, esc, svg_open

OUT = Path(__file__).resolve().parent.parent / "assets"

CONFIG = {
    "name": "Phạm Văn Ngoan",
    "handle": "~/ngoanpv",
    "roles": "Builder  ·  Multi-agent systems  ·  Voice AI  ·  Evals",
    "pills": ["Idea → Ship → Learn", "Viet Nam"],
    "caption": ("curiosity", "∞"),
    "command": "python doing_cool_stuff.py",
    "modules": [
        ("idea", "listen to users · find a real pain"),
        ("build", "multi-agent systems · RAG · voice agents"),
        ("ship", "to production, company-wide"),
        ("learn", "evals · benchmarks · make it faster"),
    ],
    "status": ("product loop running", "next: something new"),
    "sysinfo": [
        ("user", "Phạm Văn Ngoan"),
        ("home", "Viet Nam"),
        ("ships", "agents, voice AI & a few apps"),
        ("loves", "small details, big impact"),
        ("into", "agent evals · simulated crowds"),
        ("fuel", "cà phê sữa đá"),
    ],
}


def anim_window(t_on, t_off, T, fade=0.25):
    """Opacity animation: hidden until t_on, visible until t_off, loop every T."""
    a = t_on / T
    b = min((t_on + fade) / T, 0.999)
    c = t_off / T
    d = min((t_off + fade) / T, 1.0)
    kt = [0, a, b, c, d]
    vals = [0, 0, 1, 1, 0]
    if d < 1:
        kt.append(1)
        vals.append(0)
    return (
        f'<animate attributeName="opacity" dur="{T}s" repeatCount="indefinite" '
        f'values="{";".join(map(str, vals))}" '
        f'keyTimes="{";".join(f"{k:.4f}" for k in kt)}"/>'
    )


# ---------------------------------------------------------------- banner
def banner(mode: str) -> str:
    c = THEMES[mode]
    W, H = 1200, 300
    rnd = random.Random(7)
    s = [svg_open(W, H, f"{CONFIG['name']} — {CONFIG['roles']}")]
    s.append(
        f"""<defs>
<linearGradient id="tg" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="520" y2="0" spreadMethod="reflect">
  <stop offset="0" stop-color="{c['text']}"/><stop offset="0.55" stop-color="{c['text']}"/><stop offset="1" stop-color="{c['amber']}"/>
  <animateTransform attributeName="gradientTransform" type="translate" values="0 0;520 0;0 0" dur="18s" repeatCount="indefinite"/>
</linearGradient>
<radialGradient id="moon"><stop offset="0" stop-color="{c['ink']}" stop-opacity="{c['glow']*0.5}"/><stop offset="1" stop-color="{c['ink']}" stop-opacity="0"/></radialGradient>
<filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="1.6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<clipPath id="card"><rect width="{W}" height="{H}" rx="18"/></clipPath>
</defs>
<g clip-path="url(#card)">
<rect width="{W}" height="{H}" fill="{c['bg']}"/>"""
    )
    # raked sand lines, barely there
    d = []
    for y0 in range(12, H, 13):
        pts = " L".join(f"{x} {y0 + 1.2 * math.sin(x / 60 + y0 * 0.2):.1f}" for x in range(0, W + 20, 20))
        d.append("M" + pts)
    s.append(f'<path d="{" ".join(d)}" fill="none" stroke="{c["grid"]}" stroke-width="1.1"/>')
    s.append(
        f'<circle cx="955" cy="150" r="230" fill="url(#moon)"><animate attributeName="r" values="215;240;215" dur="12s" repeatCount="indefinite" '
        f'calcMode="spline" keyTimes="0;0.5;1" keySplines="0.45 0 0.55 1;0.45 0 0.55 1"/></circle></g>'
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="18" fill="none" stroke="{c["border"]}"/>'
    )
    # left text block
    s.append(
        f'<text x="66" y="86" font-family="{MONO}" font-size="14" fill="{c["muted"]}">'
        f'<tspan fill="{c["cyan"]}">➜</tspan> {esc(CONFIG["handle"])} '
        f'<tspan fill="{c["faint"]}">git:(</tspan><tspan fill="{c["pink"]}">main</tspan><tspan fill="{c["faint"]}">)</tspan></text>'
    )
    s.append(
        f'<text x="62" y="152" font-family="{SERIF}" font-size="60" font-weight="600" '
        f'letter-spacing="0.5" fill="url(#tg)">{esc(CONFIG["name"])}</text>'
    )
    s.append(
        f'<text x="66" y="190" font-family="{SANS}" font-size="18" fill="{c["muted"]}">{esc(CONFIG["roles"])}</text>'
    )
    x = 66
    for i, p in enumerate(CONFIG["pills"]):
        w = int(len(p) * 7.4 + 36)
        s.append(
            f'<g transform="translate({x},220)">'
            f'<rect x="0.5" y="0.5" width="{w}" height="30" rx="15" fill="none" stroke="{c["faint"]}"/>'
            f'<circle cx="17" cy="15.5" r="3.5" fill="{c["amber"]}">'
            f'<animate attributeName="opacity" values="1;0.35;1" dur="5s" begin="{i*1.5}s" repeatCount="indefinite"/></circle>'
            f'<text x="29" y="20.5" font-family="{SANS}" font-size="13" fill="{c["text"]}" opacity="0.85">{esc(p)}</text></g>'
        )
        x += w + 12

    # a quiet network on the right
    layers = [3, 5, 5, 2]
    xs = [790, 900, 1010, 1120]
    nodes = []
    for li, (n, lx) in enumerate(zip(layers, xs)):
        span = (n - 1) * 44
        top = 150 - span / 2
        nodes.append([(lx, top + k * 44) for k in range(n)])
    edges = []
    for li in range(len(nodes) - 1):
        for a_ in nodes[li]:
            for b_ in nodes[li + 1]:
                edges.append(f'<line x1="{a_[0]}" y1="{a_[1]}" x2="{b_[0]}" y2="{b_[1]}"/>')
    s.append(f'<g stroke="{c["faint"]}" stroke-width="1" opacity="0.8">{"".join(edges)}</g>')

    pk = ['<g filter="url(#soft)">']
    for i in range(10):
        pts = [rnd.choice(layer) for layer in nodes]
        d = "M" + " L".join(f"{x} {y}" for x, y in pts)
        col = c["amber"] if i % 3 else c["cyan"]
        begin = round(i * 0.7, 2)
        pk.append(
            f'<path d="{d}" fill="none" stroke="{col}" stroke-width="1.2" stroke-dasharray="420" stroke-dashoffset="420" opacity="0">'
            f'<animate attributeName="stroke-dashoffset" values="420;0;0" keyTimes="0;0.6;1" dur="5s" begin="{begin}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0;0.45;0.45;0" keyTimes="0;0.15;0.65;1" dur="5s" begin="{begin}s" repeatCount="indefinite"/></path>'
            f'<circle r="2.8" fill="{col}" opacity="0">'
            f'<animateMotion path="{d}" dur="5s" begin="{begin}s" repeatCount="indefinite" keyPoints="0;1;1" keyTimes="0;0.6;1" calcMode="linear"/>'
            f'<animate attributeName="opacity" values="0;0.9;0.9;0" keyTimes="0;0.08;0.6;0.66" dur="5s" begin="{begin}s" repeatCount="indefinite"/></circle>'
        )
    pk.append("</g>")
    s.append("".join(pk))
    for li, layer in enumerate(nodes):
        for k, (x, y) in enumerate(layer):
            begin = round(li * 0.8 + k * 0.15, 2)
            s.append(
                f'<circle cx="{x}" cy="{y}" r="7.5" fill="{c["bg"]}" stroke="{c["muted"]}" stroke-width="1.3"/>'
                f'<circle cx="{x}" cy="{y}" r="3" fill="{c["ink"]}">'
                f'<animate attributeName="opacity" values="0.3;0.9;0.3" dur="6s" begin="{begin}s" repeatCount="indefinite"/></circle>'
            )
    s.append(
        f'<text x="955" y="278" text-anchor="middle" font-family="{MONO}" font-size="12.5" fill="{c["muted"]}">'
        f'model.fit(<tspan fill="{c["amber"]}">{esc(CONFIG["caption"][0])}</tspan>, epochs=<tspan fill="{c["cyan"]}">{esc(CONFIG["caption"][1])}</tspan>)</text>'
    )
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------- terminal
def terminal(mode: str) -> str:
    c = THEMES[mode]
    W, H = 1000, 330
    T = 16.0
    FS = 14
    CW = FS * 0.6  # forced monospace advance via textLength
    LH = 25
    x0, y0 = 26, 76
    t_end = T - 0.7
    s = [svg_open(W, H, f"Terminal: {CONFIG['command']}")]
    term_bg, bar_bg = c["term_bg"], c["bar_bg"]
    s.append(
        f'<defs><clipPath id="win"><rect width="{W}" height="{H}" rx="14"/></clipPath></defs>'
        f'<g clip-path="url(#win)"><rect width="{W}" height="{H}" fill="{term_bg}"/>'
        f'<rect width="{W}" height="40" fill="{bar_bg}"/></g>'
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="14" fill="none" stroke="{c["border"]}"/>'
        f'<circle cx="24" cy="20" r="6" fill="{c["faint"]}"/><circle cx="44" cy="20" r="6" fill="{c["faint"]}"/><circle cx="64" cy="20" r="6" fill="{c["faint"]}"/>'
        f'<text x="{W/2}" y="25" text-anchor="middle" font-family="{MONO}" font-size="13" fill="{c["muted"]}">ngoan@vietnam: ~/projects — zsh</text>'
    )
    # line 1: prompt + typed command
    cmd = CONFIG["command"]
    prompt = "❯ "
    s.append(
        f'<text x="{x0}" y="{y0}" font-family="{MONO}" font-size="{FS}" fill="{c["green"]}" font-weight="700">{prompt}</text>'
    )
    cx = x0 + 2 * CW
    t0, per = 0.7, 0.07
    widths, times = [0], [0]
    for i in range(1, len(cmd) + 1):
        times.append((t0 + i * per) / T)
        widths.append(round(i * CW, 2))
    times.append(t_end / T)
    widths.append(0)
    if times[-1] < 1:
        times.append(1)
        widths.append(0)
    s.append(
        f'<clipPath id="typed"><rect x="{cx}" y="{y0-FS-2}" height="{FS+8}" width="0">'
        f'<animate attributeName="width" calcMode="discrete" dur="{T}s" repeatCount="indefinite" '
        f'values="{";".join(map(str, widths))}" keyTimes="{";".join(f"{t:.4f}" for t in times)}"/></rect></clipPath>'
    )
    s.append(
        f'<text x="{cx}" y="{y0}" font-family="{MONO}" font-size="{FS}" fill="{c["text"]}" '
        f'textLength="{len(cmd)*CW:.1f}" lengthAdjust="spacingAndGlyphs" clip-path="url(#typed)">'
        f'<tspan fill="{c["cyan"]}">python</tspan> {esc(cmd.split(" ",1)[1])}</text>'
    )
    # cursor following the typing on line 1
    typed_done = t0 + len(cmd) * per
    cur_x = [cx + (i * CW) for i in range(len(cmd) + 1)]
    cur_t = [0] + [(t0 + i * per) / T for i in range(1, len(cmd) + 1)]
    s.append(
        f'<rect y="{y0-FS+1}" width="{CW:.1f}" height="{FS+2}" fill="{c["text"]}" x="{cx}">'
        f'<animate attributeName="x" calcMode="discrete" dur="{T}s" repeatCount="indefinite" '
        f'values="{";".join(f"{v:.1f}" for v in cur_x)}" keyTimes="{";".join(f"{t:.4f}" for t in cur_t)}"/>'
        f'{anim_window(0, typed_done + 0.35, T, fade=0.01)}</rect>'
    )

    # output lines
    t = typed_done + 0.6
    y = y0 + LH
    s.append(
        f'<g opacity="0"><text x="{x0}" y="{y}" font-family="{MONO}" font-size="{FS}" fill="{c["muted"]}">'
        f'[boot] loading product loop <tspan fill="{c["faint"]}">.........</tspan></text>{anim_window(t, t_end, T)}</g>'
    )
    mod_cols = [c["violet"], c["cyan"], c["green"], c["amber"]]
    for i, (name, desc) in enumerate(CONFIG["modules"]):
        t += 0.55
        y += LH
        s.append(
            f'<g opacity="0" font-family="{MONO}" font-size="{FS}">'
            f'<text x="{x0}" y="{y}" fill="{c["green"]}">✔</text>'
            f'<text x="{x0+22}" y="{y}" fill="{mod_cols[i]}" font-weight="700">{esc(name)}</text>'
            f'<text x="{x0+124}" y="{y}" fill="{c["text"]}">{esc(desc)}</text>'
            f"{anim_window(t, t_end, T)}</g>"
        )
    t += 0.6
    y += LH
    s.append(
        f'<g opacity="0"><text x="{x0}" y="{y}" font-family="{MONO}" font-size="{FS}" fill="{c["muted"]}">'
        f'[<tspan fill="{c["green"]}">ok</tspan>] {esc(CONFIG["status"][0])} · '
        f'<tspan fill="{c["amber"]}">{esc(CONFIG["status"][1])}</tspan></text>{anim_window(t, t_end, T)}</g>'
    )
    # progress bar under the modules
    bar_y = y + 22
    s.append(
        f'<g opacity="0"><rect x="{x0}" y="{bar_y}" width="440" height="6" rx="3" fill="{c["faint"]}" opacity="0.35"/>'
        f'<rect x="{x0}" y="{bar_y}" width="0" height="6" rx="3" fill="{c["cyan"]}">'
        f'<animate attributeName="width" dur="{T}s" repeatCount="indefinite" values="0;0;440;440;0" '
        f'keyTimes="0;{(typed_done+0.6)/T:.4f};{t/T:.4f};{t_end/T:.4f};1"/></rect>'
        f"{anim_window(typed_done + 0.6, t_end, T)}</g>"
    )
    # final prompt with blinking cursor
    t += 0.7
    y = bar_y + 40
    s.append(
        f'<g opacity="0"><text x="{x0}" y="{y}" font-family="{MONO}" font-size="{FS}" fill="{c["green"]}" font-weight="700">{prompt}</text>'
        f'<rect x="{x0+2*CW:.1f}" y="{y-FS+1}" width="{CW:.1f}" height="{FS+2}" fill="{c["text"]}">'
        f'<animate attributeName="opacity" values="1;0" dur="1s" calcMode="discrete" repeatCount="indefinite"/></rect>'
        f"{anim_window(t, t_end, T)}</g>"
    )

    # right column: neofetch-style sysinfo
    rx = 640
    s.append(f'<line x1="{rx-24}" y1="56" x2="{rx-24}" y2="{H-24}" stroke="{c["border"]}"/>')
    tt = typed_done + 0.9
    ry = y0
    s.append(
        f'<g opacity="0"><text x="{rx}" y="{ry}" font-family="{MONO}" font-size="{FS}" font-weight="700" fill="{c["cyan"]}">ngoan<tspan fill="{c["text"]}">@</tspan><tspan fill="{c["violet"]}">github</tspan></text>'
        f'<text x="{rx}" y="{ry+18}" font-family="{MONO}" font-size="{FS}" fill="{c["faint"]}">───────────────────</text>'
        f"{anim_window(tt, t_end, T)}</g>"
    )
    ry += 20
    for i, (k, v) in enumerate(CONFIG["sysinfo"]):
        tt += 0.45
        ry += LH
        s.append(
            f'<g opacity="0" font-family="{MONO}" font-size="{FS}">'
            f'<text x="{rx}" y="{ry}" fill="{c["cyan"]}" font-weight="700">{esc(k)}</text>'
            f'<text x="{rx+64}" y="{ry}" fill="{c["text"]}">{esc(v)}</text>'
            f"{anim_window(tt, t_end, T)}</g>"
        )
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------- focus panels
def focus(mode: str) -> str:
    c = THEMES[mode]
    W, H = 1000, 250
    CWD, GAP = 235, 20
    rnd = random.Random(3)
    s = [svg_open(W, H, "How I build products: find the pain, build with AI, ship it, learn and iterate")]
    s.append(
        f'<defs><filter id="fglow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.2" result="b"/>'
        f'<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
        f'<clipPath id="phone"><rect x="0" y="0" width="58" height="104" rx="10"/></clipPath></defs>'
    )
    cards = [
        ("pain", "Find the pain", "talk to users · listen hard", "interviews · reviews · notes", c["pink"]),
        ("ai", "Build with AI", "agents that actually help", "LangGraph · RAG · voice", c["violet"]),
        ("ship", "Ship it", "to production, at scale", "vLLM · Docker · Kubernetes", c["cyan"]),
        ("learn", "Learn & iterate", "evals · latency · cost", "DeepEval · Langfuse · A/B", c["green"]),
    ]
    for i, (kind, title, sub, tags, acc) in enumerate(cards):
        ox = i * (CWD + GAP)
        s.append(f'<g transform="translate({ox},0)">')
        s.append(
            f'<rect x="0.5" y="0.5" width="{CWD-1}" height="{H-1}" rx="14" fill="{c["panel"]}" stroke="{c["border"]}"/>'
            f'<line x1="20" y1="1" x2="56" y2="1" stroke="{acc}" stroke-width="2" stroke-linecap="round"/>'
            f'<text x="20" y="40" font-family="{SERIF}" font-size="21" font-weight="600" fill="{c["text"]}">{esc(title)}</text>'
            f'<text x="20" y="58" font-family="{SANS}" font-size="12.5" fill="{c["muted"]}">{esc(sub)}</text>'
            f'<line x1="20" y1="212" x2="{CWD-20}" y2="212" stroke="{c["border"]}"/>'
            f'<text x="20" y="233" font-family="{MONO}" font-size="11" fill="{acc}">{esc(tags)}</text>'
        )
        # animation stage: y 72..200 (128 tall), x 20..215
        if kind == "ai":
            # attention heatmap
            n, cs, g = 8, 11, 3
            gx, gy = 70, 78
            for r in range(n):
                for k in range(n):
                    base = 0.12 + (0.55 if r == k else 0) + (0.25 if abs(r - k) == 1 else 0)
                    vals = [min(1, max(0.08, base + rnd.uniform(-0.1, 0.45))) for _ in range(3)]
                    v = ";".join(f"{x:.2f}" for x in vals + [vals[0]])
                    s.append(
                        f'<rect x="{gx+k*(cs+g)}" y="{gy+r*(cs+g)}" width="{cs}" height="{cs}" rx="2" fill="{acc}" opacity="{vals[0]:.2f}">'
                        f'<animate attributeName="opacity" values="{v}" dur="{rnd.uniform(2.4,3.6):.1f}s" repeatCount="indefinite"/></rect>'
                    )
            toks = ["xin", "chào", "các", "bạn"]
            for j, tk in enumerate(toks):
                s.append(
                    f'<text x="{gx-8}" y="{gy + 8 + j*2*(cs+g)}" text-anchor="end" font-family="{MONO}" font-size="10" fill="{c["muted"]}">{tk}</text>'
                )
            # scanning highlight row
            s.append(
                f'<rect x="{gx-3}" width="{n*(cs+g)+3}" height="{cs+6}" rx="3" fill="none" stroke="{c["text"]}" stroke-opacity="0.5">'
                f'<animate attributeName="y" calcMode="discrete" values="{";".join(str(gy-3+r*(cs+g)) for r in range(n))}" dur="4s" repeatCount="indefinite"/></rect>'
            )
        elif kind == "ship":
            # phone with scrolling feed + progress ring
            px, py = 44, 82
            s.append(f'<g transform="translate({px},{py})">')
            s.append(f'<rect x="-3" y="-3" width="64" height="110" rx="13" fill="none" stroke="{c["text"]}" stroke-opacity="0.7" stroke-width="2"/>')
            s.append('<g clip-path="url(#phone)">')
            s.append(f'<rect width="58" height="104" fill="{c["bg"]}"/>')
            rows = []
            for r in range(12):
                colr = [c["violet"], c["cyan"], c["green"], c["amber"]][r % 4]
                rows.append(
                    f'<rect x="6" y="{14 + r*22}" width="46" height="17" rx="4" fill="{colr}" fill-opacity="0.18"/>'
                    f'<circle cx="14" cy="{22.5 + r*22}" r="4" fill="{colr}"/>'
                    f'<rect x="22" y="{19 + r*22}" width="{16 + (r*7)%18}" height="3" rx="1.5" fill="{c["muted"]}"/>'
                    f'<rect x="22" y="{25 + r*22}" width="{10 + (r*5)%14}" height="2.5" rx="1.2" fill="{c["faint"]}"/>'
                )
            s.append(
                f'<g>{"".join(rows)}<animateTransform attributeName="transform" type="translate" '
                f'values="0 0;0 -88;0 -88;0 -176;0 -176;0 0" keyTimes="0;0.2;0.4;0.6;0.85;1" dur="6s" repeatCount="indefinite" '
                f'calcMode="spline" keySplines="0.4 0 0.2 1;0 0 1 1;0.4 0 0.2 1;0 0 1 1;0.4 0 0.2 1"/></g>'
            )
            s.append(f'<rect x="20" y="4" width="18" height="5" rx="2.5" fill="{c["text"]}" opacity="0.8"/>')
            s.append("</g></g>")
            # build ring
            cxr, cyr, rr = 158, 134, 30
            circ = 2 * math.pi * rr
            s.append(
                f'<circle cx="{cxr}" cy="{cyr}" r="{rr}" fill="none" stroke="{c["faint"]}" stroke-width="6" opacity="0.5"/>'
                f'<circle cx="{cxr}" cy="{cyr}" r="{rr}" fill="none" stroke="{acc}" stroke-width="6" stroke-linecap="round" '
                f'stroke-dasharray="{circ:.1f}" stroke-dashoffset="{circ:.1f}" transform="rotate(-90 {cxr} {cyr})">'
                f'<animate attributeName="stroke-dashoffset" values="{circ:.1f};0;0;{circ:.1f}" keyTimes="0;0.6;0.9;1" dur="6s" repeatCount="indefinite"/></circle>'
                f'<path d="M{cxr-11} {cyr} l7 8 l14 -16" fill="none" stroke="{acc}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" opacity="0">'
                f'<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;0.6;0.65;0.9;1" dur="6s" repeatCount="indefinite"/></path>'
                f'<text x="{cxr}" y="{cyr+48}" text-anchor="middle" font-family="{MONO}" font-size="10" fill="{c["muted"]}">build ▸ ship</text>'
            )
        elif kind == "pain":
            # user feedback bubbles pop in, then the lightbulb switches on
            T = 6.0
            msgs = [("I keep forgetting to…", 22, 80), ("this takes way too long", 34, 114), ("I'd pay for this!", 22, 148)]
            for j, (m, bx, byy) in enumerate(msgs):
                w = int(len(m) * 6.3 + 20)
                on = (0.3 + j * 0.9) / T
                s.append(
                    f'<g opacity="0"><rect x="{bx}" y="{byy}" width="{w}" height="26" rx="13" fill="{acc if j == 2 else c["bg"]}" '
                    f'fill-opacity="{0.18 if j == 2 else 1}" stroke="{acc}" stroke-opacity="{0.9 if j == 2 else 0.35}"/>'
                    f'<path d="M{bx+10} {byy+24} l-6 8 l12 -6 z" fill="{c["bg"] if j != 2 else acc}" fill-opacity="{1 if j != 2 else 0.18}"/>'
                    f'<text x="{bx+12}" y="{byy+17}" font-family="{SANS}" font-size="11" fill="{c["text"]}" font-weight="{700 if j == 2 else 400}">{esc(m)}</text>'
                    f'<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;{on:.3f};{on+0.04:.3f};0.92;1" dur="{T}s" repeatCount="indefinite"/>'
                    f'<animateTransform attributeName="transform" type="translate" values="0 8;0 8;0 0;0 0" keyTimes="0;{on:.3f};{on+0.06:.3f};1" dur="{T}s" repeatCount="indefinite"/></g>'
                )
            lx, ly = 196, 96
            on = 3.2 / T
            s.append(
                f'<circle cx="{lx}" cy="{ly}" r="20" fill="{c["amber"]}" opacity="0" filter="url(#fglow)">'
                f'<animate attributeName="opacity" values="0;0;0.35;0.2;0.35;0" keyTimes="0;{on:.3f};{on+0.05:.3f};0.7;0.85;1" dur="{T}s" repeatCount="indefinite"/></circle>'
                f'<path d="M{lx} {ly-14} a12 12 0 0 1 7 21.5 v4 h-14 v-4 a12 12 0 0 1 7 -21.5 z" fill="{c["panel"]}" stroke="{c["muted"]}" stroke-width="1.8">'
                f'<animate attributeName="fill" values="{c["panel"]};{c["panel"]};{c["amber"]};{c["amber"]};{c["panel"]}" keyTimes="0;{on:.3f};{on+0.02:.3f};0.92;1" dur="{T}s" repeatCount="indefinite"/></path>'
                f'<rect x="{lx-6}" y="{ly+14}" width="12" height="3" rx="1.5" fill="{c["muted"]}"/>'
                f'<rect x="{lx-4.5}" y="{ly+19}" width="9" height="3" rx="1.5" fill="{c["muted"]}"/>'
            )
        else:
            # candlesticks + moving average drawing
            T = 7.0
            price = 60.0
            closes, candles = [], []
            for k in range(12):
                o = price
                price += rnd.uniform(-7, 9)
                cl = price
                hi = max(o, cl) + rnd.uniform(1, 5)
                lo = min(o, cl) - rnd.uniform(1, 5)
                candles.append((o, cl, hi, lo))
                closes.append(cl)
            allv = [v for cd in candles for v in cd]
            vmin, vmax = min(allv), max(allv)
            top, bot = 80, 196

            def Y(v):
                return bot - (v - vmin) / (vmax - vmin) * (bot - top)

            for k, (o, cl, hi, lo) in enumerate(candles):
                x = 26 + k * 15
                col = c["green"] if cl >= o else c["red"]
                on = (0.2 + k * 0.32) / T
                s.append(
                    f'<g opacity="0"><line x1="{x+4}" x2="{x+4}" y1="{Y(hi):.1f}" y2="{Y(lo):.1f}" stroke="{col}" stroke-width="1.5"/>'
                    f'<rect x="{x}" y="{Y(max(o,cl)):.1f}" width="8" height="{max(2, abs(Y(o)-Y(cl))):.1f}" rx="1" fill="{col}"/>'
                    f'<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;{on:.3f};{on+0.02:.3f};0.93;1" dur="{T}s" repeatCount="indefinite"/></g>'
                )
            ma = []
            for k in range(len(closes)):
                w = closes[max(0, k - 2): k + 1]
                ma.append((26 + k * 15 + 4, Y(sum(w) / len(w))))
            d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in ma)
            s.append(
                f'<path d="{d}" fill="none" stroke="{acc}" stroke-width="2" stroke-linejoin="round" stroke-dasharray="400" stroke-dashoffset="400">'
                f'<animate attributeName="stroke-dashoffset" values="400;400;0;0;400" keyTimes="0;0.03;{(0.2+12*0.32)/T:.3f};0.93;1" dur="{T}s" repeatCount="indefinite"/></path>'
            )
            lx, ly = ma[-1]
            s.append(
                f'<g opacity="0"><rect x="{lx+4}" y="{ly-9:.1f}" width="24" height="16" rx="4" fill="{acc}"/>'
                f'<text x="{lx+16}" y="{ly+3:.1f}" text-anchor="middle" font-family="{MONO}" font-size="9.5" font-weight="700" fill="{c["bg"]}">v2</text>'
                f'<animate attributeName="opacity" values="0;0;1;0.4;1;0" keyTimes="0;0.6;0.63;0.75;0.87;0.93" dur="{T}s" repeatCount="indefinite"/></g>'
            )
        s.append("</g>")
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------- stillness (raked sand garden + ensō)
def stillness(mode: str) -> str:
    W, H = 1000, 240
    if mode == "dark":
        bg1, bg2, line, stone, stone_hi, ink, glow = "#141311", "#191814", "#2c2a24", "#24221d", "#4d493f", "#e9e3d6", 0.14
    else:
        bg1, bg2, line, stone, stone_hi, ink, glow = "#f6f2ea", "#f0eadf", "#e0d7c6", "#5b5852", "#8d8980", "#2b2823", 0.10
    rnd = random.Random(11)
    s = [svg_open(W, H, "A quiet raked-sand garden")]
    s.append(
        f"""<defs>
<linearGradient id="zbg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{bg1}"/><stop offset="1" stop-color="{bg2}"/></linearGradient>
<radialGradient id="zmoon"><stop offset="0" stop-color="{ink}" stop-opacity="{glow}"/><stop offset="1" stop-color="{ink}" stop-opacity="0"/></radialGradient>
<radialGradient id="zstone" cx="0.38" cy="0.3" r="0.8"><stop offset="0" stop-color="{stone_hi}"/><stop offset="1" stop-color="{stone}"/></radialGradient>
<filter id="brush" x="-10%" y="-10%" width="120%" height="120%">
  <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="4" result="n"/>
  <feDisplacementMap in="SourceGraphic" in2="n" scale="5" xChannelSelector="R" yChannelSelector="G"/>
</filter>
<filter id="soft"><feGaussianBlur stdDeviation="1.4"/></filter>
<clipPath id="zc"><rect width="{W}" height="{H}" rx="18"/></clipPath>
</defs>
<g clip-path="url(#zc)"><rect width="{W}" height="{H}" fill="url(#zbg)"/>"""
    )
    # keep-out zones: (cx, cy, rx, ry) — raked lines stop at the outer ring
    stones = [(300, 128, 34, 20, 7), (520, 92, 18, 11, 4), (575, 166, 12, 7, 3)]
    enso = (820, 120, 78)
    zones = [(cx, cy, rx + 12 * rings + 8, (rx + 12 * rings + 8) * 0.58) for cx, cy, rx, ry, rings in stones]
    zones.append((enso[0], enso[1], enso[2] + 22, enso[2] + 22))

    def inside(x, y):
        return any(((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 < 1 for cx, cy, rx, ry in zones)

    lines = []
    for y0 in range(14, H, 11):
        seg = []
        for x in range(-4, W + 8, 6):
            y = y0 + 1.1 * math.sin(x / 47 + y0 * 0.3)
            if inside(x, y):
                if len(seg) > 1:
                    lines.append(seg)
                seg = []
            else:
                seg.append((x, y))
        if len(seg) > 1:
            lines.append(seg)
    d = " ".join("M" + " L".join(f"{x} {y:.1f}" for x, y in seg) for seg in lines)
    s.append(f'<path d="{d}" fill="none" stroke="{line}" stroke-width="1.3" stroke-linecap="round"/>')

    # stones with raked rings that breathe very slowly
    for i, (cx, cy, rx, ry, rings) in enumerate(stones):
        ring = "".join(
            f'<ellipse rx="{rx + 12 * k}" ry="{(rx + 12 * k) * 0.58:.1f}" fill="none" stroke="{line}" stroke-width="1.3"/>'
            for k in range(1, rings + 1)
        )
        s.append(
            f'<g transform="translate({cx},{cy})"><g>{ring}'
            f'<animateTransform attributeName="transform" type="scale" values="1;1.035;1" dur="10s" begin="{i*1.3}s" repeatCount="indefinite" '
            f'calcMode="spline" keyTimes="0;0.5;1" keySplines="0.45 0 0.55 1;0.45 0 0.55 1"/></g>'
        )
        if i == 0:  # one slow ripple, like a drop on still water
            for k in range(2):
                s.append(
                    f'<ellipse rx="{rx+6}" ry="{(rx+6)*0.58:.1f}" fill="none" stroke="{ink}" stroke-width="1" opacity="0">'
                    f'<animate attributeName="rx" values="{rx+6};{rx+96}" dur="10s" begin="{k*5}s" repeatCount="indefinite"/>'
                    f'<animate attributeName="ry" values="{(rx+6)*0.58:.1f};{(rx+96)*0.58:.1f}" dur="10s" begin="{k*5}s" repeatCount="indefinite"/>'
                    f'<animate attributeName="opacity" values="0;0.35;0" keyTimes="0;0.15;1" dur="10s" begin="{k*5}s" repeatCount="indefinite"/></ellipse>'
                )
        s.append(
            f'<ellipse cx="2" cy="{ry*0.55:.1f}" rx="{rx*1.05:.1f}" ry="{ry*0.45:.1f}" fill="#000" opacity="0.18" filter="url(#soft)"/>'
            f'<ellipse rx="{rx}" ry="{ry}" fill="url(#zstone)"/></g>'
        )

    # ensō — one brush stroke, drawn slowly, held, released
    ex, ey, er = enso
    s.append(f'<circle cx="{ex}" cy="{ey}" r="{er+40}" fill="url(#zmoon)"/>')
    a0, sweep = math.radians(-70), math.radians(318)
    a1 = a0 + sweep
    x0, y0 = ex + er * math.cos(a0), ey + er * math.sin(a0)
    x1, y1 = ex + er * math.cos(a1), ey + er * math.sin(a1)
    path = f"M{x0:.1f} {y0:.1f} A{er} {er} 0 1 1 {x1:.1f} {y1:.1f}"
    L = er * sweep + 4
    T = 16
    draw = (
        f'<animate attributeName="stroke-dashoffset" values="{L:.0f};{L:.0f};0;0;0" keyTimes="0;0.05;0.4;0.9;1" dur="{T}s" repeatCount="indefinite" '
        f'calcMode="spline" keySplines="0 0 1 1;0.55 0.05 0.35 1;0 0 1 1;0 0 1 1"/>'
        f'<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;0.05;0.8;0.93;1" dur="{T}s" repeatCount="indefinite"/>'
    )
    s.append(
        f'<g filter="url(#brush)">'
        f'<path d="{path}" fill="none" stroke="{ink}" stroke-width="11" stroke-linecap="round" stroke-dasharray="{L:.0f}" stroke-dashoffset="{L:.0f}" opacity="0.9">{draw}</path>'
        f'<path d="{path}" fill="none" stroke="{ink}" stroke-width="3" stroke-linecap="round" stroke-dasharray="{L:.0f}" stroke-dashoffset="{L:.0f}" opacity="0.5" transform="translate(4 3)">{draw}</path>'
        f"</g>"
    )

    # a few motes drifting upward, barely there
    for i in range(7):
        x = rnd.uniform(60, 960)
        dur = rnd.uniform(14, 22)
        s.append(
            f'<circle cx="{x:.0f}" cy="{H+6}" r="{rnd.uniform(1,1.8):.1f}" fill="{ink}" opacity="0">'
            f'<animate attributeName="cy" values="{H+6};{rnd.uniform(-10,60):.0f}" dur="{dur:.1f}s" begin="{-rnd.uniform(0,dur):.1f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="cx" values="{x:.0f};{x+rnd.uniform(-30,30):.0f};{x:.0f}" dur="{dur:.1f}s" begin="{-rnd.uniform(0,dur):.1f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0;0.45;0" dur="{dur:.1f}s" begin="{-rnd.uniform(0,dur):.1f}s" repeatCount="indefinite"/></circle>'
        )
    # one leaf, drifting down and settling on the sand
    leaf = f'<path d="M0 -5 C5 -3 6 3 0 6 C-6 3 -5 -3 0 -5 Z" fill="{"#c9a36b" if mode == "dark" else "#b07d3b"}" opacity="0.85"/>'
    s.append(
        f'<g opacity="0">{leaf}'
        f'<animateMotion path="M640 -12 C600 40 700 70 650 110 S620 170 668 196" dur="20s" repeatCount="indefinite" rotate="auto" keyPoints="0;1;1" keyTimes="0;0.6;1" calcMode="linear"/>'
        f'<animate attributeName="opacity" values="0;0.9;0.9;0" keyTimes="0;0.05;0.85;1" dur="20s" repeatCount="indefinite"/></g>'
    )
    s.append(f'</g><rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="18" fill="none" stroke="{line}"/></svg>')
    return "".join(s)


# ---------------------------------------------------------------- exploring (simulated crowd + eval gate)
def exploring(mode: str) -> str:
    c = THEMES[mode]
    W, H = 1000, 300
    T = 12.0
    rnd = random.Random(21)
    s = [svg_open(W, H, "Exploring: simulated crowds, how ideas spread, and evaluation gates that can abstain")]
    s.append(
        f'<defs><filter id="eg" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="2.5" result="b"/>'
        f'<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>'
        f'<rect x="0.5" y="0.5" width="599" height="{H-1}" rx="16" fill="{c["panel"]}" stroke="{c["border"]}"/>'
        f'<rect x="620.5" y="0.5" width="379" height="{H-1}" rx="16" fill="{c["panel"]}" stroke="{c["border"]}"/>'
        f'<text x="24" y="34" font-family="{MONO}" font-size="13" fill="{c["muted"]}">crowd.<tspan fill="{c["cyan"]}">simulate</tspan>(decision)</text>'
        f'<text x="576" y="34" text-anchor="end" font-family="{SANS}" font-size="11.5" fill="{c["muted"]}">'
        f'<tspan fill="{c["cyan"]}">●</tspan> heard   <tspan fill="{c["violet"]}">●</tspan> passed it on</text>'
        f'<text x="24" y="{H-18}" font-family="{SANS}" font-size="12" fill="{c["muted"]}">personas grounded in real answers · ideas spread through friends</text>'
    )
    centers = [(120, 115), (275, 95), (440, 120), (190, 215), (385, 215)]
    nodes = []
    for ci, (cx, cy) in enumerate(centers):
        for _ in range(11):
            for _try in range(40):
                a, r = rnd.uniform(0, 2 * math.pi), rnd.uniform(6, 50)
                x, y = cx + r * math.cos(a) * 1.25, cy + r * math.sin(a) * 0.85
                if all((x - n[0]) ** 2 + (y - n[1]) ** 2 > 196 for n in nodes):
                    break
            nodes.append((x, y, ci))
    N = len(nodes)
    d2 = lambda i, j: (nodes[i][0] - nodes[j][0]) ** 2 + (nodes[i][1] - nodes[j][1]) ** 2
    adj = {i: set() for i in range(N)}
    for i in range(N):
        same = sorted((j for j in range(N) if j != i and nodes[j][2] == nodes[i][2]), key=lambda j: d2(i, j))
        for j in same[:2 + (i % 2)]:
            adj[i].add(j); adj[j].add(i)
    for a_, b_ in [(0, 1), (1, 2), (0, 3), (3, 4), (2, 4), (1, 4)]:
        ia = [i for i in range(N) if nodes[i][2] == a_]
        ib = [i for i in range(N) if nodes[i][2] == b_]
        i, j = min(((i, j) for i in ia for j in ib), key=lambda p: d2(*p))
        adj[i].add(j); adj[j].add(i)
    edges = {tuple(sorted((i, j))) for i in adj for j in adj[i]}
    s.append(f'<g stroke="{c["faint"]}" stroke-width="1" opacity="0.55">' + "".join(
        f'<line x1="{nodes[i][0]:.1f}" y1="{nodes[i][1]:.1f}" x2="{nodes[j][0]:.1f}" y2="{nodes[j][1]:.1f}"/>' for i, j in edges) + "</g>")
    # propagation: only agents who are convinced pass it on
    seed = min(range(N), key=lambda i: d2(i, i) + (nodes[i][0] - 95) ** 2 + (nodes[i][1] - 120) ** 2)
    import heapq
    bridge_nodes = {i for i in adj for j in adj[i] if nodes[i][2] != nodes[j][2]}
    heard, shares, trips = {seed: 0.8}, {seed}, []
    pq = [(0.8, seed)]
    while pq:
        t_i, i = heapq.heappop(pq)
        if i not in shares:
            continue
        for j in sorted(adj[i]):
            t = t_i + rnd.uniform(0.3, 0.6)
            if j in heard or t > 8.8:
                continue
            heard[j] = t
            trips.append((i, j, t_i, t))
            if j in bridge_nodes or rnd.random() < 0.55:
                shares.add(j)
                heapq.heappush(pq, (t, j))
    pk = []
    for i, j, t0, t1 in trips:
        pth = f"M{nodes[i][0]:.1f} {nodes[i][1]:.1f} L{nodes[j][0]:.1f} {nodes[j][1]:.1f}"
        k0, k1 = t0 / T, t1 / T
        pk.append(
            f'<circle r="2.6" fill="{c["violet"]}" opacity="0">'
            f'<animateMotion path="{pth}" dur="{T}s" repeatCount="indefinite" keyPoints="0;0;1;1" keyTimes="0;{k0:.4f};{k1:.4f};1" calcMode="linear"/>'
            f'<animate attributeName="opacity" values="0;0;1;0;0" keyTimes="0;{k0:.4f};{(k0+k1)/2:.4f};{k1:.4f};1" dur="{T}s" repeatCount="indefinite"/></circle>'
        )
    s.append('<g filter="url(#eg)">' + "".join(pk) + "</g>")
    end = 10.8 / T
    for i, (x, y, ci) in enumerate(nodes):
        base = c["faint"]
        if i in heard:
            k = heard[i] / T
            col = c["violet"] if i in shares else c["cyan"]
            s.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{5.5 if i == seed else 4.5}" fill="{base}">'
                f'<animate attributeName="fill" values="{base};{base};{col};{col};{base}" keyTimes="0;{k:.4f};{k+0.01:.4f};{end:.4f};1" dur="{T}s" repeatCount="indefinite"/></circle>'
            )
            if i in shares:
                s.append(
                    f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="none" stroke="{col}" opacity="0">'
                    f'<animate attributeName="r" values="4;4;14;14" keyTimes="0;{k:.4f};{min(k+0.08,0.99):.4f};1" dur="{T}s" repeatCount="indefinite"/>'
                    f'<animate attributeName="opacity" values="0;0;0.7;0;0" keyTimes="0;{k:.4f};{k+0.005:.4f};{min(k+0.08,0.99):.4f};1" dur="{T}s" repeatCount="indefinite"/></circle>'
                )
        else:
            s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="{base}"/>')

    # eval gate: two runs per loop — one concludes, one abstains
    gx = 644
    s.append(
        f'<text x="{gx}" y="34" font-family="{MONO}" font-size="13" fill="{c["muted"]}"><tspan fill="{c["amber"]}">eval_gate</tspan>(run)</text>'
        f'<text x="976" y="34" text-anchor="end" font-family="{SANS}" font-size="11.5" fill="{c["muted"]}">conclude — or abstain</text>'
    )
    metrics = [("agrees with real people", 0.62, (0.80, 0.78)), ("stable across reruns", 0.70, (0.88, 0.52)),
               ("enough evidence", 0.55, (0.74, 0.70))]
    bw = 330
    for m, (lab, thr, (v1, v2)) in enumerate(metrics):
        y = 70 + m * 50
        s.append(
            f'<text x="{gx}" y="{y}" font-family="{SANS}" font-size="12.5" fill="{c["text"]}">{lab}</text>'
            f'<rect x="{gx}" y="{y+9}" width="{bw}" height="8" rx="4" fill="{c["faint"]}" opacity="0.4"/>'
        )
        w1, w2 = bw * v1, bw * v2
        t_on = (0.6 + m * 0.5) / T
        t2 = (6.6 + m * 0.5) / T
        s.append(
            f'<rect x="{gx}" y="{y+9}" height="8" rx="4" width="{w1:.0f}" fill="{c["green"]}">'
            f'<animate attributeName="width" values="0;0;{w1:.0f};{w1:.0f};0;0;{w2:.0f};{w2:.0f};0" '
            f'keyTimes="0;{t_on:.3f};{t_on+0.08:.3f};0.47;0.5;{t2:.3f};{t2+0.08:.3f};0.97;1" dur="{T}s" repeatCount="indefinite"/>'
        )
        if v2 < thr:
            s.append(
                f'<animate attributeName="fill" values="{c["green"]};{c["green"]};{c["amber"]};{c["amber"]}" keyTimes="0;0.5;0.501;1" dur="{T}s" repeatCount="indefinite"/>'
            )
        s.append("</rect>")
        tx = gx + bw * thr
        s.append(f'<line x1="{tx:.0f}" y1="{y+5}" x2="{tx:.0f}" y2="{y+21}" stroke="{c["text"]}" stroke-width="1.5" opacity="0.7"/>')
    # verdicts
    vy = 232
    for k, (label, sub, col, a, b) in enumerate([
        ("CONCLUDE", "rank: B › A › C", c["green"], 2.4, 5.8),
        ("ABSTAIN", "not stable enough to say", c["amber"], 8.4, 11.8),
    ]):
        s.append(
            f'<g opacity="0"><rect x="{gx}" y="{vy}" width="332" height="40" rx="10" fill="{col}" fill-opacity="0.12" stroke="{col}" stroke-opacity="0.6"/>'
            f'<text x="{gx+16}" y="{vy+25}" font-family="{MONO}" font-size="13" font-weight="700" fill="{col}">{label}</text>'
            f'<text x="{gx+120}" y="{vy+25}" font-family="{SANS}" font-size="12.5" fill="{c["text"]}">{sub}</text>'
            f"{anim_window(a, b, T)}</g>"
        )
    s.append("</svg>")
    return "".join(s)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for mode in ("dark", "light"):
        (OUT / f"banner-{mode}.svg").write_text(banner(mode), encoding="utf-8")
        (OUT / f"terminal-{mode}.svg").write_text(terminal(mode), encoding="utf-8")
        (OUT / f"focus-{mode}.svg").write_text(focus(mode), encoding="utf-8")
        (OUT / f"stillness-{mode}.svg").write_text(stillness(mode), encoding="utf-8")
        (OUT / f"exploring-{mode}.svg").write_text(exploring(mode), encoding="utf-8")
    print("static assets written to", OUT)


if __name__ == "__main__":
    main()
