# Script de démonstration · soutenance Urban Data Explorer

Durée cible **10 min** + 5 min Q&A. Storytelling > démo technique brute.

## Ouverture (0:00 → 1:00) · le problème

> "Paris, 2024. Prix au mètre carré médian au-dessus de 10 000 €. 20
> arrondissements, 20 réalités économiques. Pour un habitant qui cherche
> un logement, un urbaniste qui planifie un quartier, un investisseur qui
> arbitre entre le 18e et le 6e, l'information existe — mais éclatée
> entre data.gouv, OpenData Paris, INSEE, Airparif. **Comment lire ce
> marché à l'échelle de l'arrondissement, en un seul écran ?**"

→ Slides 1 + 2.

## Notre réponse (1:00 → 1:30)

> "Une plateforme open data complète : un pipeline médaillon Bronze /
> Silver / Gold qui agrège **17 sources** publiques, une API REST
> sécurisée, et un dashboard cartographique interactif avec **4 niveaux
> d'information** et **4 indicateurs composites** que nous avons
> construits."

→ Slide 3.

## Architecture (1:30 → 3:00)

> "L'architecture suit le pattern médaillon. (montrer slide 4)
> En **Bronze**, on ingère brut, partitionné par date d'ingestion. En
> **Silver**, on nettoie avec 6 règles métier, on géocode chaque
> transaction sur son arrondissement par jointure spatiale, on applique
> des window functions pour les rangs et les deltas. En **Gold**, on
> matérialise dans DuckDB des datamarts relationnels prêts à servir
> l'API.
>
> On a fait le choix de Polars + DuckDB au lieu de Spark — le volume
> tient en RAM, on démarre instantanément, et on peut migrer vers
> PySpark sans refonte si on scale à France entière."

→ Slides 4 + 7 + 10.

## Démo live · 1. carte choroplèthe (3:00 → 4:30)

```bash
# Terminal 1
uvicorn api.main:app --reload --port 8000

# Terminal 2
cd frontend && python -m http.server 5500
# → http://localhost:5500
```

> "Connexion `admin` / `admin`. La carte se peint avec l'indicateur
> `prix_m2` par défaut. Je peux changer pour `idx_attractivite` —
> immédiatement, le 6e, le 7e et le 16e sortent du lot. Je clique sur
> le 7e, j'obtiens la fiche complète : population, parc, revenu médian,
> les 4 indicateurs."

## Démo live · 2. couches POI (4:30 → 5:30)

> "J'active la couche **culture** : les musées et monuments
> historiques apparaissent en bleu. J'ajoute **transport** : Vélib,
> Belib, pistes cyclables. C'est le premier niveau d'enrichissement
> qu'on attendait."

## Démo live · 3. timeline (5:30 → 6:30)

> "Le slider du bas rejoue la timeline mois par mois depuis 2019.
> On voit les pics post-confinement, le plateau 2022-2024, le
> décrochage du 7e en 2024."

## Démo live · 4. comparaison (6:30 → 7:30)

> "Je sélectionne 16e vs 19e dans le mode comparaison. Le radar
> 5 dimensions montre instantanément le contraste : 16e dominant en
> attractivité et accessibilité (revenus élevés), 19e dominant en
> effort social. C'est la lecture multi-critère que le sujet
> demandait."

## Choix techniques (7:30 → 8:30)

> "Cinq ADR dans `docs/DECISIONS.md` documentent nos choix :
> - Polars + DuckDB plutôt que Spark
> - Partitionnement year/month/day par date d'ingestion
> - Indicateurs composites en z-score (lecture comparable)
> - DuckDB read-only par requête (concurrence sécurisée)
> - Frontend statique CDN-only (déployable n'importe où)
>
> Côté qualité : 20 tests pytest, lint ruff, CI GitHub Actions sur
> chaque push qui rebuilt le PDF, le PPT et la base démo."

→ Slide 9.

## Déploiement (8:30 → 9:15)

> "Tout est déployable :
> - Frontend → `vercel --prod` (config dans `frontend/vercel.json`)
> - API → image Docker prête, démo locale via `docker compose up`
> - CI/CD via GitHub Actions
>
> La base de démo (`data/demo/urban.duckdb`, 2.8 MB) est commitée :
> n'importe qui clone, lance l'API et le front, et a la démo
> immédiatement sans télécharger les ~500 MB de DVF/POI bruts."

## Conclusion + Q&A (9:15 → 10:00)

> "Pour résumer · 17 sources, 4 indicateurs composites originaux,
> 4 niveaux d'information cartographique, API REST + dashboard
> interactif. Le code est sur **github.com/Adam-Blf/urban-data-explorer**
> avec 19 commits granulaires alternés entre Adam et Emilien, doc
> complète (architecture, data catalog, ADRs, déploiement, schémas
> mermaid). Merci, place aux questions."

→ Slide 12.

---

## Captures à préparer (avant la soutenance)

- `docs/screenshots/01-choropleth-prix.png` · vue d'ouverture, choroplèthe prix
- `docs/screenshots/02-poi-culture.png` · couche culture activée
- `docs/screenshots/03-popup-7e.png` · popup au clic
- `docs/screenshots/04-timeline-2024.png` · slider sur 2024
- `docs/screenshots/05-comparaison-radar.png` · radar 16e vs 19e

Capture rapide via Windows + `Snip & Sketch` (Win + Shift + S).

## Plan B si la démo live échoue

- Garder une **vidéo MP4 de 2 min** prête à lancer en local (capture OBS Studio)
- Garder un **GIF animé** intégré au PPT slide 11 en cas de coupure réseau
- Le PDF du rapport et les screenshots sur clé USB
