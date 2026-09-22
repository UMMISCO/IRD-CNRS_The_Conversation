#!/usr/bin/env python3
"""Fetch, from OpenAlex, the yearly publication counts needed for the "sustainability
came first at the IRD" time chart.

For each institute (by ROR) three server-side aggregations, all exact (no sampling):
  1. total works per year                        -> denominator
  2. works carrying >= 1 UN SDG tag, per year    -> distinct count (pipe = OR)
  3. works per year for each of the 17 SDGs      -> thematic composition

OpenAlex assigns SDG tags with a classifier applied to the whole corpus regardless of
publication date, so a 1995 paper can carry SDG 13. The tag describes the SUBJECT, it is
not a claim that the authors used SDG vocabulary - which is exactly what we need to ask
"who was working on these questions before they had a name".

Writes data/sdg_timeseries.json. Needs network; run once, the figure scripts are offline.
"""
import json, os, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "data")
MAILTO = "CHANGEME"
API = "https://api.openalex.org/works"

RORS = {"IRD": "05q3vnk25", "CNRS": "02feahw73"}
SDGS = {n: f"https://metadata.un.org/sdg/{n}" for n in range(1, 18)}
SDG_LABELS = {
    1: "Pas de pauvreté", 2: "Faim « zéro »", 3: "Santé et bien-être",
    4: "Éducation de qualité", 5: "Égalité entre les sexes",
    6: "Eau propre et assainissement", 7: "Énergie propre",
    8: "Travail décent et croissance", 9: "Industrie et infrastructure",
    10: "Inégalités réduites", 11: "Villes et communautés durables",
    12: "Consommation et production responsables", 13: "Lutte contre le changement climatique",
    14: "Vie aquatique", 15: "Vie terrestre", 16: "Paix et justice",
    17: "Partenariats pour les objectifs",
}


def group_by_year(filters):
    """One grouped query -> {year: count}. Exact, aggregated server-side."""
    q = urllib.parse.urlencode(
        {"filter": ",".join(filters), "group_by": "publication_year", "mailto": MAILTO}, safe=":|/,")
    for attempt in range(5):
        try:
            with urllib.request.urlopen(f"{API}?{q}", timeout=60) as r:
                payload = json.load(r)
            return {int(g["key"]): g["count"] for g in payload["group_by"]
                    if g["key"] and str(g["key"]).isdigit()}
        except Exception as exc:                       # transient 429/5xx
            if attempt == 4:
                raise
            print(f"  retry {attempt + 1} ({exc})")
            time.sleep(2 * (attempt + 1))


def main():
    out = {"source": "OpenAlex", "rors": RORS, "sdg_labels": SDG_LABELS, "fetched": time.strftime("%Y-%m-%d"), "institutes": {}}

    for name, ror in RORS.items():
        base = f"institutions.ror:{ror}"
        print(f"{name}: total by year")
        total = group_by_year([base])

        print(f"{name}: any-SDG by year")
        any_sdg = group_by_year([base, "sustainable_development_goals.id:" + "|".join(SDGS.values())])

        per_sdg = {}
        for n, uri in SDGS.items():
            print(f"{name}: SDG {n}")
            per_sdg[n] = group_by_year([base, f"sustainable_development_goals.id:{uri}"])
            time.sleep(0.2)

        out["institutes"][name] = {"total": total, "any_sdg": any_sdg, "per_sdg": per_sdg}

    os.makedirs(DATA, exist_ok=True)
    path = os.path.join(DATA, "sdg_timeseries.json")
    with open(path, "w") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, sort_keys=True)
    print("wrote", path)


if __name__ == "__main__":
    main()
