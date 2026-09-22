#!/usr/bin/env python3
"""Figure 3 - A euro is not worth the same everywhere it is spent.

Data: data/euro_value_map.csv, data/ppp_all_countries.csv (World Bank PA.NUS.PPP / PA.NUS.FCRF),
data/climate_disaster_burden.csv (researcher density, works). Offline.
"""
import csv, os, statistics, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import LogLocator, NullFormatter

# the colour rule lives in figure 4 and is imported, never copied: the two figures must
# mean the same thing by a red dot, and two copies of a threshold drift apart
from make_fig4_catastrophes import leads_ird
from style import (CNRS, FIGW, GRID, INK, INK2, IRD, MUTED, RULE, SURFACE, T_BODY,
                   T_LABEL, T_NOTE, headline, save)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA, FIGS = os.path.join(ROOT, "data"), os.path.join(ROOT, "figures")

FRANCE_C = "#8A857A"
CLOUD_C = "#9C988C"     # the context cloud: every other country, deliberately colourless
XMAX, YMIN = 3.7, 9    # frame; three countries fall outside it and are named on the chart
FR_NAMES = {"Egypt": "Égypte"}
GROUPS = {"ird_south": IRD, "cnrs_typical": CNRS, "france": FRANCE_C}


def load():
    rows = list(csv.DictReader(open(os.path.join(DATA, "euro_value_map.csv"))))
    for r in rows:
        r["ppp"] = float(r["ppp_mult_vs_fr"])
        r["dens"] = float(r["researchers_per_million"])

    def med(group):
        return statistics.median(r["ppp"] for r in rows if r["group"] == group)

    return rows, med("ird_south"), med("cnrs_typical")


def load_cloud():
    """The countries of figure 4, on this figure's axes.

    Same 111 countries, because they are the ones for which both researcher density and the
    World Bank price level exist. The 15 named here are drawn separately and excluded, so no
    country is plotted twice. Dot area follows total works, as on figure 4.

    Returns the dots that fit in the frame, and the names of those that do not.
    """
    ppp = {r["iso2"]: r for r in csv.DictReader(
        open(os.path.join(DATA, "ppp_all_countries.csv"), encoding="utf-8"))}
    named = {r["iso"] for r in csv.DictReader(
        open(os.path.join(DATA, "euro_value_map.csv"), encoding="utf-8"))}
    dots, off = [], []
    for r in csv.DictReader(open(os.path.join(DATA, "climate_disaster_burden.csv"),
                                 encoding="utf-8")):
        q = ppp.get(r["iso2"])
        if not q or not r["researchers_per_million"] or q["iso3"] in named:
            continue
        x, y = float(q["ppp_mult_vs_fr"]), float(r["researchers_per_million"])
        ird_works, cnrs_works = int(r["ird_works"] or 0), int(r["cnrs_works"] or 0)
        works = ird_works + cnrs_works
        lead_ird = leads_ird(ird_works, cnrs_works)
        if x > XMAX or y < YMIN:
            name = FR_NAMES.get(r["country"], r["country"])
            off.append((name, x, y))
        else:
            dots.append((x, y, 16 + 30 * (works ** 0.32) / 8, lead_ird))
    return dots, sorted(off, key=lambda t: -t[1])


def build(title, deck, stem):
    rows, mult_ird, mult_cnrs = load()
    cloud, offscale = load_cloud()

    fig, ax_a = plt.subplots(figsize=(FIGW, 6.4 if title else 5.6))
    top = 0.795 if title else 0.965
    fig.subplots_adjust(left=0.115, right=0.965, top=top, bottom=0.175)
    box_a = ax_a.get_position()
    LX = 0.012

    # ---------- panel 1: the value map ------------------------------------------------
    # the context cloud, behind everything else
    cloud_colors = [IRD if d[3] else CNRS for d in cloud]
    ax_a.scatter([d[0] for d in cloud], [d[1] for d in cloud], s=[d[2] for d in cloud],
                 color=cloud_colors, alpha=0.5, edgecolor=SURFACE, linewidth=0.7, zorder=3)

    for r in rows:
        france = r["group"] == "france"
        if (france):
            continue
        ax_a.scatter(r["ppp"], r["dens"], s=170 if not france else 140,
                     c=GROUPS[r["group"]], marker="D" if france else "o",
                     edgecolor=SURFACE, linewidth=1.6, zorder=4, alpha=0.92)

    # Country names. Using radial offsets in points and leader lines (arrows)
    # to pull the labels away from the dense background cloud.
    LABELS = {
        "États-Unis": (0, -50, "center", "top"),
        "Royaume-Uni": (0, -26, "center", "top"),
        "Allemagne": (0, 28, "center", "bottom"),
        "Italie": (28, -25, "left", "center"),
        "Japon": (35, 10, "left", "center"),
        "Chine": (30, 18, "left", "bottom"),
        "Brésil": (0, -30, "center", "top"),
        "Sénégal": (0, 30, "center", "bottom"),
        "Congo": (32, 14, "left", "bottom"),
        "Tchad": (28, 5, "left", "top"),
        "Côte d'Ivoire": (-5, 25, "right", "bottom"),
        "Burkina Faso": (-35, 0, "right", "center"),
        "Niger": (-20, -14, "right", "top"),
        "Mali": (14, -26, "left", "top"),
        "Madagascar": (30, -8, "left", "center"),
    }

    leader = dict(arrowstyle="-", color=MUTED, lw=0.9, shrinkA=1, shrinkB=4)
    for r in rows:
        c = r["country"]
        if c == "France":
            continue
        off = LABELS.get(c)
        if off is None:
            continue
        dx, dy, ha, va = off
        xy = (r["ppp"], r["dens"])
        ax_a.annotate(c, xy, textcoords="offset points", xytext=(dx, dy),
                      ha=ha, va=va, fontsize=T_NOTE, color=INK2, zorder=6,
                      arrowprops=leader)

    ax_a.axvline(1.0, color=RULE, lw=1.0, ls=(0, (4, 3)), zorder=1)
    ax_a.text(1.2, 7, "France\n(référence)", ha="center", va="bottom", fontsize=T_NOTE, color=MUTED)

    ax_a.set_yscale("log")
    ax_a.set_xlim(0.6, XMAX)
    # bottom margin widened from 15: Niger sits at 27 researchers/M and its label,
    # hung below the dot, ran into the axis line
    # The axis floor sits below YMIN, which is only the inclusion threshold: the extra sixth
    # of a decade is empty space that keeps the lowest labels (Mali, Niger) off the
    # "hors cadre" note. No country lies between the two values.
    ax_a.set_ylim(6, 15000)
    ax_a.set_yticks([100, 1000, 10000])
    ax_a.set_yticklabels(["100", "1\u202f000", "10\u202f000"])
    ax_a.yaxis.set_minor_locator(LogLocator(base=10.0, subs=tuple(range(2, 10)), numticks=99))
    ax_a.yaxis.set_minor_formatter(NullFormatter())
    ax_a.set_xticks([0.75, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5])
    ax_a.set_xticklabels(["0,75\u202f\u00d7", "1\u202f\u00d7", "1,5\u202f\u00d7",
                          "2\u202f\u00d7", "2,5\u202f\u00d7", "3\u202f\u00d7",
                          "3,5\u202f\u00d7"])
    ax_a.set_xlabel("Impact d'un euro investi dans le système de recherche par pays, par rapport à la France", fontsize=T_BODY, color=MUTED, labelpad=7)
    ax_a.set_ylabel("Nombre de chercheurs par million d'habitants\n(échelle logarithmique)", fontsize=T_BODY, color=MUTED, linespacing=1.4, labelpad=10)
    ax_a.tick_params(labelsize=T_BODY, length=0)
    ax_a.tick_params(which="minor", length=0)
    # the minor grid is what makes the log scale legible; it stays fainter than the decades
    ax_a.grid(True, which="major", color=GRID, lw=0.9, zorder=0)
    ax_a.grid(True, which="minor", color=GRID, lw=0.5, alpha=0.55, zorder=0)
    ax_a.set_axisbelow(True)
    for side in ("top", "right"):
        ax_a.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax_a.spines[side].set_color(RULE)

    handles = [
        Line2D([], [], marker="o", ls="", ms=11, color=IRD, markeredgecolor=SURFACE, label="Principalement IRD"),
        Line2D([], [], marker="o", ls="", ms=11, color=CNRS, markeredgecolor=SURFACE, label="Principalement CNRS"),
    ]
    leg = ax_a.legend(handles=handles, loc="upper right", frameon=False, fontsize=T_NOTE, handletextpad=0.4, borderpad=0.2, labelspacing=0.55)
    for text in leg.get_texts():
        text.set_color(INK2)

    # Off-scale countries are named rather than silently clipped: three of the 96 context
    # countries fall outside the frame, and widening it to fit them would squash the two
    # groups this figure is about into a sliver.
    if offscale:
        def fmt(n, x, y):
            return (f"{n} ({x:.1f}\u00d7)".replace(".", ",") if x > XMAX
                    else f"{n} ({y:.1f}/M)".replace(".", ","))

    headline(fig, title, deck)
    save(fig, stem, FIGS)
    return mult_ird, len(rows)


if __name__ == "__main__":
    mult_ird, n = build(None, None, "fig3_valeur_euro_nolegend")
    print(f"  value map: {n} pays")
    print(f"  médiane IRD : un euro y achète {mult_ird:.2f}\u00d7 "
          "ce qu'il achète en France")
