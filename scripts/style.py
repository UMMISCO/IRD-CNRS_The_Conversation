#!/usr/bin/env python3
"""Shared look for the three Conversation figures.

Colour has to survive colour-blindness and grayscale.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# --- palette -------------------------------------------------------------------------
IRD = "#E30613"        # institutional red, unchanged
CNRS = "#3160C8"       # institutional blue, lightened into the passing lightness band
MID = "#C77B12"        # amber, darkened to clear 3:1 against the surface
# The two greys of the choropleth, and the rule that orders them. "Comparable" is a DATA
# class and "no data" is an absence, so the data class must be the DARKER of the two: a fill
# reads as "more" the darker it gets. They used to be the other way round - no-data at #DCDCD4
# sat darker than comparable at #EFEDE4 - and the effect was that half of Europe and North
# America looked like missing data. Comparable is now clearly a fill; no-data is the palest
# thing on the map, just dark enough to keep the coastlines and borders visible.
#
# Comparable stays deliberately neutral rather than taking a hue: it is the midpoint of a
# diverging scale, and every light violet tried for it collided with either the light red or
# the light blue (normal-vision deltaE around 12, under the 15 floor). It therefore fails the
# validator's chroma and lightness-band checks by design - those apply to categorical palettes,
# not to a diverging midpoint.
NEUTRAL = "#CFC8B4"    # "comparable" - a data class, so darker than the no-data fill
NODATA = "#EFEEE9"     # no or negligible collaboration - the palest fill on the map
SURFACE = "#FCFCFB"

INK = "#0B0B0B"        # headline
INK2 = "#3D3C3A"       # body / subtitle
MUTED = "#6E6C67"      # axis labels, footnotes
RULE = "#C9C7BD"       # axis lines, light separators
GRID = "#E6E4DA"

# --- type scale (points; at FIGW=9in, 1 pt renders as ~1 px in the article column) -----
FIGW = 9.0
T_HEAD = 20            # headline
T_SUB = 14             # subtitle / deck
T_LABEL = 15           # series and category labels
T_BODY = 13.5          # annotations, legend
T_NOTE = 12            # footnote - the floor, used sparingly

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "text.color": INK,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "axes.edgecolor": RULE,
})


def headline(fig, title, deck=None, y=0.965, x=0.012):
    """Headline + optional deck, top-left. Skipped entirely when `title` is None, which is
    how the `_nolegend` variants are produced for a journal that sets its own caption."""
    if title is None:
        return
    fig.text(x, y, title, fontsize=T_HEAD, fontweight="bold", color=INK, ha="left", va="top")
    if deck:
        fig.text(x, y - 0.075, deck, fontsize=T_SUB, color=INK2, ha="left", va="top",
                 linespacing=1.45)


def save(fig, stem, outdir):
    """PNG at 200 dpi for the CMS. PNG only - the CMS takes bitmaps and nobody opened the PDFs."""
    import os
    os.makedirs(outdir, exist_ok=True)
    fig.savefig(os.path.join(outdir, f"{stem}.png"), dpi=200, bbox_inches="tight",
                pad_inches=0.12)
    plt.close(fig)
    print(f"  wrote {stem}.png")
