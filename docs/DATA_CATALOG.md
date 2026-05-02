# Data Catalog · Urban Data Explorer

Référentiel des sources, leur licence, leur fraîcheur, leur usage métier.

## Sources cœur (analyse logement)

| Clé | Dataset | Provider | Licence | Volume Paris | Granularité | Fraîcheur | Usage |
|---|---|---|---|---|---|---|---|
| `dvf` | DVF géolocalisé | data.gouv.fr (DGFiP) | Licence Ouverte 2.0 | ~50k mutations / an · ~250k 2019-2024 | mutation | trimestrielle | prix m², volumes, timeline |
| `social_housing` | Logements sociaux financés à Paris | OpenData Paris | ODbL | ~5 000 lignes | programme | annuelle | indice effort social |
| `filosofi` | Filosofi 2021 (revenus, inégalités) | INSEE | Licence Ouverte 2.0 | 1 ligne / commune | commune | 2 ans | indice accessibilité |
| `arrondissements` | Arrondissements GeoJSON | OpenData Paris | ODbL | 20 polygones | arrondissement | statique | choroplèthe + jointure spatiale |
| `air_quality` | Qualité air station Paris Centre | Airparif via OpenData Paris | ODbL | ~30k mesures horaires | station × heure | horaire | composite environnement |

## Sources POI (4 niveaux d'information cartographique)

| Catégorie | Clé feeder | Dataset OpenData / data.gouv | Volume | Champ géo |
|---|---|---|---|---|
| transport | `velib_stations` | Vélib · stations | ~1 400 | `geo_point_2d` |
| transport | `belib_bornes`   | Belib · bornes IRVE | ~600 | `geo_point_2d` |
| transport | `amenagements_cyclables` | Aménagements cyclables Paris | ~12 000 | `geo_shape` |
| service public | `ecoles_elementaires` | Écoles élémentaires Paris | ~330 | `geo_point_2d` |
| service public | `colleges` | Collèges Paris | ~120 | `geo_point_2d` |
| service public | `sanisettes` | Toilettes publiques Paris | ~750 | `geo_point_2d` |
| commerce | `marches` | Marchés découverts Paris | ~80 | `geo_point_2d` |
| culture | `que_faire_paris` | Que Faire à Paris (événements) | ~10 000 / an | `geo_point_2d` |
| culture | `musees_france` | Musées de France (data.gouv) | ~150 IDF | `latitude/longitude` |
| culture | `monuments_historiques` | Immeubles protégés MH (data.gouv) | ~3 800 IDF | `latitude/longitude` |
| santé | `hopitaux_idf` | Établissements hospitaliers IDF (data.gouv) | ~370 IDF | `latitude/longitude` |
| environnement | `espaces_verts` | Espaces verts publics Paris | ~3 000 | `geo_shape` (polygone) |

## 4 indicateurs composites (force de proposition)

Construits dans `kpi_arrondissement` à partir des 17 sources ci-dessus.

| Indicateur | Sources combinées | Lecture |
|---|---|---|
| `idx_accessibilite` | DVF (prix m²) + Filosofi (revenu médian) | >0.6 = accessible · <0.3 = très tendu |
| `idx_tension` | DVF (transactions) + Population/Parc logements | rotation pour 1 000 logements |
| `idx_effort_social` | Logements sociaux + Population | unités sociales pour 10 000 hab. |
| `idx_attractivite` | z-score combiné · accessibilité (30%) + densité POI culture/transport/santé/env (40%) + effort social (15%) − tension (15%) | échelle z, 0 = moyenne Paris |

## Fréquence d'ingestion recommandée

| Source | Fréquence | Justification |
|---|---|---|
| DVF | trimestrielle | publication officielle DGFiP |
| Logements sociaux | annuelle | mise à jour annuelle dataset |
| Filosofi | bisannuelle | INSEE diffusé tous les 2 ans |
| Arrondissements | statique (1×/an de safety) | géométrie quasi-immuable |
| Air quality | horaire (cron) | mesures temps réel |
| Vélib stations | hebdomadaire | nouvelles stations / fermetures |
| Belib | hebdomadaire | déploiement progressif |
| Écoles, collèges | annuelle | rentrée scolaire |
| Marchés | annuelle | révision rare |
| Que faire à Paris | quotidienne | flux événementiel |
| Musées / Monuments | trimestrielle | mises à jour rares mais publication régulière |
| Hôpitaux | annuelle | restructuration rare |
| Espaces verts | annuelle | inventaire DEVE |
| Sanisettes | trimestrielle | maintenance / ouverture |

Toutes les ingestions sont **idempotentes** par partition `year/month/day` · rejouer le même jour écrase la même partition Bronze sans pollution.

## Qualité

- **Validation** au passage Silver (5+ règles métier sur DVF), exemple ·
  - `valeur_fonciere` ∈ [50 000, 50 000 000] €
  - `surface_reelle_bati` > 9 m²
  - point géographique dans la bbox Paris
- **Géocodage** · jointure spatiale point-in-polygon Shapely (pas de service tiers requis).
- **Logs rejets** · `logs/processor_<source>_<runid>.txt` détaille les rejets par règle.

## Licence des données restituées

Données publiées sous **Licence Ouverte 2.0 / ODbL** par les producteurs · le projet conserve cette licence pour les jeux dérivés (datamarts).
