"""
clean_data.py : Nettoyage et fusion des données brutes.

Étapes :
1. Lecture du fichier IRCOM (revenus 2002) en sautant les lignes d'en-tête.
2. Filtrage sur les lignes "Total" (une ligne par commune).
3. Lecture du référentiel communes (coordonnées GPS, population…).
4. Fusion sur le code INSEE reconstruit (dep + commune).
5. Export dans data/cleaned/revenus_communes.csv.
"""

import sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
import config


# Colonnes retenues après nettoyage
COLS_RENAME = {
    0:  "dep",
    1:  "commune",
    2:  "libelle",
    3:  "tranche",
    4:  "nb_foyers",
    5:  "rfr_total",       # Revenu Fiscal de Référence total (k€)
    6:  "impot_net",       # Impôt net (k€)
    7:  "nb_foyers_imposes",
    8:  "rfr_imposes",
    9:  "nb_salaires",
    10: "montant_salaires",
    11: "nb_retraites",
    12: "montant_retraites",
}


def load_revenus(path: Path) -> pd.DataFrame:
    """
    Charge et nettoie le fichier IRCOM revenus 2002.

    Parameters

    path : Path
        Chemin vers le fichier .xlsx brut.

    Returns

    pd.DataFrame
        DataFrame avec une ligne par commune (tranche « Total »).
    """
    # Les 3 premières lignes sont du méta-données, la ligne 3 (index 3) est
    # l'en-tête réel → on saute les 5 premières lignes et on nomme manuellement
    df = pd.read_excel(path, header=None, skiprows=5)
    df = df.rename(columns=COLS_RENAME)

    # On ne garde que les lignes agrégées "Total" par commune
    df = df[df["tranche"].astype(str).str.strip() == "Total"].copy()

    # Nettoyage des codes département et commune (espaces, zéros)
    # Dans IRCOM, le dep est encodé sur 3 chiffres + espace (ex: "010 ")
    # Le code INSEE officiel utilise 2 chiffres pour le dep (ex: "01")
    df["dep_raw"]  = df["dep"].astype(str).str.strip()
    # On prend les 2 premiers chiffres significatifs (ignore le zéro de droite)
    df["dep"]      = df["dep_raw"].str[:2]
    df["commune"]  = df["commune"].astype(str).str.strip().str.zfill(3)

    # Construction du code INSEE standard (5 caractères : 2 dep + 3 commune)
    df["code_insee"] = df["dep"] + df["commune"]

    # Conversion numérique (certaines valeurs sont "n.c." → NaN)
    numeric_cols = ["nb_foyers", "rfr_total", "impot_net",
                    "nb_foyers_imposes", "rfr_imposes"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Calcul du revenu fiscal de référence moyen par foyer (€)
    df["rfr_moyen"] = (df["rfr_total"] * 1000) / df["nb_foyers"]

    # Taux d'imposition moyen (%)
    df["taux_imposition"] = (df["impot_net"] / df["rfr_total"]) * 100

    return df[["code_insee", "dep", "libelle", "nb_foyers",
               "rfr_total", "rfr_moyen", "impot_net", "taux_imposition"]]


def load_communes(path: Path) -> pd.DataFrame:
    """
    Charge le référentiel des communes (coordonnées, population, région…).

    Parameters

    path : Path
        Chemin vers le fichier communes-france-2025.csv.

    Returns

    pd.DataFrame
        DataFrame avec code_insee, coordonnées et métadonnées utiles.
    """
    df = pd.read_csv(path, dtype={"code_insee": str}, low_memory=False)

    # On ne garde que les communes (typecom == "COM")
    if "typecom" in df.columns:
        df = df[df["typecom"] == "COM"]

    cols_utiles = [
        "code_insee", "nom_standard", "dep_nom", "reg_nom",
        "population", "latitude_centre", "longitude_centre",
        "densite", "superficie_km2",
    ]
    cols_utiles = [c for c in cols_utiles if c in df.columns]
    return df[cols_utiles].copy()


def merge_and_save() -> pd.DataFrame:
    """
    Fusionne les deux sources et exporte le fichier nettoyé.

    Returns
    pd.DataFrame
        DataFrame fusionné prêt pour le dashboard.
    """
    print("  Chargement des revenus IRCOM…")
    df_rev = load_revenus(config.RAW_REVENUS)
    print(f"    → {len(df_rev)} communes dans IRCOM")

    print("  Chargement du référentiel communes…")
    df_com = load_communes(config.RAW_COMMUNES)
    print(f"    → {len(df_com)} communes dans le référentiel")

    print("  Fusion sur code_insee…")
    df = df_rev.merge(df_com, on="code_insee", how="left")
    matched = df["latitude_centre"].notna().sum()
    print(f"    → {matched} communes géolocalisées sur {len(df)}")

    # Suppression des lignes sans coordonnées (non géolocalisables)
    df = df.dropna(subset=["latitude_centre", "longitude_centre", "rfr_moyen"])

    config.DATA_CLEANED_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(config.CLEAN_REVENUS, index=False)
    print(f"  Fichier nettoyé exporté → {config.CLEAN_REVENUS}")
    return df


if __name__ == "__main__":
    print(" Nettoyage des données")
    df = merge_and_save()
    print(f"\nAperçu :\n{df.head(3)}")
    print(f"\nStatistiques rfr_moyen :\n{df['rfr_moyen'].describe()}")
