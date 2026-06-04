"""
common_functions.py
Fonctions utilitaires partagées entre les composants et pages du dashboard.
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import config


def load_clean_data() -> pd.DataFrame:
    """
    Charge le fichier nettoyé data/cleaned/revenus_communes.csv.
    Déclenche le nettoyage automatiquement si le fichier est absent.

    Returns
    pd.DataFrame
        Données prêtes pour les visualisations (34 000+ communes).
    """
    if not config.CLEAN_DATA.exists():
        from src.utils.clean_data import merge_and_save
        merge_and_save()

    return pd.read_csv(
        config.CLEAN_DATA,
        dtype={"code_insee": str, "dep": str},
        low_memory=False,
    )


def get_region_options(df: pd.DataFrame) -> list[dict]:
    """
    Construit la liste d'options pour le Dropdown de sélection de région.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame chargé depuis load_clean_data().

    Returns
    list[dict]
        Liste [{"label": ..., "value": ...}] pour dcc.Dropdown.
    """
    regions = sorted(df["reg_nom"].dropna().unique())
    return [{"label": "France entière", "value": "Toutes"}] + [
        {"label": r, "value": r} for r in regions
    ]


def filter_by_region(df: pd.DataFrame, region: str) -> pd.DataFrame:
    """
    Filtre le DataFrame par région.

    Parameters
    df : pd.DataFrame
    region : str
        Nom de région ou « Toutes » pour ne pas filtrer.

    Returns=
    pd.DataFrame
    """
    if region and region != "Toutes":
        return df[df["reg_nom"] == region].copy()
    return df.copy()
