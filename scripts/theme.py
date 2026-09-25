"""Shared palette + fonts for every SVG in this profile.

A light ink-wash palette: rice paper, sumi ink, and the colours of a clear
day — sky indigo, river teal, moss, saffron, sakura, a vermilion sun.
Each asset is rendered twice (dark + light) and the README picks one with
<picture> so it matches the viewer's GitHub theme.
"""

SANS = "'Segoe UI', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Ubuntu, Arial, sans-serif"
SERIF = "'Iowan Old Style', 'Palatino Linotype', Palatino, 'Book Antiqua', Georgia, 'Noto Serif', serif"
MONO = "'SF Mono', 'JetBrains Mono', Menlo, Consolas, 'Liberation Mono', monospace"

# The accent keys keep their historical names so every drawing function can
# stay the same; the values are what makes it calm.
BRIGHT = {
    "bg": "#f8f2e7",       # rice paper
    "panel": "#fcf8f1",
    "border": "#e7dcc7",
    "grid": "#efe5d3",
    "text": "#2b2823",     # sumi ink
    "muted": "#6f685c",
    "faint": "#dccfb8",
    "violet": "#4f7cac",   # sky indigo
    "cyan": "#2f8f8a",     # river teal
    "green": "#6a9a4b",    # moss
    "amber": "#dc9a2c",    # saffron
    "pink": "#e27d8f",     # sakura
    "red": "#e0714f",      # vermilion sun
    "ink": "#2b2823",
    "term_bg": "#fffaf2",
    "bar_bg": "#f3e9d8",
    "glow": 0.3,
}
# Bright in both GitHub themes: the profile reads as one light ink-wash painting.
THEMES = {"dark": dict(BRIGHT), "light": dict(BRIGHT)}


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
