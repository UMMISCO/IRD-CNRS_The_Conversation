#!/usr/bin/env python3
"""Distinct yearly counts for candidate "sustainability" SDG bundles.

Per-SDG counts cannot simply be summed - a work carrying both SDG 13 and SDG 15 would be
counted twice. OpenAlex's pipe (`|`) is an OR inside one filter, so each query below returns
DISTINCT works carrying at least one goal of the bundle.

The bundles are defined by a principle stated in advance, not chosen after seeing the result:
  env_dev  - the environment + basic-needs goals (1, 2, 6, 13, 14, 15). Includes SDG 6
             (clean water), on which the CNRS is AHEAD of the IRD: dropping it would have
             flattered our own argument.
  climate  - the three biosphere goals (13, 14, 15).

Writes data/sdg_bundles.json.
"""
import json, os, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "data")
MAILTO = "CHANGEME"
API = "https://api.openalex.org/works"

RORS = {"IRD": "05q3vnk25", "CNRS": "02feahw73"}
BUNDLES = {
    "env_dev": [1, 2, 6, 13, 14, 15],
    "climate": [13, 14, 15],
}

def group_by_year(filters):
    q = urllib.parse.urlencode(
        {"filter": ",".join(filters), "group_by": "publication_year", "mailto": MAILTO}, safe=":|/,")
    for attempt in range(5):
        try:
            with urllib.request.urlopen(f"{API}?{q}", timeout=60) as r:
                payload = json.load(r)
            return {int(g["key"]): g["count"] for g in payload["group_by"]
                    if g["key"] and str(g["key"]).isdigit()}
        except Exception as exc:
            if attempt == 4:
                raise
            print(f"  retry {attempt + 1} ({exc})")
            time.sleep(2 * (attempt + 1))

def main():
    out = {"source": "OpenAlex", "bundles": BUNDLES, "fetched": time.strftime("%Y-%m-%d"), "counts": {}}
    for name, ror in RORS.items():
        out["counts"][name] = {}
        for bundle, goals in BUNDLES.items():
            print(f"{name} / {bundle}")
            uris = "|".join(f"https://metadata.un.org/sdg/{n}" for n in goals)
            out["counts"][name][bundle] = group_by_year([f"institutions.ror:{ror}", f"sustainable_development_goals.id:{uris}"])
            time.sleep(0.3)

    os.makedirs(DATA, exist_ok=True)
    path = os.path.join(DATA, "sdg_bundles.json")
    with open(path, "w") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, sort_keys=True)
    print("wrote", path)

if __name__ == "__main__":
    main()
