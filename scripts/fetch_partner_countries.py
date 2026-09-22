#!/usr/bin/env python3
"""Partner-country counts for the IRD and the CNRS, straight from OpenAlex.

One grouped query per institute: works carrying the institute's ROR, grouped by the country
of every co-affiliated institution. Exact, aggregated server-side, no sampling.

Why these counts are NOT plotted raw: both institutes' biggest partners are the same rich
countries (US, UK, Germany). A raw map of "where do you collaborate" looks nearly identical
for the two - which is precisely why the figure uses each institute's own PROFILE instead
(what share of its international collaboration a country represents), a size-free measure.

Writes data/partner_countries.json.
"""
import json, os, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "data")
MAILTO = "CHANGEME"
RORS = {"IRD": "05q3vnk25", "CNRS": "02feahw73"}

def fetch(ror):
    q = urllib.parse.urlencode(
        {"filter": f"institutions.ror:{ror}", "group_by": "institutions.country_code", "per_page": "200", "mailto": MAILTO}, safe=":|/,")
    for attempt in range(5):
        try:
            with urllib.request.urlopen(
                    f"https://api.openalex.org/works?{q}", timeout=60) as r:
                payload = json.load(r)

            # group keys come back as full URIs
            # ("https://openalex.org/countries/SN"): keep the ISO-3166 alpha-2 tail, which
            # is what the map geometry is keyed on.
            def iso(g):
                return g["key"].rstrip("/").rsplit("/", 1)[-1].upper()

            groups = [g for g in payload["group_by"] if g.get("key")]
            return ({iso(g): g["count"] for g in groups},
                    {iso(g): g["key_display_name"] for g in groups})
        except Exception as exc:
            if attempt == 4:
                raise
            print(f"  retry {attempt + 1} ({exc})")
            time.sleep(2 * (attempt + 1))

def main():
    out = {"source": "OpenAlex", "rors": RORS, "fetched": time.strftime("%Y-%m-%d"), "counts": {}, "names": {}}
    for name, ror in RORS.items():
        print(name)
        counts, names = fetch(ror)
        out["counts"][name] = counts
        out["names"].update(names)
        time.sleep(0.3)

    os.makedirs(DATA, exist_ok=True)
    path = os.path.join(DATA, "partner_countries.json")
    with open(path, "w") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, sort_keys=True)
    print("wrote", path, "|", {k: len(v) for k, v in out["counts"].items()})

if __name__ == "__main__":
    main()
