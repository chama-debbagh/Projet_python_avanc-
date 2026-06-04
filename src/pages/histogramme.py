"""
histogramme.py
Page avec l'histogramme interactif de la distribution du RFR moyen par commune.

Fonctionnalités :
- Filtre par région via Dropdown
- Choix du nombre de classes via Slider
- Affichage de la médiane et de la moyenne en annotation
- Tableau de statistiques descriptives
"""

from dash import html, dcc, callback, Input, Output
import plotly.graph_objects as go
import pandas as pd

from src.utils.common_functions import load_clean_data, get_region_options, filter_by_region


#  Layout 

def layout() -> html.Div:
    """Retourne le layout complet de la page histogramme."""
    df      = load_clean_data()
    options = get_region_options(df)

    return html.Div([
        html.H2("Distribution du revenu fiscal de référence moyen par commune (2002)"),
        html.P(
            "Chaque barre représente le nombre de communes dont le RFR moyen par foyer "
            "fiscal se situe dans l'intervalle correspondant.",
            style={"color": "#666", "marginBottom": "20px"},
        ),

        #  Filtres 
        html.Div([
            html.Div([
                html.Label("Région", style={"fontWeight": "600", "display": "block", "marginBottom": "4px"}),
                dcc.Dropdown(
                    id="histo-region",
                    options=options,
                    value="Toutes",
                    clearable=False,
                    style={"minWidth": "260px"},
                ),
            ]),
            html.Div([
                html.Label(
                    id="histo-bins-label",
                    children="Nombre de classes : 50",
                    style={"fontWeight": "600", "display": "block", "marginBottom": "4px"},
                ),
                dcc.Slider(
                    id="histo-bins",
                    min=10, max=100, step=5, value=50,
                    marks={10: "10", 25: "25", 50: "50", 75: "75", 100: "100"},
                    tooltip={"placement": "bottom", "always_visible": False},
                ),
            ], style={"minWidth": "280px"}),
            html.Div([
                html.Label("Échelle X", style={"fontWeight": "600", "display": "block", "marginBottom": "4px"}),
                dcc.RadioItems(
                    id="histo-scale",
                    options=[
                        {"label": "Linéaire", "value": "linear"},
                        {"label": "Logarithmique", "value": "log"},
                    ],
                    value="linear",
                    inline=True,
                    inputStyle={"marginRight": "4px"},
                    labelStyle={"marginRight": "14px"},
                ),
            ]),
        ], style={"display": "flex", "gap": "32px", "flexWrap": "wrap",
                  "alignItems": "flex-start", "marginBottom": "20px",
                  "background": "#f7f9fc", "padding": "16px 20px",
                  "borderRadius": "8px", "border": "1px solid #dde3ed"}),

        #  Graphique 
        dcc.Graph(id="histo-graph", style={"height": "480px"}),

        #  Statistiques descriptives 
        html.Div(id="histo-stats", style={"marginTop": "16px"}),
    ], style={"padding": "24px 32px"})


#  Callbacks 

@callback(
    Output("histo-bins-label", "children"),
    Input("histo-bins", "value"),
)
def update_bins_label(n_bins: int) -> str:
    """Met à jour le label du slider de classes."""
    return f"Nombre de classes : {n_bins}"


@callback(
    Output("histo-graph", "figure"),
    Output("histo-stats", "children"),
    Input("histo-region", "value"),
    Input("histo-bins",   "value"),
    Input("histo-scale",  "value"),
)
def update_histogramme(region: str, n_bins: int, scale: str):
    """
    Reconstruit l'histogramme selon les filtres sélectionnés.

    Parameters
    ----------
    region : str  Région ou « Toutes »
    n_bins : int  Nombre de classes
    scale  : str  « linear » ou « log »

    Returns
    -------
    tuple[go.Figure, html.Div]
    """
    df = filter_by_region(load_clean_data(), region)

    mediane = df["rfr_moyen"].median()
    moyenne = df["rfr_moyen"].mean()
    titre   = f"RFR moyen – {'France entière' if region == 'Toutes' else region}"

    #  Construction de l'histogramme 
    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=df["rfr_moyen"],
        nbinsx=n_bins,
        name="Communes",
        marker_color="#3498db",
        opacity=0.85,
    ))

    # Ligne médiane
    fig.add_vline(
        x=mediane,
        line_dash="dash", line_color="#e74c3c", line_width=2,
        annotation_text=f"Médiane : {mediane:,.0f} €",
        annotation_position="top right",
        annotation_font_color="#e74c3c",
    )
    # Ligne moyenne
    fig.add_vline(
        x=moyenne,
        line_dash="dot", line_color="#f39c12", line_width=2,
        annotation_text=f"Moyenne : {moyenne:,.0f} €",
        annotation_position="top left",
        annotation_font_color="#f39c12",
    )

    fig.update_layout(
        title=titre,
        xaxis_title="Revenu fiscal de référence moyen par foyer (€)",
        yaxis_title="Nombre de communes",
        xaxis_type=scale,
        plot_bgcolor="white",
        paper_bgcolor="white",
        bargap=0.04,
        legend_title="Légende",
        font={"family": "Arial, sans-serif"},
        margin={"t": 50, "b": 60, "l": 60, "r": 20},
    )
    fig.update_xaxes(gridcolor="#f0f0f0", showgrid=True)
    fig.update_yaxes(gridcolor="#f0f0f0", showgrid=True)

    # Tableau de statistiques 
    stats = df["rfr_moyen"].describe()
    rows  = [
        ("Communes", f"{len(df):,}".replace(",", "\u202f")),
        ("Minimum",  f"{stats['min']:,.0f} €".replace(",", "\u202f")),
        ("1er quartile", f"{stats['25%']:,.0f} €".replace(",", "\u202f")),
        ("Médiane",  f"{stats['50%']:,.0f} €".replace(",", "\u202f")),
        ("Moyenne",  f"{stats['mean']:,.0f} €".replace(",", "\u202f")),
        ("3e quartile", f"{stats['75%']:,.0f} €".replace(",", "\u202f")),
        ("Maximum",  f"{stats['max']:,.0f} €".replace(",", "\u202f")),
    ]
    cell = {"padding": "6px 14px", "border": "1px solid #dde3ed", "textAlign": "right"}
    table = html.Table([
        html.Thead(html.Tr([
            html.Th("Statistique", style={**cell, "background": "#2c3e50", "color": "white", "textAlign": "left"}),
            html.Th("Valeur",      style={**cell, "background": "#2c3e50", "color": "white"}),
        ])),
        html.Tbody([
            html.Tr([
                html.Td(label, style={**cell, "textAlign": "left", "background": "#fafcff"}),
                html.Td(value, style=cell),
            ]) for label, value in rows
        ]),
    ], style={"borderCollapse": "collapse", "fontSize": "0.88rem"})

    stats_div = html.Div([
        html.H4("Statistiques descriptives", style={"marginBottom": "8px"}),
        table,
    ])

    return fig, stats_div
