"""
config.py – Paramètres globaux du projet.
"""

from pathlib import Path

# Racine du projet
ROOT_DIR = Path(__file__).parent

# Données
DATA_RAW_DIR     = ROOT_DIR / "data" / "raw"
DATA_CLEANED_DIR = ROOT_DIR / "data" / "cleaned"

RAW_REVENUS   = DATA_RAW_DIR / "ircom-communes-revenus-2002.xlsx"
RAW_COMMUNES  = DATA_RAW_DIR / "communes-france-2025.csv"

CLEAN_REVENUS  = DATA_CLEANED_DIR / "revenus_communes.csv"

#Dashboard 
APP_TITLE = "Inégalités de revenus par commune en France (2002)"
APP_HOST  = "127.0.0.1"
APP_PORT  = 8050
APP_DEBUG = False
