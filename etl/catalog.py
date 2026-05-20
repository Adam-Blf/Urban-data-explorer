from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Literal

import requests

Provider = Literal["paris", "data_gouv"]


@dataclass(frozen=True)
class SourceSpec:
    """Describe one source exposed by the project catalog."""

    source_id: str
    title: str
    provider: Provider
    slug: str
    catalog_url: str
    family: str
    arrondissement_candidates: tuple[str, ...] = ()
    postal_candidates: tuple[str, ...] = ()
    status_candidates: tuple[str, ...] = ()
    category_candidates: tuple[str, ...] = ()
    latitude_candidates: tuple[str, ...] = ()
    longitude_candidates: tuple[str, ...] = ()
    metadata_only: bool = False

    @property
    def download_url(self) -> str | None:
        if self.metadata_only:
            return None
        if self.provider == "paris":
            return (
                "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/"
                f"{self.slug}/exports/csv?use_labels=true&lang=fr"
            )
        return resolve_data_gouv_download_url(self.slug)


def paris_url(slug: str) -> str:
    return f"https://opendata.paris.fr/explore/dataset/{slug}/"


@lru_cache(maxsize=32)
def resolve_data_gouv_download_url(slug: str) -> str | None:
    """Resolve a downloadable resource URL for a data.gouv dataset."""

    response = requests.get(
        "https://www.data.gouv.fr/api/1/datasets/",
        params={"q": slug},
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    for dataset in payload.get("data", []):
        dataset_slug = str(dataset.get("slug", ""))
        title = str(dataset.get("title", ""))
        if slug not in dataset_slug and slug.replace("-", " ") not in title.lower():
            continue
        for resource in dataset.get("resources", []):
            url = resource.get("url")
            fmt = str(resource.get("format", "")).lower()
            if url and fmt in {"csv", "json", "geojson", "tsv"}:
                return url
    return None


ALL_SOURCES: tuple[SourceSpec, ...] = (
    # Paris Open Data sources used for the main operational catalog.
    SourceSpec(
        source_id="espaces_verts",
        title="Espaces verts",
        provider="paris",
        slug="espaces_verts",
        catalog_url="https://opendata.paris.fr/explore/dataset/espaces_verts/export/?disjunctive.type_ev&disjunctive.categorie&disjunctive.adresse_codepostal&disjunctive.presence_cloture",
        family="green_space",
        arrondissement_candidates=("adresse_codepostal", "code_postal", "arrondissement"),
        postal_candidates=("adresse_codepostal", "code_postal", "postal_code"),
        category_candidates=("categorie", "type_ev"),
        status_candidates=("presence_cloture",),
    ),
    SourceSpec(
        source_id="stationnement_voie_publique_emprises",
        title="Stationnement sur voie publique - emprises",
        provider="paris",
        slug="stationnement-sur-voie-publique-emprises",
        catalog_url="https://opendata.paris.fr/explore/dataset/stationnement-sur-voie-publique-emprises/information/?disjunctive.regpri&disjunctive.regpar&disjunctive.typsta&disjunctive.arrond&disjunctive.locsta&disjunctive.zoneres&disjunctive.parite&disjunctive.signhor&disjunctive.signvert&disjunctive.confsign&disjunctive.typemob",
        family="mobility",
        arrondissement_candidates=("arrond", "arrondissement", "code_postal"),
        category_candidates=("typsta", "locsta", "typemob"),
        status_candidates=("regpri", "regpar", "zoneres"),
    ),
    SourceSpec(
        source_id="stationnement_voie_publique_emplacements",
        title="Stationnement - voie publique emplacements",
        provider="paris",
        slug="stationnement-voie-publique-emplacements",
        catalog_url="https://opendata.paris.fr/explore/dataset/stationnement-voie-publique-emplacements/information/?disjunctive.typsta&disjunctive.regpar&disjunctive.regpri&disjunctive.arrond&disjunctive.locsta&disjunctive.zoneres&disjunctive.stv&disjunctive.prefet&disjunctive.zoneasp&disjunctive.parite&disjunctive.signhor&disjunctive.signvert&disjunctive.typemob&disjunctive.confsign",
        family="mobility",
        arrondissement_candidates=("arrond", "arrondissement", "code_postal"),
        category_candidates=("typsta", "typemob", "locsta"),
        status_candidates=("regpar", "regpri", "zoneres", "stv"),
    ),
    SourceSpec(
        source_id="belib",
        title="Belib - points de recharge",
        provider="paris",
        slug="belib-points-de-recharge-pour-vehicules-electriques-disponibilite-temps-reel",
        catalog_url="https://opendata.paris.fr/explore/dataset/belib-points-de-recharge-pour-vehicules-electriques-disponibilite-temps-reel/export/?disjunctive.statut_pdc&disjunctive.arrondissement",
        family="mobility",
        arrondissement_candidates=("arrondissement", "code_postal"),
        status_candidates=("statut_pdc",),
        category_candidates=("type_pdc", "borne", "puissance"),
    ),
    SourceSpec(
        source_id="velib_stations",
        title="Velib - emplacement des stations",
        provider="paris",
        slug="velib-emplacement-des-stations",
        catalog_url="https://opendata.paris.fr/explore/dataset/velib-emplacement-des-stations/export/",
        family="mobility",
        arrondissement_candidates=("nom_arrondissement_communes", "arrondissement", "code_postal"),
        category_candidates=("capacity", "station_code", "name"),
    ),
    SourceSpec(
        source_id="sanisettesparis",
        title="Sanisettes Paris",
        provider="paris",
        slug="sanisettesparis",
        catalog_url="https://opendata.paris.fr/explore/dataset/sanisettesparis/export/?disjunctive.type&disjunctive.arrondissement&disjunctive.horaire&disjunctive.acces_pmr&disjunctive.relais_bebe&disjunctive.statut",
        family="public_service",
        arrondissement_candidates=("arrondissement", "code_postal"),
        status_candidates=("statut", "acces_pmr", "relais_bebe"),
        category_candidates=("type", "horaire"),
    ),
    SourceSpec(
        source_id="amenagements_cyclables",
        title="Aménagements cyclables",
        provider="paris",
        slug="amenagements-cyclables",
        catalog_url="https://opendata.paris.fr/explore/dataset/amenagements-cyclables/information/?disjunctive.amenagement&disjunctive.arrondissement&disjunctive.position_amenagement&disjunctive.vitesse_maximale_autorisee&disjunctive.source",
        family="mobility",
        arrondissement_candidates=("arrondissement", "code_postal"),
        category_candidates=("amenagement", "position_amenagement", "source"),
    ),
    SourceSpec(
        source_id="velib_disponibilite",
        title="Velib - disponibilité temps réel",
        provider="paris",
        slug="velib-disponibilite-en-temps-reel",
        catalog_url="https://opendata.paris.fr/explore/dataset/velib-disponibilite-en-temps-reel/information/?disjunctive.is_renting&disjunctive.is_installed&disjunctive.is_returning&disjunctive.name&disjunctive.nom_arrondissement_communes",
        family="mobility",
        arrondissement_candidates=("nom_arrondissement_communes", "arrondissement", "code_postal"),
        status_candidates=("is_renting", "is_installed", "is_returning"),
        category_candidates=("name",),
    ),
    SourceSpec(
        source_id="chantiers_perturbants",
        title="Chantiers perturbants",
        provider="paris",
        slug="chantiers-perturbants",
        catalog_url="https://opendata.paris.fr/explore/dataset/chantiers-perturbants/information/?disjunctive.cp_arrondissement&disjunctive.maitre_ouvrage&disjunctive.objet&disjunctive.impact_circulation&disjunctive.niveau_perturbation&disjunctive.statut",
        family="pressure",
        arrondissement_candidates=("cp_arrondissement", "arrondissement", "code_postal"),
        status_candidates=("statut", "impact_circulation", "niveau_perturbation"),
        category_candidates=("objet", "maitre_ouvrage"),
    ),
    SourceSpec(
        source_id="ecoles_elementaires",
        title="Ecoles elementaires",
        provider="paris",
        slug="etablissements-scolaires-ecoles-elementaires",
        catalog_url="https://opendata.paris.fr/explore/dataset/etablissements-scolaires-ecoles-elementaires/information/?disjunctive.arr_libelle&disjunctive.annee_scol&disjunctive.id_projet&disjunctive.arr_insee&disjunctive.type_etabl",
        family="education",
        arrondissement_candidates=("arr_insee", "arr_libelle", "code_postal"),
        category_candidates=("type_etabl", "id_projet"),
    ),
    SourceSpec(
        source_id="colleges",
        title="Colleges",
        provider="paris",
        slug="etablissements-scolaires-colleges",
        catalog_url="https://opendata.paris.fr/explore/dataset/etablissements-scolaires-colleges/information/?disjunctive.arr_libelle&disjunctive.annee_scol&disjunctive.id_projet&disjunctive.arr_insee",
        family="education",
        arrondissement_candidates=("arr_insee", "arr_libelle", "code_postal"),
        category_candidates=("id_projet",),
    ),
    SourceSpec(
        source_id="marches_decouverts",
        title="Marches decouverts",
        provider="paris",
        slug="marches-decouverts",
        catalog_url="https://opendata.paris.fr/explore/dataset/marches-decouverts/information/?disjunctive.produit&disjunctive.ardt&disjunctive.jours_tenue&disjunctive.gestionnaire",
        family="public_service",
        arrondissement_candidates=("ardt", "arrondissement", "code_postal"),
        category_candidates=("produit", "jours_tenue", "gestionnaire"),
    ),
    SourceSpec(
        source_id="que_faire_a_paris",
        title="Que faire a Paris",
        provider="paris",
        slug="que-faire-a-paris-",
        catalog_url="https://opendata.paris.fr/explore/dataset/que-faire-a-paris-/information/?disjunctive.access_type&disjunctive.price_type&disjunctive.deaf&disjunctive.blind&disjunctive.pmr&disjunctive.address_city&disjunctive.address_zipcode&disjunctive.address_name&disjunctive.programs",
        family="culture",
        arrondissement_candidates=("address_zipcode", "arrondissement", "code_postal"),
        category_candidates=("programs", "access_type", "price_type"),
    ),
    SourceSpec(
        source_id="logements_sociaux",
        title="Logements sociaux finances a Paris",
        provider="paris",
        slug="logements-sociaux-finances-a-paris",
        catalog_url="https://opendata.paris.fr/explore/dataset/logements-sociaux-finances-a-paris/information/?disjunctive.bs&disjunctive.mode_real&disjunctive.nature_programme&disjunctive.ville&disjunctive.code_postal",
        family="housing",
        arrondissement_candidates=("code_postal", "ville", "arrondissement"),
        category_candidates=("nature_programme", "mode_real", "bs"),
    ),
    SourceSpec(
        source_id="immeubles_proteges",
        title="Immeubles proteges",
        provider="data_gouv",
        slug="immeubles-proteges-au-titre-des-monuments-historiques-2",
        catalog_url="https://www.data.gouv.fr/datasets/immeubles-proteges-au-titre-des-monuments-historiques-2",
        family="culture",
        arrondissement_candidates=("code_postal", "commune", "arrondissement"),
        category_candidates=("nature", "statut", "designation"),
        metadata_only=True,
    ),
    SourceSpec(
        source_id="musees_france",
        title="Musees de France",
        provider="data_gouv",
        slug="liste-des-musees-de-france",
        catalog_url="https://www.data.gouv.fr/datasets/liste-des-musees-de-france",
        family="culture",
        arrondissement_candidates=("code_postal", "commune", "arrondissement"),
        category_candidates=("type", "theme"),
        metadata_only=True,
    ),
    SourceSpec(
        source_id="hopitaux_idf",
        title="Etablissements hospitaliers franciliens",
        provider="data_gouv",
        slug="les-etablissements-hospitaliers-franciliens-idf",
        catalog_url="https://www.data.gouv.fr/datasets/les-etablissements-hospitaliers-franciliens-idf",
        family="health",
        arrondissement_candidates=("code_postal", "commune", "arrondissement"),
        category_candidates=("type_etablissement", "statut"),
        metadata_only=True,
    ),
    SourceSpec(
        source_id="medecins_has",
        title="Medecins accredites par la HAS",
        provider="data_gouv",
        slug="medecins-accredites-par-la-has",
        catalog_url="https://www.data.gouv.fr/datasets/medecins-accredites-par-la-has",
        family="health",
        arrondissement_candidates=("code_postal", "commune", "arrondissement"),
        category_candidates=("specialite", "type"),
        metadata_only=True,
    ),
)
