"""
config.py
configuration
Paramètres globaux : chemins de fichiers, constantes du dashboard.
Modifier uniquement ce fichier pour adapter les chemins à une autre machine.
"""

from pathlib import Path
# Répertoires
ROOT_DIR         = Path(__file__).parent
DATA_RAW_DIR     = ROOT_DIR / "data" / "raw"
DATA_CLEANED_DIR = ROOT_DIR / "data" / "cleaned"

#Fichiers bruts
RAW_REVENUS  = DATA_RAW_DIR / "ircom-communes-revenus-2002.xlsx"
RAW_COMMUNES = DATA_RAW_DIR / "communes-france-2025.csv"

#Fichier nettoyé
CLEAN_DATA = DATA_CLEANED_DIR / "revenus_communes.csv"

#Dashboard
APP_TITLE = "Inégalités de revenus par commune en France (2002)"
APP_HOST  = "127.0.0.1"
APP_PORT  = 8050
DEBUG     = False
