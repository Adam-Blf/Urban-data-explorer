# 🧠 Vision & Roadmap IA (V2)

Ce document détaille les perspectives d'évolution du projet **Urban Data Explorer** vers un système intelligent de recommandation et de prédiction immobilière.

## 1. Modélisation Prédictive (Machine Learning)
L'objectif principal de la V2 est de passer d'un outil de visualisation descriptive à un outil d'aide à la décision prédictif.

### Algorithmes envisagés
*   **XGBoost / Random Forest** : Pour prédire l'évolution des prix au m² à 1 an par quartier, en se basant sur les séries temporelles de la base DVF et les indicateurs de tension urbaine.
*   **Régression Géographique Pondérée (GWR)** : Pour comprendre comment la proximité d'un service (ex: nouvelle ligne de métro ou station Belib') impacte localement le prix du foncier.

## 2. Système de Recommandation (Intelligence Urbaine)
Développement d'un profilage utilisateur (moteur de suggestion) :
*   *Scénario A* : "Je suis une famille avec 2 enfants, je cherche un quartier avec un Indice de Qualité de Vie > 80 et une forte densité d'écoles."
*   *Scénario B* : "Je suis un investisseur, je cherche les zones où la Tension Immobilière est moyenne mais où le Patrimoine Culturel est en forte croissance."

## 3. Scalabilité Big Data
Pour traiter l'ensemble de la base DVF France (plusieurs millions de lignes) :
*   **Migration vers PySpark** : Utilisation de Spark SQL pour les agrégations lourdes sur cluster.
*   **Stockage PostGIS** : Remplacer les fichiers Flat JSON par une base de données relationnelle spatiale pour des requêtes de proximité en temps réel (< 100ms).

## 4. Analyse de Sentiment (NLP)
*   Scraping des avis de quartiers (ex: Ville-Ideale.fr) pour enrichir l'Indice de Qualité de Vie avec une dimension subjective (Analyse de sentiment via BERT).

---
**Équipe DE2 - Urban Data Explorer**
