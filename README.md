# Figures pour *The Conversation* — fusion IRD–CNRS

Figures de l'article « Fusion IRD–CNRS : ce que révèlent les données sur les spécificités de la recherche en partenariat ».

## Utilisation

Dépendances : Python 3 et `matplotlib`.

```bash
python3 scripts/make_all.py
```

Les figures sont créées dans le dossier `figures/`. Les scripts `fetch_*.py` rafraîchissent les données (réseau requis). Pour ceux qui interrogent OpenAlex, remplacer d'abord `MAILTO = "CHANGEME"` par une adresse e-mail (*polite pool*).

## Figure 1 — les deux géographies de co-publication

Pour créer la figure `figures/fig1_carte_deux_geographies_nolegend.png`, lancez le script :
```bash
python3 scripts/make_fig1_carte.py
```
La figure se base sur :
- `data/partner_countries.json` : pour l'IRD et le CNRS, le nombre de publications co-signées avec chaque pays, tiré d'[OpenAlex](https://openalex.org) (ROR `05q3vnk25` et `02feahw73`). Chaque pays est coloré selon le rapport entre la part qu'il occupe dans les co-publications internationales de l'IRD et celle qu'il occupe dans celles du CNRS.
- La projection de la map utilise la *Equal Earth projection* dans le fichier `data/world_countries.json`.

## Figure 1 bis — les structures conjointes, pays par pays

Pour créer la figure `figures/fig1bis_carte_structures_nolegend.png`, lancez le script :
```bash
python3 scripts/make_fig1bis_carte_structures.py
```

La figure se base sur `data/structures_by_country.csv`, relevé à la main, qui donne pour chaque pays le nombre de structures conjointes de chaque organisme :
- IRD : LMI et JEAI, relevés le 2026-09-17 sur les pages [LMI](https://www.ird.fr/laboratoires-mixtes-internationaux-lmi) et [JEAI](https://www.ird.fr/jeunes-equipes-associees-lird-jeai) de l'IRD ;
- CNRS : les 62 IRL de la liste reconstituée dans IRD-impact (`analyses/datasets/cnrs_irl_labs.csv`, sur les ~80 annoncés par le CNRS), plus les 27 UMIFRE
  (cotutelle CNRS / ministère des Affaires étrangères), relevées en Septembre 2026 sur [Wikipédia](https://fr.wikipedia.org/wiki/Unit%C3%A9s_mixtes_des_instituts_fran%C3%A7ais_de_recherche_%C3%A0_l%27%C3%A9tranger) faute de liste officielle consolidée.

Une structure présente dans plusieurs pays est comptée dans chacun d'eux. Les colonnes `cnrs_irl` et `cnrs_umifre` sont séparées, ce qui permet de refaire la carte sans les UMIFRE. Le fond de carte est le même qu'en figure 1.

## Figure 2 — l'antériorité sur le climat

Pour créer la figure `figures/fig2_anteriorite_climat_nolegend.png`, lancez le script :
```bash
python3 scripts/make_fig2_anteriorite.py
```

La figure se base sur deux fichiers tirés d'OpenAlex :

- `data/sdg_timeseries.json` : le nombre de publications annuelles de l'IRD et du CNRS, au total et par Objectif de développement durable (ODD), selon l'étiquetage ODD d'OpenAlex.
- `data/sdg_bundles.json` : les mêmes comptes pour des groupes d'ODD, sans doublons (groupe environnement et développement : ODD 1, 2, 6, 13, 14, 15).

## Figure 3 — ce qu'un euro achète

Pour créer la figure `figures/fig3_valeur_euro_nolegend.png`, lancez le script :
```bash
python3 scripts/make_fig3_euro.py
```

La figure se base sur trois fichiers :

- `data/ppp_all_countries.csv` : ce qu'un euro de recherche achète dans chaque pays par rapport à la France, calculé à partir des indicateurs `PA.NUS.PPP` et `PA.NUS.FCRF` de la Banque mondiale (2025).
- `data/euro_value_map.csv` : les pays partenaires types de chaque organisme et leur nombre de chercheurs par million d'habitants.
- `data/climate_disaster_burden.csv` : les publications de l'IRD et du CNRS par pays (basée sur OpenAlex).

## Figure 4 — catastrophes climatiques et chercheurs

Pour créer la figure `figures/fig4_catastrophes_nolegend.png`, lancez le script :
```bash
python3 scripts/make_fig4_catastrophes.py
```

La figure se base sur `data/climate_disaster_burden.csv`, qui croise trois sources par pays :
- les catastrophes climatiques survenues depuis 2000 ([IFRC GO](https://go.ifrc.org)) ;
- l'exposition de la population et le nombre de chercheurs par million d'habitants (Banque mondiale) ;
- les publications de l'IRD et du CNRS (OpenAlex).

## Licence

Voir [`LICENSE`](LICENSE) :

- **Code** (`scripts/`) — licence MIT ;
- **Données et figures** (`data/`, `figures/`) — CC BY 4.0. Attribution suggérée :
  « UMMISCO (IRD & Sorbonne Université), IRD–CNRS reproducibility dataset, 2026, recompiled from public sources (OpenAlex, theses.fr, HCERES, IRD Programme LMI, World Bank). CC BY 4.0. »

Les sources publiques d'origine conservent leurs propres conditions (OpenAlex CC0, Banque mondiale, theses.fr, HAL, HCERES).
