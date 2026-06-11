"""
main.py
Point d'entrée du dashboard.

Étapes au démarrage :
1. Vérification des fichiers bruts dans data/raw/
2. Génération de data/cleaned/revenus_communes.csv si absent
3. Lancement du serveur Dash

Usage :
    python main.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import dash
from dash import html, dcc
from dash.dependencies import Input, Output

import config
from src.utils.get_data import check_raw_files
from src.utils.clean_data import merge_and_save
from src.components.header import create_header
from src.components.footer import create_footer
from src.components.navbar import create_navbar

# Import des pages (enregistre aussi leurs callbacks dans le registre global Dash)
from src.pages import home, histogramme, analyses, carte, about

# 1. Pipeline de données 

def prepare_data() -> None:
    """
    Prépare les données nettoyées si elles ne sont pas encore générées.
    Arrête l'exécution si les fichiers bruts sont manquants.
    """
    print("\n Vérification des données ")
    if not check_raw_files():
        print("\nFichiers bruts manquants dans data/raw/. Arrêt.")
        sys.exit(1)

    if not config.CLEAN_DATA.exists():
        print("\n Génération des données nettoyées…")
        merge_and_save()
    else:
        print(f"  [OK] Données nettoyées trouvées : {config.CLEAN_DATA.name}")


#2. Application Dash

app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True, 
    title=config.APP_TITLE,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        create_header(),
        create_navbar(),
        html.Main(id="page-content", style={"minHeight": "78vh"}),
        create_footer(),
    ],
    style={"fontFamily": "Arial, Helvetica, sans-serif", "margin": "0"},
)


#3. Routage

_ROUTES = {
    "/":            home.layout,
    "/histogramme": histogramme.layout,
    "/analyses":    analyses.layout,
    "/carte":       carte.layout,
    "/about":       about.layout,
}


@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def display_page(pathname: str):
    """
    Sélectionne le layout à afficher selon l'URL courante.
    Parameters
    pathname : str
        Chemin de l'URL (ex : « /histogramme »).
    Returns
    dash component
        Le layout de la page correspondante, ou la page d'accueil par défaut.
    """
    page_fn = _ROUTES.get(pathname, home.layout)
    return page_fn()


#Démarrage

if __name__ == "__main__":
    prepare_data()
    url = f"http://{config.APP_HOST}:{config.APP_PORT}"
    print(f"\nDashboard disponible sur {url}\n")
    app.run(
        host=config.APP_HOST,
        port=config.APP_PORT,
        debug=config.DEBUG,
    )
