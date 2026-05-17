
import sys
from pathlib import Path
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import config
from src.utils.get_data import check_raw_files
from src.utils.clean_data import merge_and_save
from src.components.header import create_header
from src.components.footer import create_footer
from src.components.navbar import create_navbar
from src.pages import home, histogramme, carte, about


# Vérification et préparation des données
def prepare_data() -> None:
    """
    Vérifie la présence des fichiers bruts et génère les données nettoyées
    si elles n'existent pas encore.
    """
    print("Préparation des données")
    if not check_raw_files():
        print("Fichiers bruts manquants, arrêt.")
        sys.exit(1)

    if not config.CLEAN_REVENUS.exists():
        print("Fichier nettoyé absent → lancement du nettoyage…")
        merge_and_save()
    else:
        print(f"Fichier nettoyé trouvé : {config.CLEAN_REVENUS.name}")


# Application Dash
app = dash.Dash(
    __name__,
    # Gestion multi-page : les pages sont chargées via dcc.Location
    suppress_callback_exceptions=True,
    title=config.APP_TITLE,
)

app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    create_header(),
    create_navbar(),
    html.Main(id="page-content", style={"minHeight": "80vh"}),
    create_footer(),
])


#Routage entre les pages 
@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def display_page(pathname: str):
    """
    Sélectionne le layout à afficher selon l'URL.

    Parameters
    pathname : str
        Chemin de l'URL courante.

    Returns
    dash.development.base_component.Component
        Le layout de la page correspondante.
    """
    routes = {
        "/":            home.layout,
        "/histogramme": histogramme.layout,
        "/carte":       carte.layout,
        "/about":       about.layout,
    }
    page_fn = routes.get(pathname, home.layout)
    return page_fn()


#Lancement
if __name__ == "__main__":
    prepare_data()
    print(f"\n=== Dashboard disponible sur http://{config.APP_HOST}:{config.APP_PORT} ===\n")
    app.run(
        host=config.APP_HOST,
        port=config.APP_PORT,
        debug=config.APP_DEBUG,
    )
