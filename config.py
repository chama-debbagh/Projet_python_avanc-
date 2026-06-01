"""
config.py
Fichier de configuration centralisé du projet.
Contient les URLs des données, les chemins de fichiers et les constantes globales.
"""
 
import os
 
# Répertoires
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
DATA_CLEAN_DIR = os.path.join(BASE_DIR, "data", "cleaned")
 
# URLs des sources de données 
# Dataset 1 : Comptes des communes (OFGL)- budgets principaux 2017-2024
# Source : data.gouv.fr / OFGL
BUDGET_URL = (
    "https://data.ofgl.fr/api/explore/v2.1/catalog/datasets/"
    "ofgl-base-communes-consolidee/exports/csv"
    "?lang=fr&timezone=Europe%2FParis&use_labels=true&delimiter=%3B"
)
 
# Dataset 2 : Communes de France - coordonnées géographiques (lat/lon + code INSEE)
# Source : data.gouv.fr
COMMUNES_URL = (
    "https://www.data.gouv.fr/fr/datasets/r/dbe8a621-a9c4-4bc3-9cae-be1699c5ff25"
)
 
# Chemins fichiers locaux 
BUDGET_RAW = os.path.join(DATA_RAW_DIR, "budget_communes_raw.csv")
COMMUNES_RAW = os.path.join(DATA_RAW_DIR, "communes_raw.csv")
MERGED_CLEAN = os.path.join(DATA_CLEAN_DIR, "budget_communes_clean.csv")
 
# Paramètres du dashboard
APP_TITLE = "Finances des communes françaises"
APP_PORT = 8050
DEBUG = False
 
# Année par défaut affichée au démarrage
DEFAULT_YEAR = 2022
 
# Colonnes budgétaires disponibles pour les graphiques
BUDGET_COLUMNS = {
    "Dépenses de fonctionnement (en €)": "depenses_fonctionnement",
    "Recettes de fonctionnement (en €)": "recettes_fonctionnement",
    "Dépenses d'investissement (en €)": "depenses_investissement",
    "Recettes d'investissement (en €)": "recettes_investissement",
    "Dette au 31/12 (en €)": "encours_dette",
    "Épargne brute (en €)": "epargne_brute",
}
 