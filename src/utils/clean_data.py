"""
clean_data.py
Nettoyage et fusion des données brutes IRCOM + référentiel communes.

Pipeline :
1. Lecture IRCOM (skip 5 lignes d'en-tête DGFiP)
2. Filtrage sur tranche "Total" → une ligne par commune
3. Reconstruction du code INSEE 5 caractères
4. Calcul de métriques dérivées (RFR moyen, taux imposition)
5. Fusion avec le référentiel communes (coordonnées GPS, région, population)
6. Export CSV dans data/cleaned/
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import config


# Correspondance position colonne → nom métier dans l'XLSX IRCOM
_COLS = {
    0:  "dep_raw",
    1:  "commune_raw",
    2:  "libelle",
    3:  "tranche",
    4:  "nb_foyers",
    5:  "rfr_total_k",      
    6:  "impot_net_k",
    7:  "nb_foyers_imposes",
    8:  "rfr_imposes_k",
    9:  "nb_salaires",
    10: "montant_salaires_k",
    11: "nb_retraites",
    12: "montant_retraites_k",
}


def _load_revenus(path: Path) -> pd.DataFrame:
    """
    Charge le fichier IRCOM, filtre les lignes « Total » et calcule les métriques.

    Parameters
    path : Path
        Chemin vers ircom-communes-revenus-2002.xlsx
    Returns
    pd.DataFrame
        Une ligne par commune avec code_insee, rfr_moyen, taux_imposition…
    """
    # Sauter les 5 premières lignes de méta-données DGFiP
    df = pd.read_excel(path, header=None, skiprows=5)
    df = df.rename(columns=_COLS)

    # Ne garder que la ligne agrégée "Total" (une par commune)
    df = df[df["tranche"].astype(str).str.strip() == "Total"].copy()

    #  Reconstruction du code INSEE 
    # Dans l'XLSX, le département est encodé "010 " (3 chiffres + espace)
    # Le code INSEE officiel utilise 2 chiffres : "01"
    df["dep"]      = df["dep_raw"].astype(str).str.strip().str[:2]
    df["commune"]  = df["commune_raw"].apply(
        lambda x: str(int(float(x))).zfill(3) if pd.notna(x) else None
    )
    df["code_insee"] = df["dep"] + df["commune"]

    #  Conversion numérique (valeurs "n.c." → NaN) 
    num_cols = ["nb_foyers", "rfr_total_k", "impot_net_k", "nb_foyers_imposes"]
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    #  Métriques dérivées 
    # Revenu fiscal de référence moyen par foyer, en euros
    df["rfr_moyen"] = (df["rfr_total_k"] * 1000) / df["nb_foyers"]

    # Taux d'imposition effectif (%)
    df["taux_imposition"] = np.where(
        df["rfr_total_k"] > 0,
        (df["impot_net_k"] / df["rfr_total_k"]) * 100,
        np.nan,
    )
    # Clamp : certaines petites communes ont des valeurs aberrantes (< 0 ou > 60 %)
    df["taux_imposition"] = df["taux_imposition"].clip(lower=0, upper=60)

    cols_out = [
        "code_insee", "dep", "libelle",
        "nb_foyers", "rfr_total_k", "rfr_moyen",
        "impot_net_k", "taux_imposition",
    ]
    return df[cols_out].dropna(subset=["code_insee", "rfr_moyen"])


def _load_communes(path: Path) -> pd.DataFrame:
    """
    Charge le référentiel géographique des communes (coordonnées, région, population).
    Parameters
    path : Path
        Chemin vers communes-france-2025.csv
    Returns
    pd.DataFrame
        Sous-ensemble utile avec code_insee comme clé de jointure.
    """
    df = pd.read_csv(
        path,
        dtype={"code_insee": str},
        low_memory=False,
    )

    # Ne garder que les communes (typecom == "COM")
    if "typecom" in df.columns:
        df = df[df["typecom"] == "COM"].copy()

    cols = [
        "code_insee", "nom_standard", "dep_nom", "reg_nom",
        "population", "latitude_centre", "longitude_centre",
        "densite", "superficie_km2",
    ]
    cols = [c for c in cols if c in df.columns]
    return df[cols].drop_duplicates(subset=["code_insee"])


def merge_and_save() -> pd.DataFrame:
    """
    Fusionne les données IRCOM avec le référentiel communes, puis sauvegarde.

    Returns
    pd.DataFrame
        DataFrame final prêt pour le dashboard (34 000+ communes).
    """
    print("  Chargement IRCOM…")
    df_rev = _load_revenus(config.RAW_REVENUS)
    print(f"    {len(df_rev)} communes dans IRCOM")

    print("  Chargement référentiel communes…")
    df_com = _load_communes(config.RAW_COMMUNES)
    print(f"    {len(df_com)} communes dans le référentiel")

    print("  Fusion sur code_insee…")
    df = df_rev.merge(df_com, on="code_insee", how="left")
    n_geo = df["latitude_centre"].notna().sum()
    print(f"    {n_geo} / {len(df)} communes géolocalisées")

    # Supprimer les communes sans coordonnées GPS (non cartographiables)
    df = df.dropna(subset=["latitude_centre", "longitude_centre", "rfr_moyen"])

    config.DATA_CLEANED_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(config.CLEAN_DATA, index=False)
    print(f"    Exporté → {config.CLEAN_DATA.name} ({len(df)} lignes)")
    return df


if __name__ == "__main__":
    result = merge_and_save()
    print("\nAperçu :")
    print(result[["code_insee", "libelle", "rfr_moyen", "reg_nom"]].head(5))
    print("\nStatistiques rfr_moyen :")
    print(result["rfr_moyen"].describe())
