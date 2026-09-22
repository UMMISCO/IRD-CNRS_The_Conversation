#!/usr/bin/env python3
"""Figure 1 bis - the same map, coloured by STRUCTURES instead of co-publications.

Data: data/structures_by_country.csv, data/world_countries.json. Offline.
"""
import csv, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon

# the projection and the frame are figure 1's, imported rather than copied so the two maps
# cannot drift apart
from make_fig1_carte import LAT_N, LAT_S, equal_earth
from style import (FIGW, INK2, MUTED, NODATA, RULE, SURFACE, T_LABEL, T_NOTE, headline, save)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA, FIGS = os.path.join(ROOT, "data"), os.path.join(ROOT, "figures")

# Diverging scale on the BALANCE between the two, not on the raw count. Full red where only
# the IRD is present, full blue where only the CNRS is, and the tints plus a purple midpoint
# for the countries where both are.
#
# The dataviz guidance says a diverging scale takes a neutral grey midpoint and never a hue.
# The exception is deliberate: the midpoint here is not "zero" or "no data", it is "both
# organisations, in equal number", and red plus blue making purple states that better than
# grey, which on this map already means "neither". The five steps were run through the palette
# validator and pass every check - lightness band, chroma, CVD separation (worst adjacent
# pair deltaE 11.5 under deuteranopia), normal-vision floor (16.8) and contrast.
#
# The purple cannot be lightened much further. Sitting between the two tints in hue, at
# their lightness it collides with one or the other: paler versions fell to deltaE 11 against
# the light blue, and pushing it toward magenta to escape that dropped it to deltaE 10
# against the light red. It separates by being a step darker, so a step darker it stays.
IRD_ONLY, IRD_MORE = "#C00510", "#F2857F"
EQUAL = "#B265AB"        # softened toward the two tints; see the note below
CNRS_MORE, CNRS_ONLY = "#82A8EA", "#2B4FA2"


def load():
    path = os.path.join(DATA, "structures_by_country.csv")
    rows = list(csv.DictReader(line for line in open(path, encoding="utf-8")
                               if not line.startswith("#")))
    out = {}
    for r in rows:
        # the CNRS side is IRL + UMIFRE; the CSV keeps the two columns apart
        out[r["iso2"]] = (int(r["ird_structures"]),
                          int(r["cnrs_irl"]) + int(r["cnrs_umifre"]), r["pays"])
    return out


def colour(iso, counts):
    rec = counts.get(iso)
    if rec is None:
        return NODATA
    ird, cnrs, _ = rec
    if ird and not cnrs:
        return IRD_ONLY
    if cnrs and not ird:
        return CNRS_ONLY
    if ird > cnrs:
        return IRD_MORE
    if cnrs > ird:
        return CNRS_MORE
    if ird == cnrs > 0:
        return EQUAL
    return NODATA


def build(title, deck, stem):
    counts = load()
    world = json.load(open(os.path.join(DATA, "world_countries.json")))

    x0, _ = equal_earth(-180, 0)
    _, y_s = equal_earth(0, LAT_S)
    _, y_n = equal_earth(0, LAT_N)
    map_w_in = FIGW - 0.02
    map_h_in = map_w_in * (y_n - y_s) / (2 * -x0)
    head_in = 1.30 if title else 0.06
    foot_in = 2.05
    fig_h = map_h_in + head_in + foot_in

    fig, ax = plt.subplots(figsize=(FIGW, fig_h))
    fig.subplots_adjust(left=0.005, right=0.995,
                        top=1 - head_in / fig_h, bottom=foot_in / fig_h)

    patches, colours = [], []
    for iso, geom in world.items():
        col = colour(iso, counts)
        for ring in geom["r"]:
            pts = [equal_earth(ring[k], ring[k + 1]) for k in range(0, len(ring), 2)]
            if len(pts) >= 3:
                patches.append(Polygon(pts, closed=True))
                colours.append(col)
    ax.add_collection(PatchCollection(patches, facecolor=colours, edgecolor=SURFACE,
                                      linewidth=0.35))
    ax.set_xlim(x0, -x0)
    ax.set_ylim(y_s, y_n)
    ax.set_aspect(1.0)
    ax.axis("off")

    n_both = sum(1 for i, c, _ in counts.values() if i and c)
    n_ird = sum(1 for i, c, _ in counts.values() if i and not c)
    n_cnrs = sum(1 for i, c, _ in counts.values() if c and not i)

    handles = [
        mpatches.Patch(facecolor=IRD_ONLY, edgecolor=RULE, lw=0.5, label="l'IRD seul"),
        mpatches.Patch(facecolor=IRD_MORE, edgecolor=RULE, lw=0.5, label="les deux, l'IRD en a plus"),
        mpatches.Patch(facecolor=CNRS_ONLY, edgecolor=RULE, lw=0.5, label="le CNRS seul"),
        mpatches.Patch(facecolor=CNRS_MORE, edgecolor=RULE, lw=0.5, label="les deux, le CNRS en a plus"),
        mpatches.Patch(facecolor=EQUAL, edgecolor=RULE, lw=0.5, label="les deux, à égalité"),
        mpatches.Patch(facecolor=NODATA, edgecolor=RULE, lw=0.5, label="aucune structure"),
    ]
    leg = ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 0),
                    ncol=3, frameon=False, handlelength=1.15, handleheight=1.15,
                    columnspacing=1.6, handletextpad=0.5, fontsize=T_NOTE,
                    # title="Structures conjointes implantées dans le pays en 2026 (LMI et JEAI pour l'IRD, IRL et UMIFRE pour le CNRS)")
                    title="Implantation des dispositifs internationaux de l'IRD et du CNRS en 2026")
    leg.get_title().set_fontsize(T_NOTE)
    leg.get_title().set_color(MUTED)
    for text in leg.get_texts():
        text.set_color(INK2)

    headline(fig, title, deck)
    save(fig, stem, FIGS)
    return n_ird, n_cnrs, n_both, counts


if __name__ == "__main__":
    n_ird, n_cnrs, n_both, counts = build(
        None, None, "fig1bis_carte_structures_nolegend")
    both = sorted((v[2], v[0], v[1]) for v in counts.values() if v[0] and v[1])
    print(f"  IRD seul {n_ird} | CNRS seul {n_cnrs} | les deux {n_both} | total "
          f"{n_ird + n_cnrs + n_both} pays")
    print("  les deux :", ", ".join(f"{n} ({i}/{c})" for n, i, c in both))
