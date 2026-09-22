#!/usr/bin/env python3
"""Figure 1 - Two geographies: the IRD and the CNRS do not set up in the same places.

Data: data/partner_countries.json (OpenAlex, exact server-side aggregation),
data/ird_cnrs_structures_by_region.csv (IRD pages + reconstructed CNRS IRL list),
data/world_countries.json (geometry). Offline.
"""
import csv, json, math, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon, Wedge

from style import (FIGW, INK2, MUTED, NEUTRAL, NODATA, RULE, SURFACE, T_LABEL, T_NOTE, headline, save)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA, FIGS = os.path.join(ROOT, "data"), os.path.join(ROOT, "figures")

MIN_WORKS = 50           # below this the ratio is noise; such countries are shown as "no data"
HOME = "FR"              # excluded: domestic co-authorship dominates both and says nothing here
LAT_S, LAT_N = -57, 74   # south cut drops Antarctica, north cut the empty Arctic

# Colours for the STRUCTURES layer. Red for the IRD, blue for the CNRS - the same language as
# the choropleth, because they carry the same meaning. The symbols are anchored at sea, where
# the background is the plain surface, so a red disc never sits on a red country.
IRD_C, IRL_C = "#C00510", "#3160C8"
LABEL_ABOVE = {"Méditerranée"}   # regions whose label goes above the pie
R_PIE = 0.105            # every pie the same radius, in projected units: the pie shows the
                         # share, the numbers underneath carry the magnitude

# class edges on the index, from most-IRD to most-CNRS
CLASSES = [
    (5.0, float("inf"), "#C00510", "5× et plus"),
    (2.0, 5.0, "#F2857F", "2 à 5×"),
    (0.5, 2.0, NEUTRAL, "comparable"),
    (0.0, 0.5, "#6E90DA", "2× et plus"),
]

def load():
    d = json.load(open(os.path.join(DATA, "partner_countries.json")))
    ird, cnrs = d["counts"]["IRD"], d["counts"]["CNRS"]
    tot_i = sum(v for k, v in ird.items() if k != HOME)
    tot_c = sum(v for k, v in cnrs.items() if k != HOME)

    index = {}
    for iso in set(ird) | set(cnrs):
        if iso == HOME:
            continue
        i, c = ird.get(iso, 0), cnrs.get(iso, 0)
        if i + c < MIN_WORKS:
            continue
        # +1e-12 keeps a zero denominator finite; such countries land in the top class anyway
        index[iso] = ((i / tot_i) + 1e-12) / ((c / tot_c) + 1e-12)
    return index, d["names"]

def load_structures():
    """Joint structures per region: LMI + JEAI for the IRD, IRL/CRI for the CNRS.

    Provenance, and the geographic rule used to assign a country to a region, are in the
    header of the CSV. The IRD regions and counts are its own pages'; the CNRS list is the
    62 IRL reconstructed one by one in the IRD-impact repository, the CNRS publishing none.
    """
    path = os.path.join(DATA, "ird_cnrs_structures_by_region.csv")
    rows = list(csv.DictReader(line for line in open(path) if not line.startswith("#")))
    for r in rows:
        r["lmi"], r["jeai"] = int(r["lmi"]), int(r["jeai"])
        r["cnrs_irl"] = int(r["cnrs_irl"])
        r["ird"] = r["lmi"] + r["jeai"]
        r["lon"], r["lat"] = float(r["lon"]), float(r["lat"])
    return rows

# --- Equal Earth projection (Savric, Patterson & Jenny, 2018) ---------------------------
_A1, _A2, _A3, _A4 = 1.340264, -0.081106, 0.000893, 0.003796

def equal_earth(lon_deg, lat_deg):
    lon, lat = math.radians(lon_deg), math.radians(lat_deg)
    theta = math.asin(math.sqrt(3.0) / 2.0 * math.sin(lat))
    t2 = theta * theta
    t6 = t2 * t2 * t2
    den = 3.0 * (9 * _A4 * t6 * t2 + 7 * _A3 * t6 + 3 * _A2 * t2 + _A1)
    x = 2.0 * math.sqrt(3.0) * lon * math.cos(theta) / den
    y = _A4 * theta * t6 * t2 + _A3 * theta * t6 + _A2 * theta * t2 + _A1 * theta
    return x, y

def colour(iso, index):
    v = index.get(iso)
    if v is None:
        # return NODATA
        return NEUTRAL
    for lo, hi, col, _ in CLASSES:
        if lo <= v < hi:
            return col
    # return NODATA
    return NEUTRAL

def build(title, deck, stem):
    index, _names = load()
    world = json.load(open(os.path.join(DATA, "world_countries.json")))

    # Frame first, figure height second. Equal Earth has its own aspect ratio; picking a
    # figure size by hand left the map floating in white space, so the height is derived
    # from the projected extent and the map always fills the column width exactly.
    x0, _ = equal_earth(-180, 0)
    _, y_s = equal_earth(0, LAT_S)
    _, y_n = equal_earth(0, LAT_N)
    map_w_in = FIGW - 0.02                      # side margins
    map_h_in = map_w_in * (y_n - y_s) / (2 * -x0)
    head_in = 1.62 if title else 0.06           # headline + deck (3 lines)
    foot_in = 2.72                              # punchline + Asia note + two keys
    fig_h = map_h_in + head_in + foot_in

    fig, ax = plt.subplots(figsize=(FIGW, fig_h))
    fig.subplots_adjust(left=0.005, right=0.995,
                        top=1 - head_in / fig_h, bottom=foot_in / fig_h)

    patches, colours = [], []
    for iso, geom in world.items():
        col = colour(iso, index)
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

    n_ird = sum(1 for v in index.values() if v >= 5)
    n_cnrs = sum(1 for v in index.values() if v <= 0.5)

    # --- legend
    handles = [
        mpatches.Patch(facecolor=CLASSES[0][2], edgecolor=RULE, lw=0.5, label="l'IRD, 5× et plus"),
        mpatches.Patch(facecolor=CLASSES[1][2], edgecolor=RULE, lw=0.5, label="l'IRD, 2 à 5×"),
        mpatches.Patch(facecolor=CLASSES[3][2], edgecolor=RULE, lw=0.5, label="le CNRS, 2× et plus"),
        mpatches.Patch(facecolor=NEUTRAL, edgecolor=RULE, lw=0.5, label="comparable"),
    ]
    leg = ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 0),
                    ncol=5, frameon=False, handlelength=1.15, handleheight=1.15,
                    columnspacing=1.35, handletextpad=0.5, fontsize=T_NOTE,
                    title="Nombre de co-publication par pays en 2024")
    leg.get_title().set_fontsize(T_NOTE)
    leg.get_title().set_color(MUTED)
    for text in leg.get_texts():
        text.set_color(INK2)

    headline(fig, title, deck)
    save(fig, stem, FIGS)
    return n_ird, n_cnrs, len(index)

if __name__ == "__main__":
    n_ird, n_cnrs, n_tot =     build(None, None, "fig1_carte_deux_geographies_nolegend")
    print(f"  countries scored: {n_tot} | IRD >=5x: {n_ird} | CNRS >=2x: {n_cnrs}")
