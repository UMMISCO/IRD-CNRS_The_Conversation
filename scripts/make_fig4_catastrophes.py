#!/usr/bin/env python3
"""Figure 4 - Where the climate hits countries with almost no researchers.

Data: data/climate_disaster_burden.csv (IFRC GO x World Bank x OpenAlex). Offline.
"""
import csv, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import LogLocator, NullFormatter

from style import (CNRS, FIGW, GRID, INK2, IRD, MUTED, RULE, SURFACE, T_BODY, T_NOTE,
                   headline, save)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA, FIGS = os.path.join(ROOT, "data"), os.path.join(ROOT, "figures")

R = {"ird": 946, "cnrs": 10896}     # researchers (HCERES / Cour des comptes)
MIN_EVENTS = 10                     # the Red Cross "country that gets hit" threshold
LEAD_RATIO = 2.5                    # see leads_ird()


def leads_ird(ird_works, cnrs_works):
    """True where the IRD co-publishes at least LEAD_RATIO times more PER RESEARCHER.

    The margin is the point. A bare ">= 1x" test put the cut exactly where the two
    organisations are level, so countries separated by rounding landed on opposite sides. The
    United States came out red at 1,03x - the IRD has 16 658 works there against the CNRS's
    186 767, eleven times fewer - and with it Switzerland at 1,10x, Canada, Sweden, Belgium and
    the Netherlands. Twenty-one countries above 2 000 researchers per million read as IRD-led.

    The data leaves a wide gap to cut in. The IRD's eight partner countries run from 5,6x
    (Chad) to 29,4x (Congo); no Northern country reaches 2,4x. Any threshold between 2,5 and 5
    splits them identically, so 2,5 is the round number nearest the gap: at it, every one of
    the eight partners is red and no country above 2 000 researchers per million is.

    Blue therefore means "the CNRS leads, or the two are close", not "the CNRS leads".

    A country the IRD has never worked with cannot be a lead for it; and a zero CNRS count is
    settled by the comparison rather than by a truthiness test, which is what painted Bhutan
    blue on 5 IRD works against 0.
    """
    if not ird_works:
        return False
    if not cnrs_works:
        return True
    return (ird_works / R["ird"]) / (cnrs_works / R["cnrs"]) >= LEAD_RATIO
BAND = "#F3EAD9"                    # lowest-capacity quintile
SHOW_NAMES = True

# The fifteen countries named on figure 3, so the two figures can be read against each other.
DIRECT = {   # iso2 -> (name, dx, dy, ha, va)
    "MG": ("Madagascar", 8, 15, "left", "bottom"),
    "TD": ("Tchad", 9, 5, "left", "bottom"),
    "BR": ("Brésil", 8, 9, "left", "bottom"),
    "CN": ("Chine", -6, 11, "right", "bottom"),
    "US": ("États-Unis", 0, 15, "center", "bottom"),
    "JP": ("Japon", 12, 5, "left", "center"),
}
RAIL_A, RAIL_B = -6.0, -11.5
RAIL = {     # iso2 -> (name, label x, row)
    "BF": ("Burkina Faso", 15, RAIL_A),
    "CI": ("Côte d'Ivoire", 90, RAIL_A),
    "CG": ("Congo", 300, RAIL_A),
    "IT": ("Italie", 1100, RAIL_A),
    "DE": ("Allemagne", 9000, RAIL_A),
    "GB": ("Royaume-Uni", 3300, RAIL_B),
    # Senegal is boxed in by two larger dots at the same height on either side, so its
    # label goes up into the empty space above the cloud on a diagonal leader
    "SN": ("Sénégal", 200, 47),
}
# Niger and Mali sit 0.015 of a decade apart - one blob - so they share a single label
PAIR = ("NE", "ML", "Niger, Mali", -34, 30, "right", "bottom")


def load():
    with open(os.path.join(DATA, "climate_disaster_burden.csv"), encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        r["evts"] = int(r["go_climate_events_since_2000"] or 0)
        r["dens"] = float(r["researchers_per_million"]) if r["researchers_per_million"] else None
        r["ird"], r["cnrs"] = int(r["ird_works"] or 0), int(r["cnrs_works"] or 0)
        r["lead_ird"] = leads_ird(r["ird"], r["cnrs"])
    return rows

def build(title, deck, stem):
    rows = load()
    known = sorted([r for r in rows if r["dens"] is not None], key=lambda r: r["dens"])
    q1 = known[: len(known) // 5]
    q1_max = q1[-1]["dens"]
    pts = [r for r in rows if r["dens"] is not None and r["evts"] > 0]

    fig, ax = plt.subplots(figsize=(FIGW, 6.7 if title else 5.5))
    fig.subplots_adjust(left=0.125, right=0.965, top=0.765 if title else 0.965, bottom=0.15)
    
    ax.axhline(MIN_EVENTS, color=MUTED, lw=0.9, ls=(0, (4, 3)), zorder=1)
    ax.text(0.78, MIN_EVENTS + 1.2, "10 catastrophes", fontsize=T_NOTE, color=MUTED, style="italic", va="bottom", zorder=2)

    named_iso2 = set(DIRECT.keys()) | set(RAIL.keys()) | set(PAIR[:2])
    for r in pts:
        is_named = r["iso2"] in named_iso2
        point_alpha = 0.92 if is_named else 0.5
        ax.scatter(r["dens"], r["evts"], s=16 + 30 * ((r["ird"] + r["cnrs"]) ** 0.32) / 8,
                   color=IRD if r["lead_ird"] else CNRS, alpha=point_alpha,
                   edgecolor=SURFACE, linewidth=1.6 if is_named else 0.7, zorder=3 if not is_named else 4)

    if SHOW_NAMES:
        def dot(iso):
            m = [r for r in pts if r["iso2"] == iso]
            return (m[0]["dens"], m[0]["evts"]) if m else None

        leader = dict(arrowstyle="-", color=MUTED, lw=0.9, shrinkA=1, shrinkB=5)
        for iso, (name, dx, dy, ha, va) in DIRECT.items():
            xy = dot(iso)
            if xy:
                ax.annotate(name, xy, textcoords="offset points", xytext=(dx, dy), ha=ha, va=va, fontsize=T_NOTE, color=INK2, zorder=6)
        for iso, (name, lx, row) in RAIL.items():
            xy = dot(iso)
            if xy:
                ax.annotate(name, xy, xytext=(lx, row), textcoords="data", ha="center", va="center", fontsize=T_NOTE, color=INK2, arrowprops=leader, zorder=6)
        i1, i2, name, dx, dy, ha, va = PAIR
        if dot(i1) and dot(i2):
            ax.annotate(name, dot(i1), textcoords="offset points", xytext=(dx, dy), ha=ha, va=va, fontsize=T_NOTE, color=INK2, arrowprops=leader, zorder=6)

    ax.set_xscale("log")
    ax.set_xlim(0.7, 2.5e4)
    ax.set_ylim(-15, 80)
    # Plain numbers, not 10^0..10^4, and the minor gridlines restored: without them a log axis
    # reads as a linear one with odd spacing. Narrow no-break space as the French thousands mark.
    ax.set_xticks([1, 10, 100, 1000, 10000])
    ax.set_xticklabels(["1", "10", "100", "1 000", "10 000"])
    ax.xaxis.set_minor_locator(LogLocator(base=10.0, subs=tuple(range(2, 10)), numticks=99))
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.tick_params(labelsize=T_BODY, length=0)
    ax.tick_params(which="minor", length=0)
    ax.set_xlabel("Nombre de chercheurs par million d'habitants\n(échelle logarithmique)", fontsize=T_BODY, color=MUTED, labelpad=7)
    ax.set_ylabel("Nombre de catastrophes climatiques\nrecensées depuis 2000", fontsize=T_BODY, color=MUTED, linespacing=1.4, labelpad=10)
    ax.yaxis.grid(True, color=GRID, lw=0.9, zorder=0)
    ax.xaxis.grid(True, which="minor", color=GRID, lw=0.5, alpha=0.55, zorder=0)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(RULE)

    # colour is the only thing saying which organisation a dot favours, so the key stays on
    handles = [
        Line2D([], [], marker="o", ls="", ms=9, color=IRD, alpha=0.75,
               markeredgecolor=SURFACE, label="Principalement IRD"),
        Line2D([], [], marker="o", ls="", ms=9, color=CNRS, alpha=0.75,
               markeredgecolor=SURFACE, label="Principalement CNRS"),
    ]
    leg = ax.legend(handles=handles, loc="upper right", frameon=False, fontsize=T_NOTE,
                    handletextpad=0.4, borderpad=0.2, labelspacing=0.5)
    for text in leg.get_texts():
        text.set_color(INK2)

    headline(fig, title, deck)
    save(fig, stem, FIGS)

    # the claim in the caption, computed rather than asserted
    hit = [r for r in q1 if r["evts"] >= MIN_EVENTS]
    return len(pts), len(q1), len(hit), sum(r["lead_ird"] for r in hit), q1_max


if __name__ == "__main__":
    n, n_q1, n_hit, n_red, q1_max = build(None, None, "fig4_catastrophes_nolegend")
    print(f"  {n} pays tracés | quintile le moins doté : {n_q1} pays sous {q1_max:.0f}/M")
    print(f"  dont frappés (≥ {MIN_EVENTS} événements) : {n_hit}, "
          f"l'IRD devant dans {n_red} ({100 * n_red / n_hit:.0f} %)")
