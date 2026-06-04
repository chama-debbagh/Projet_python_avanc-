"""
about.py
Page « À propos » : description du projet, sources de données, technologies.
"""

from dash import html


def layout() -> html.Div:
    """Retourne le layout de la page À propos."""
    section = {"marginTop": "24px"}
    return html.Div([
        html.H2("À propos de ce projet"),

        html.Div([
            html.H3("Contexte"),
            html.P(
                "Ce dashboard a été réalisé dans le cadre du mini-projet Data à l'ESIEE Paris. "
                "Il explore les inégalités de revenus fiscaux des communes françaises en 2002 "
                "à partir des données publiques en libre accès sur data.gouv.fr."
            ),
        ], style=section),

        html.Div([
            html.H3("Sources de données"),
            html.Ul([
                html.Li([
                    html.Strong("IRCOM 2002 (DGFiP) : "),
                    "Revenus fiscaux de référence par commune. ",
                    html.A("data.gouv.fr",
                           href="https://www.data.gouv.fr/fr/datasets/impot-sur-le-revenu-par-commune/",
                           target="_blank"),
                ]),
                html.Li([
                    html.Strong("Référentiel communes 2025 : "),
                    "Coordonnées GPS, population, région. ",
                    html.A("data.gouv.fr",
                           href="https://www.data.gouv.fr/fr/datasets/communes-de-france-base-des-codes-postaux/",
                           target="_blank"),
                ]),
            ]),
        ], style=section),

        html.Div([
            html.H3("Technologies utilisées"),
            html.Ul([
                html.Li("Python 3.12"),
                html.Li("Dash 4 – framework de dashboard web"),
                html.Li("Plotly 6 – visualisations interactives"),
                html.Li("Pandas – manipulation des données"),
                html.Li("OpenPyXL – lecture du fichier Excel IRCOM"),
            ]),
        ], style=section),

        html.Div([
            html.H3("Lancer le dashboard"),
            html.Pre(
                "git clone <adresse_du_depot>\n"
                "cd data_project\n"
                "python -m venv .venv\n"
                "source .venv/bin/activate\n"
                "pip install -r requirements.txt\n"
                "python main.py",
                style={
                    "background": "#f4f4f4", "padding": "14px",
                    "borderRadius": "6px", "fontSize": "0.88rem",
                    "border": "1px solid #ddd",
                },
            ),
        ], style=section),

    ], style={"padding": "24px 32px", "maxWidth": "800px"})
