"""
home.py
Page d'accueil du dashboard.
Présente le contexte du projet et les chiffres clés.
"""

from dash import html, dcc
from src.utils.common_functions import load_clean_data


def layout() -> html.Div:
    """Retourne le layout de la page d'accueil avec des KPIs."""
    df = load_clean_data()

    n_communes   = f"{len(df):,}".replace(",", "\u202f")
    rfr_median   = f"{df['rfr_moyen'].median():,.0f} €".replace(",", "\u202f")
    rfr_max      = f"{df['rfr_moyen'].max():,.0f} €".replace(",", "\u202f")
    commune_max  = df.loc[df["rfr_moyen"].idxmax(), "nom_standard"]
    rfr_min      = f"{df['rfr_moyen'].min():,.0f} €".replace(",", "\u202f")

    kpi_style = {
        "background": "#f7f9fc",
        "border": "1px solid #dde3ed",
        "borderRadius": "8px",
        "padding": "20px 28px",
        "minWidth": "180px",
        "textAlign": "center",
    }

    return html.Div([
        html.H2("Bienvenue", style={"marginBottom": "6px"}),
        html.P(
            "Ce dashboard explore les inégalités de revenus fiscaux des communes "
            "françaises en 2002 à partir des données publiques DGFiP (IRCOM). "
            "Deux visualisations permettent d'analyser la distribution des revenus "
            "et leur répartition géographique sur le territoire.",
            style={"maxWidth": "750px", "lineHeight": "1.6", "color": "#555"},
        ),

        # KPIs 
        html.Div([
            html.Div([
                html.Div(n_communes, style={"fontSize": "2rem", "fontWeight": "700", "color": "#2980b9"}),
                html.Div("communes analysées", style={"fontSize": "0.85rem", "color": "#666"}),
            ], style=kpi_style),
            html.Div([
                html.Div(rfr_median, style={"fontSize": "2rem", "fontWeight": "700", "color": "#27ae60"}),
                html.Div("RFR médian / foyer", style={"fontSize": "0.85rem", "color": "#666"}),
            ], style=kpi_style),
            html.Div([
                html.Div(rfr_max, style={"fontSize": "2rem", "fontWeight": "700", "color": "#e67e22"}),
                html.Div(f"RFR max ({commune_max})", style={"fontSize": "0.85rem", "color": "#666"}),
            ], style=kpi_style),
            html.Div([
                html.Div(rfr_min, style={"fontSize": "2rem", "fontWeight": "700", "color": "#c0392b"}),
                html.Div("RFR min / foyer", style={"fontSize": "0.85rem", "color": "#666"}),
            ], style=kpi_style),
        ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap", "margin": "24px 0"}),

        # Liens vers les pages 
        html.Div([
            dcc.Link(
                "→ Voir l'histogramme", href="/histogramme",
                style={"display": "inline-block", "background": "#2980b9",
                       "color": "white", "padding": "10px 20px",
                       "borderRadius": "5px", "textDecoration": "none",
                       "marginRight": "12px"},
            ),
            dcc.Link(
                "→ Voir la carte", href="/carte",
                style={"display": "inline-block", "background": "#27ae60",
                       "color": "white", "padding": "10px 20px",
                       "borderRadius": "5px", "textDecoration": "none"},
            ),
        ]),
    ], style={"padding": "28px 32px"})
