from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

from fpdf import FPDF, XPos, YPos


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "rapport.pdf"
LOGO = ROOT / "assets" / "efrei-blanc.png"
FONT_DIR = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"


class ReportPDF(FPDF):
    """Small branded PDF helper with a shared header and footer."""

    def header(self) -> None:  # noqa: D401
        if self.page_no() == 1:
            return
        self.set_fill_color(11, 31, 58)
        self.rect(0, 0, self.w, 18, style="F")
        self.set_text_color(255, 255, 255)
        self.set_font("Arial", "B", 11)
        self.set_y(5)
        self.cell(0, 6, "Urban Data Explorer | Rapport de soutenance", align="C")
        self.ln(14)

    def footer(self) -> None:  # noqa: D401
        self.set_y(-15)
        self.set_text_color(110, 110, 110)
        self.set_font("Arial", "", 9)
        self.cell(0, 8, f"Page {self.page_no()}", align="C")


def load_fonts(pdf: ReportPDF) -> None:
    """Register Windows Arial fonts so accents render correctly."""

    pdf.add_font("Arial", "", str(FONT_DIR / "arial.ttf"))
    pdf.add_font("Arial", "B", str(FONT_DIR / "arialbd.ttf"))
    pdf.add_font("Arial", "I", str(FONT_DIR / "ariali.ttf"))
    pdf.add_font("Arial", "BI", str(FONT_DIR / "arialbi.ttf"))


def ensure_space(pdf: ReportPDF, height: float) -> None:
    if pdf.get_y() + height > pdf.page_break_trigger:
        pdf.add_page()


def title_block(pdf: ReportPDF, title: str, subtitle: str) -> None:
    pdf.set_fill_color(11, 31, 58)
    pdf.rect(0, 0, pdf.w, 62, style="F")
    if LOGO.exists():
        pdf.image(str(LOGO), x=pdf.w - 56, y=10, w=42)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 24)
    pdf.set_xy(18, 18)
    pdf.multi_cell(0, 12, title)
    pdf.set_font("Arial", "", 13)
    pdf.set_x(18)
    pdf.multi_cell(0, 8, subtitle)
    pdf.ln(18)


def section_title(pdf: ReportPDF, title: str, accent: tuple[int, int, int] = (227, 6, 19)) -> None:
    ensure_space(pdf, 16)
    pdf.set_fill_color(*accent)
    pdf.rect(pdf.l_margin, pdf.get_y(), 4, 8, style="F")
    pdf.set_xy(pdf.l_margin + 8, pdf.get_y() - 1)
    pdf.set_text_color(11, 31, 58)
    pdf.set_font("Arial", "B", 15)
    pdf.cell(0, 8, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1)


def paragraph(pdf: ReportPDF, text: str, font_size: int = 11, color: tuple[int, int, int] = (40, 50, 60)) -> None:
    pdf.set_text_color(*color)
    pdf.set_font("Arial", "", font_size)
    pdf.multi_cell(0, 6, text)
    pdf.ln(1)


def bullets(pdf: ReportPDF, items: Iterable[str]) -> None:
    pdf.set_font("Arial", "", 11)
    pdf.set_text_color(40, 50, 60)
    for item in items:
        pdf.cell(5)
        pdf.cell(0, 6, f"• {item}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1)


def key_value_table(pdf: ReportPDF, rows: list[tuple[str, str]], widths: tuple[float, float] = (52, 124)) -> None:
    pdf.set_font("Arial", "", 10)
    for left, right in rows:
        ensure_space(pdf, 10)
        pdf.set_fill_color(243, 246, 250)
        pdf.set_text_color(11, 31, 58)
        pdf.cell(widths[0], 8, left, border=1, fill=True)
        pdf.set_text_color(35, 44, 56)
        x = pdf.get_x()
        y = pdf.get_y()
        pdf.multi_cell(widths[1], 8, right, border=1)
        pdf.set_xy(pdf.l_margin, y + 8)
    pdf.ln(2)


def score_table(pdf: ReportPDF) -> None:
    rows = [
        ("C1.1", "Modèle relationnel PostgreSQL normalisé, datamarts et intégrité."),
        ("C1.2", "Cassandra pour les événements temps réel et les objets semi-structurés."),
        ("C1.3", "Bronze/Silver/Gold sur HDFS, permissions, zones et séparation des usages."),
        ("C1.4", "Spark scalable, HDFS partitionné, restart policies et healthchecks Docker."),
        ("C2.1", "API FastAPI documentée avec OpenAPI, Swagger, ReDoc et clé optionnelle."),
        ("C2.2", "Streaming Kafka -> Spark Structured Streaming -> HDFS + Cassandra."),
        ("C2.3", "Polars normalise les sources Paris/data.gouv vers une structure commune."),
        ("C2.4", "Pipelines optimisés, indicateurs de suivi et résilience de bout en bout."),
    ]
    key_value_table(pdf, rows, widths=(18, 150))


def sources_table(pdf: ReportPDF) -> None:
    rows = [
        ("Espaces verts", "Paris Open Data"),
        ("Stationnement emprises", "Paris Open Data"),
        ("Belib", "Paris Open Data"),
        ("Velib stations", "Paris Open Data"),
        ("Sanisettes", "Paris Open Data"),
        ("Aménagements cyclables", "Paris Open Data"),
        ("Chantiers perturbants", "Paris Open Data"),
        ("Écoles / collèges", "Paris Open Data"),
        ("Marchés découverts", "Paris Open Data"),
        ("Loisirs / que faire à Paris", "Paris Open Data"),
        ("Logements sociaux", "Paris Open Data"),
        ("Immeubles protégés", "data.gouv.fr"),
        ("Musées de France", "data.gouv.fr"),
        ("Hôpitaux franciliens", "data.gouv.fr"),
        ("Médecins HAS", "data.gouv.fr"),
    ]
    key_value_table(pdf, rows, widths=(62, 108))


def build_pdf(path: Path) -> None:
    """Generate a detailed EFREI-branded PDF report."""

    pdf = ReportPDF(format="A4")
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.set_margins(16, 16, 16)
    load_fonts(pdf)
    pdf.set_title("Urban Data Explorer - Rapport de soutenance")
    pdf.set_author("Copilot")
    pdf.set_subject("Rapport détaillé brandé EFREI")
    pdf.set_keywords("EFREI, RNCP40875, data engineering, FastAPI, Spark, Hadoop")

    pdf.add_page()
    title_block(
        pdf,
        "Urban Data Explorer",
        "Rapport de soutenance détaillé - Bloc 1 RNCP40875 | EFREI",
    )

    paragraph(
        pdf,
        "Ce rapport présente une architecture data complète, pensée pour une soutenance solide et une exploitation locale proche d'un déploiement de production. "
        "Le projet couvre l'ingestion multi-sources, la normalisation, les datamarts, le streaming et l'exposition API, avec une identité visuelle EFREI.",
    )

    section_title(pdf, "1. Résumé exécutif")
    bullets(
        pdf,
        [
            "Architecture data Paris multi-sources, orientée métier et démonstration.",
            "Bronze/Silver/Gold avec HDFS, Spark et Polars pour la transformation.",
            "Datamarts relationnels dans PostgreSQL et événements temps réel dans Cassandra.",
            "API FastAPI documentée, sécurisable et prête pour une exposition contrôlée.",
            "Frontend moderne, responsive et orienté pilotage de soutenance.",
        ],
    )

    section_title(pdf, "2. Objectif du projet")
    paragraph(
        pdf,
        "L'objectif est de livrer un socle data universellement accessible, capable de rassembler des jeux de données urbains, culturels, sociaux et de mobilité "
        "autour des arrondissements parisiens. La solution doit démontrer la conception d'une base relationnelle, d'une base NoSQL, d'un lac de données, "
        "d'infrastructures scalables et d'une API documentée.",
    )

    section_title(pdf, "3. Branding EFREI et rendu")
    key_value_table(
        pdf,
        [
            ("Identité visuelle", "Couleurs bleu marine et rouge institutionnel, logo EFREI en couverture."),
            ("Typographie", "Arial pour garantir un rendu stable sur Windows et une bonne lisibilité."),
            ("Style", "Grands espaces, sections structurées, tableaux et encadrés de synthèse."),
            ("Usage", "Rapport prêt à être joint au dossier de soutenance et transmis en PDF."),
        ],
        widths=(45, 115),
    )

    section_title(pdf, "4. Jeux de données intégrés")
    paragraph(
        pdf,
        "Le projet s'appuie sur les sources identifiées sur la machine et structurées dans un catalogue interne. "
        "Les sources Paris Open Data alimentent les indicateurs opérationnels, tandis que data.gouv.fr complète la couche culture et santé.",
    )
    sources_table(pdf)

    section_title(pdf, "5. Architecture technique")
    key_value_table(
        pdf,
        [
            ("Bronze", "Snapshots bruts par source dans HDFS avec métadonnées d'ingestion."),
            ("Silver", "Nettoyage, typage, normalisation et enrichissement des colonnes communes."),
            ("Gold", "Datamarts arrondissements dans PostgreSQL et exports parquet sur HDFS."),
            ("Streaming", "Kafka alimente Spark Structured Streaming puis HDFS et Cassandra."),
            ("API", "FastAPI expose le catalogue, la supervision et les données métier."),
            ("Frontend", "Dashboard immersif avec KPI, pipeline, catalogue et événements."),
        ],
        widths=(34, 126),
    )

    section_title(pdf, "6. Pipelines de données")
    bullets(
        pdf,
        [
            "Le job Bronze télécharge les exports ou métadonnées et les stocke avec une date de snapshot.",
            "Le job Silver applique la même logique de normalisation à toutes les sources intégrées.",
            "Le job Gold agrège les signaux par arrondissement, calcule des indices et charge PostgreSQL.",
            "Le streaming Kafka est persisté simultanément dans HDFS et Cassandra pour la consultation rapide.",
        ],
    )

    section_title(pdf, "7. API documentée")
    paragraph(
        pdf,
        "L'API expose des routes groupées dans Swagger et ReDoc avec une description par tag. "
        "Les endpoints principaux permettent d'interroger le catalogue, le datamart Gold, le dernier run pipeline et les derniers événements temps réel.",
    )
    key_value_table(
        pdf,
        [
            ("GET /", "Point d'entrée simple avec liens vers la documentation."),
            ("GET /health", "Contrôle de disponibilité."),
            ("GET /catalog/sources", "Catalogue des sources intégrées."),
            ("GET /datamarts/dashboard", "Vue KPI arrondissement."),
            ("GET /datamarts/timeline", "Tendance mensuelle des volumes."),
            ("GET /pipeline/latest", "Dernier run de pipeline."),
            ("GET /events/recent", "Événements récents depuis Cassandra."),
        ],
        widths=(48, 112),
    )

    section_title(pdf, "8. Frontend de démonstration")
    bullets(
        pdf,
        [
            "Hero visuel fort et hiérarchie claire pour la soutenance.",
            "Filtres de catalogue, cartes KPI et mini-dashboard arrondissement.",
            "Graphique SVG sans dépendance lourde pour la charge par mois.",
            "Bloc supervision, événements temps réel et token local optionnel.",
            "Responsive design adapté à un écran projeté ou à un laptop.",
        ],
    )

    section_title(pdf, "9. Production et robustesse")
    key_value_table(
        pdf,
        [
            ("Docker Compose", "Restart policies, healthchecks et séparation des services."),
            ("Sécurité", "Token API optionnel via variable d'environnement."),
            ("Observabilité", "État du pipeline, endpoints health et retour d'erreur lisible."),
            ("Déploiement", "Composants prêts à être reconstruits sur une machine propre."),
            ("Livrable PDF", "Rapport généré automatiquement avec FPDF2 et branding EFREI."),
        ],
        widths=(40, 120),
    )

    pdf.add_page()
    section_title(pdf, "10. Correspondance avec le bloc RNCP40875")
    score_table(pdf)

    section_title(pdf, "11. Conclusion")
    paragraph(
        pdf,
        "La solution réunit la logique attendue pour une évaluation complète : architecture de stockage, traitement distribué, streaming, API documentée, "
        "rapport détaillé et présentation visuelle sérieuse. Le socle peut servir de base de soutenance, de démonstration ou de reprise en environnement de production.",
    )

    pdf.output(str(path))


if __name__ == "__main__":
    build_pdf(OUTPUT)
