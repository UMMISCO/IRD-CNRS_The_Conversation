#!/usr/bin/env python3
"""Figure 2 - The IRD was working on the climate before it was a trend.

Data: data/sdg_timeseries.json, data/sdg_bundles.json (OpenAlex). Offline.
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib.pyplot as plt

from style import (CNRS, FIGW, GRID, INK2, IRD, MUTED, RULE, SURFACE, T_BODY, T_LABEL,
                   T_NOTE, headline, save)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA, FIGS = os.path.join(ROOT, "data"), os.path.join(ROOT, "figures")

GOAL = "13"            # climate action
Y0, Y1 = 2002, 2024    # see the docstring for both cuts
SMOOTH = 1             # +/- 1 year => 3-year moving average


def series(inst, raw):
    """3-year moving average of the SDG share, as a percentage of the institute's output.

    The average is taken on the RATIO OF SUMS (works tagged over works published in the
    window), not the mean of three yearly percentages: the latter would give a year with 400
    publications the same weight as a year with 8 000. The window is clamped to Y1 so that
    the contaminated 2025 counts never leak into the last point.
    """
    tot, tagged = raw[inst]["total"], raw[inst]["per_sdg"][GOAL]
    out = {}
    for year in range(Y0, Y1 + 1):
        window = [y for y in range(year - SMOOTH, year + SMOOTH + 1) if Y0 - 1 <= y <= Y1]
        num = sum(tagged.get(str(y), 0) for y in window)
        den = sum(tot.get(str(y), 0) for y in window)
        out[year] = 100 * num / den if den else None
    return out


def bundle_share(inst, raw, bundles, year):
    num = bundles["counts"][inst]["env_dev"].get(str(year), 0)
    den = raw[inst]["total"].get(str(year), 0)
    return 100 * num / den if den else 0


def build(title, deck, stem):
    raw = json.load(open(os.path.join(DATA, "sdg_timeseries.json")))["institutes"]
    bundles = json.load(open(os.path.join(DATA, "sdg_bundles.json")))
    ird, cnrs = series("IRD", raw), series("CNRS", raw)

    years_all = list(range(Y0, Y1 + 1))
    ratios = [ird[y] / cnrs[y] for y in years_all]
    r_lo, r_hi = min(ratios), max(ratios)

    fig, ax = plt.subplots(figsize=(FIGW, 5.3))
    head = 0.775 if title else 0.965
    fig.subplots_adjust(left=0.115, right=0.875, top=head, bottom=0.185)

    years = years_all
    ax.plot(years, [ird[y] for y in years], color=IRD, lw=2.6, zorder=4, solid_capstyle="round")
    ax.plot(years, [cnrs[y] for y in years], color=CNRS, lw=2.6, zorder=4, solid_capstyle="round")

    # --- 2015: the year the subject acquired its label
    ax.axvline(2015, color=RULE, lw=1.0, zorder=1)
    ax.text(2015 + 0.3, 10, "2015 : accord de Paris\net adoption des\nObjectifs de Développement Durable",
            ha="left", va="top", fontsize=T_NOTE, color=MUTED, linespacing=1.35)

    # --- value points: the start of the series, 2015, and the end.
    marks = [
        (Y0, ird[Y0], IRD, Y0 + 0.30, ird[Y0] + 0.22, "left", "bottom"),
        (Y0, cnrs[Y0], CNRS, Y0 + 0.30, cnrs[Y0] - 0.22, "left", "top"),
        (2015, ird[2015], IRD, 2014.75, ird[2015] + 0.20, "right", "bottom"),
        (2015, cnrs[2015], CNRS, 2014.75, cnrs[2015] - 0.40, "right", "top"),
        (Y1, ird[Y1], IRD, None, None, None, None),
        (Y1, cnrs[Y1], CNRS, None, None, None, None),
    ]
    for x, y, col, tx, ty, ha, va in marks:
        # a surface-coloured ring keeps the dot readable where it sits on the shaded band
        ax.plot([x], [y], "o", ms=9, color=col, markeredgecolor=SURFACE, markeredgewidth=2.2, zorder=7)
        if tx is not None:
            ax.text(tx, ty, f"{y:.1f} %".replace(".", ","), ha=ha, va=va, fontsize=T_BODY, fontweight="bold", color=col, zorder=8)

    # --- direct labels
    for name, ser, col in (("IRD", ird, IRD), ("CNRS", cnrs, CNRS)):
        ax.text(Y1 + 0.45, ser[Y1], f"  {name}\n  {ser[Y1]:.1f} %".replace(".", ","),
                color=col, fontsize=T_LABEL, fontweight="bold", va="center", ha="left",
                linespacing=1.3)

    ax.set_xlim(Y0 - 0.4, Y1 + 0.4)
    ax.set_ylim(0, max(max(ird.values()), max(cnrs.values())) * 1.32)
    ax.set_xticks([2002, 2006, 2010, 2014, 2018, 2022, 2024])
    ax.set_xticklabels(["2002", "2006", "2010", "2014", "2018", "2022", "2024"], fontsize=T_BODY)
    ax.set_yticks([0, 2, 4, 6, 8])
    ax.set_yticklabels(["", "2 %", "4 %", "6 %", "8 %"], fontsize=T_BODY)
    ax.set_ylabel("Part des publications\nconsacrées à l'objectif\n\"Lutte contre le changement climatique\"", fontsize=T_BODY, color=MUTED, linespacing=1.4, labelpad=12)
    ax.yaxis.grid(True, color=GRID, lw=0.9, zorder=0)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(RULE)
    ax.tick_params(length=0)

    e_ird = bundle_share("IRD", raw, bundles, Y1)
    e_cnrs = bundle_share("CNRS", raw, bundles, Y1)

    headline(fig, title, deck)
    save(fig, stem, FIGS)
    return ird, cnrs, r_lo, r_hi, e_ird, e_cnrs


if __name__ == "__main__":
    ird, cnrs, r_lo, r_hi, e_ird, e_cnrs = build(None, None, "fig2_anteriorite_climat_nolegend")    
    print(f"  IRD {Y0}: {ird[Y0]:.2f}%  {Y1}: {ird[Y1]:.2f}%")
    print(f"  CNRS {Y0}: {cnrs[Y0]:.2f}%  {Y1}: {cnrs[Y1]:.2f}%")
    print(f"  IRD/CNRS ratio over {Y0}-{Y1}: min {r_lo:.2f}  max {r_hi:.2f}")
    print(f"  env_dev bundle {Y1}: IRD {e_ird:.1f}%  CNRS {e_cnrs:.1f}%")
