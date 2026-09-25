"""Shared palette + fonts for every SVG in this profile.

A quiet, ink-and-paper palette: warm charcoal at night, rice paper by day,
with muted earth accents (sand, moss, clay, stone, dusk). No neon.
Each asset is rendered twice (dark + light) and the README picks one with
<picture> so it matches the viewer's GitHub theme.
"""

SANS = "'Segoe UI', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Ubuntu, Arial, sans-serif"
SERIF = "'Iowan Old Style', 'Palatino Linotype', Palatino, 'Book Antiqua', Georgia, 'Noto Serif', serif"
MONO = "'SF Mono', 'JetBrains Mono', Menlo, Consolas, 'Liberation Mono', monospace"

# The accent keys keep their historical names so every drawing function can
# stay the same; the values are what makes it calm.
THEMES = {
    "dark": {
        "bg": "#141311",       # warm charcoal
        "panel": "#1a1916",
        "border": "#2e2b25",
        "grid": "#211f1b",
        "text": "#e9e3d6",     # rice paper
        "muted": "#9b9486",
        "faint": "#3d3a32",
        "violet": "#9aa3b5",   # dusk / stone blue
        "cyan": "#9fae88",     # moss
        "green": "#b3bf98",    # sage
        "amber": "#cdb17e",    # sand gold
        "pink": "#c49a8c",     # clay
        "red": "#b9765d",      # persimmon
        "ink": "#e9e3d6",
        "term_bg": "#161512",
        "bar_bg": "#1d1b18",
        "glow": 0.22,
    },
    "light": {
        "bg": "#f6f2ea",       # paper
        "panel": "#f1ece2",
        "border": "#dfd6c6",
        "grid": "#ece5d8",
        "text": "#2b2823",     # sumi ink
        "muted": "#6f685c",
        "faint": "#cdc3b1",
        "violet": "#5f6b80",
        "cyan": "#5f7249",
        "green": "#6c7e56",
        "amber": "#94753d",
        "pink": "#9a6456",
        "red": "#9a4f36",
        "ink": "#2b2823",
        "term_bg": "#f8f5ef",
        "bar_bg": "#efe9de",
        "glow": 0.14,
    },
}

# Calm sequence used wherever several categories need colours (languages, tiles).
def calm_sequence(c):
    return [c["cyan"], c["amber"], c["violet"], c["pink"], c["green"], c["muted"]]


def esc(s: str) -> str:
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def svg_open(w: int, h: int, title: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="{esc(title)}">'
        f"<title>{esc(title)}</title>"
    )
