#!/usr/bin/env python3
"""World Bank purchasing-power series for every country, to draw the context cloud on fig 3.

Same construction as data/euro_value_map.csv, checked against it on seven countries:
    multiplier = (PA.NUS.FCRF / PA.NUS.PPP)_country / (PA.NUS.FCRF / PA.NUS.PPP)_France
i.e. how much more (or less) research a euro buys there than in France, at 2025 values.

Writes data/ppp_all_countries.csv. Needs network; the figure scripts are offline.
"""
import csv, json, os, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "data")
YEAR = 2025

def fetch(indicator):
    url = (f"https://api.worldbank.org/v2/country/all/indicator/{indicator}" f"?format=json&date={YEAR}&per_page=400")
    for attempt in range(5):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                payload = json.load(r)
            return {row["countryiso3code"]: (row["country"]["id"], row["country"]["value"], row["value"])
                    for row in payload[1] if row["countryiso3code"] and row["value"]}
        except Exception as exc:
            if attempt == 4:
                raise
            print(f"  retry {attempt + 1} ({exc})")
            time.sleep(2 * (attempt + 1))

def main():
    ppp, fcrf = fetch("PA.NUS.PPP"), fetch("PA.NUS.FCRF")
    both = sorted(set(ppp) & set(fcrf))
    level = {c: fcrf[c][2] / ppp[c][2] for c in both}
    fr = level["FRA"]
    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, "ppp_all_countries.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["iso3", "iso2", "country", "year", "ppp_mult_vs_fr"])
        for c in both:
            w.writerow([c, ppp[c][0], ppp[c][1], YEAR, round(level[c] / fr, 3)])
    print(f"wrote data/ppp_all_countries.csv | {len(both)} pays, {YEAR}")

if __name__ == "__main__":
    main()
