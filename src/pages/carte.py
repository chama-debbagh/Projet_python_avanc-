"""
carte.py
Page avec la carte géolocalisée des communes françaises (scatter map).
Fonctionnalités :
- Filtre par région
- Choix de la variable à colorier (RFR moyen, taux imposition, population)
- Survol : nom de la commune, département, valeurs clés
"""

import numpy as np
from dash import html, dcc, callback, Input, Output
import plotly.express as px

from src.utils.common_functions import load_clean_data, get_region_options, filter_by_region


# Définition des variables disponibles sur la carte
_VARIABLES = {
    "rfr_moyen":       {"label": "RFR moyen (€)",         "scale": "RdYlGn"},
    "taux_imposition": {"label": "Taux d'imposition (%)",  "scale": "RdYlBu_r"},
    "population":      {"label": "Population",             "scale": "Blues"},
}


def layout() -> html.Div:
    """Retourne le layout de la page carte."""
    df      = load_clean_data()
    options = get_region_options(df)

    return html.Div([
        html.H2("Carte des revenus fiscaux par commune (2002)"),
        html.P(
            "Chaque point représente une commune. La couleur encode la variable "
            "sélectionnée, la taille est proportionnelle au nombre de foyers fiscaux.",
            style={"color": "#666", "marginBottom": "20px"},
        ),

        #  Filtres 
        html.Div([
            html.Div([
                html.Label("Région", style={"fontWeight": "600", "display": "block", "marginBottom": "4px"}),
                dcc.Dropdown(
                    id="carte-region",
                    options=options,
                    value="Toutes",
                    clearable=False,
                    style={"minWidth": "260px"},
                ),
            ]),
            html.Div([
                html.Label("Variable", style={"fontWeight": "600", "display": "block", "marginBottom": "4px"}),
                dcc.RadioItems(
                    id="carte-variable",
                    options=[{"label": v["label"], "value": k} for k, v in _VARIABLES.items()],
                    value="rfr_moyen",
                    inputStyle={"marginRight": "4px"},
                    labelStyle={"marginRight": "18px"},
                ),
            ]),
        ], style={"display": "flex", "gap": "32px", "flexWrap": "wrap",
                  "alignItems": "flex-start", "marginBottom": "20px",
                  "background": "#f7f9fc", "padding": "16px 20px",
                  "borderRadius": "8px", "border": "1px solid #dde3ed"}),

        dcc.Graph(id="carte-graph", style={"height": "620px"}),

        html.Div(id="carte-info", style={
            "marginTop": "10px", "fontSize": "0.85rem",
            "color": "#666", "fontStyle": "italic",
        }),
    ], style={"padding": "24px 32px"})


#  Callback 

@callback(
    Output("carte-graph", "figure"),
    Output("carte-info",  "children"),
    Input("carte-region",   "value"),
    Input("carte-variable", "value"),
)
def update_carte(region: str, variable: str):
    """
    Reconstruit la carte selon la région et la variable sélectionnées.
    Parameters
    region   : str  Région ou « Toutes »
    variable : str  Clé dans _VARIABLES

    Returns
    tuple[go.Figure, str]
    """
    df     = filter_by_region(load_clean_data(), region)
    meta   = _VARIABLES[variable]
    titre  = f"{meta['label']} - {'France entière' if region == 'Toutes' else region}"

    #  Normalisation de la taille des points 
    # nombre de foyers varie de 11 à 240 000 donc on utilise la racine carrée pour atténuer
    df = df.copy()
    df["_size"] = np.sqrt(df["nb_foyers"].clip(lower=1))
    # Clamp pour éviter les points trop gros ou trop petits
    df["_size"] = df["_size"].clip(upper=df["_size"].quantile(0.98))

    # Gestion des NaN dans la variable colorée
    df = df.dropna(subset=[variable])

    fig = px.scatter_map(
        df,
        lat="latitude_centre",
        lon="longitude_centre",
        color=variable,
        size="_size",
        size_max=18,
        hover_name="nom_standard",
        hover_data={
            "rfr_moyen":       ":,.0f",
            "taux_imposition": ":.1f",
            "nb_foyers":       ":,",
            "dep_nom":         True,
            "reg_nom":         True,
            "_size":           False,
            "latitude_centre":  False,
            "longitude_centre": False,
        },
        color_continuous_scale=meta["scale"],
        zoom=4.8 if region == "Toutes" else 6.5,
        center={"lat": 46.5, "lon": 2.3} if region == "Toutes" else None,
        title=titre,
        labels={variable: meta["label"]},
        map_style="carto-positron",
    )
    fig.update_layout(
        margin={"r": 0, "t": 44, "l": 0, "b": 0},
        coloraxis_colorbar={"title": meta["label"], "thickness": 14},
    )

    info = (
        f"{len(df):,} communes affichées".replace(",", "\u202f") +
        f" — {meta['label']} médian : "
        f"{df[variable].median():,.1f}".replace(",", "\u202f") +
        (" €" if variable == "rfr_moyen" else
         " %" if variable == "taux_imposition" else "")
    )
    return fig, info
