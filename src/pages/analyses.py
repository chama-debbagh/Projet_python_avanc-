"""
analyses.py
Page "Analyses" avec 7 onglets de visualisations avancées :
  1. Barplot    – RFR moyen par région
  2. Boxplot    – Distribution du RFR par région
  3. Scatter    – RFR vs taux d'imposition
  4. Top/Flop   – Top 10 / Flop 10 communes
  5. Population – RFR moyen par tranche de population
  6. Pie        – Répartition des foyers fiscaux par région
  7. Heatmap    – Corrélation entre variables numériques
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from dash import html, dcc, callback, Input, Output

from src.utils.common_functions import (
    load_clean_data,
    get_region_options,
    filter_by_region,
    #TRANCHE_ORDER,
    tranche_population,
)

#  Palette de couleurs cohérente 
PALETTE = px.colors.qualitative.Set2

#  Style de la barre de filtres 
FILTER_STYLE = {
    "display": "flex", "gap": "28px", "flexWrap": "wrap",
    "alignItems": "flex-start", "marginBottom": "20px",
    "background": "#f7f9fc", "padding": "14px 20px",
    "borderRadius": "8px", "border": "1px solid #dde3ed",
}

#  Layout principal 

def layout() -> html.Div:
    """Retourne la page Analyses complète avec 7 onglets."""
    df      = load_clean_data()
    options = get_region_options(df)

    tabs = dcc.Tabs(
        id="analyses-tabs",
        value="barplot",
        children=[
            dcc.Tab(label="Barplot",    value="barplot"),
            dcc.Tab(label="Boxplot",    value="boxplot"),
            dcc.Tab(label="Scatter",    value="scatter"),
            dcc.Tab(label="Top / Flop", value="topflop"),
            dcc.Tab(label="Population", value="population"),
            dcc.Tab(label="Pie chart",  value="pie"),
            dcc.Tab(label="Heatmap",    value="heatmap"),
        ],
        style={"marginBottom": "0"},
        colors={"border": "#dde3ed", "primary": "#2980b9", "background": "#f7f9fc"},
    )

    return html.Div([
        html.H2("Analyses approfondies"),
        html.P(
            "Explorez les données sous différents angles : comparaisons régionales, "
            "distributions, corrélations et classements.",
            style={"color": "#666", "marginBottom": "20px"},
        ),
        tabs,
        html.Div(id="analyses-content", style={"paddingTop": "8px"}),
    ], style={"padding": "24px 32px"})


# Callback principal : rendu du contenu selon l'onglet 

@callback(
    Output("analyses-content", "children"),
    Input("analyses-tabs", "value"),
)
def render_tab(tab: str) -> html.Div:
    """
    Sélectionne et retourne le sous-layout de l'onglet actif.

    Parameters
    tab : str  Valeur de l'onglet sélectionné
    """
    renderers = {
        "barplot":    _tab_barplot,
        "boxplot":    _tab_boxplot,
        "scatter":    _tab_scatter,
        "topflop":    _tab_topflop,
        "population": _tab_population,
        "pie":        _tab_pie,
        "heatmap":    _tab_heatmap,
    }
    return renderers[tab]()



# ONGLET 1 : BARPLOT : RFR moyen par région


def _tab_barplot() -> html.Div:
    return html.Div([
        html.H3("RFR moyen par région"),
        html.Div([
            html.Div([
                html.Label("Variable", style={"fontWeight":"600","display":"block","marginBottom":"4px"}),
                dcc.RadioItems(
                    id="bar-variable",
                    options=[
                        {"label": "RFR moyen (€)",          "value": "rfr_moyen"},
                        {"label": "Taux d'imposition (%)",   "value": "taux_imposition"},
                        {"label": "Nb foyers (médiane)",     "value": "nb_foyers"},
                    ],
                    value="rfr_moyen", inline=True,
                    inputStyle={"marginRight":"4px"}, labelStyle={"marginRight":"16px"},
                ),
            ]),
            html.Div([
                html.Label("Tri", style={"fontWeight":"600","display":"block","marginBottom":"4px"}),
                dcc.RadioItems(
                    id="bar-sort",
                    options=[{"label":"Croissant","value":"asc"},{"label":"Décroissant","value":"desc"}],
                    value="desc", inline=True,
                    inputStyle={"marginRight":"4px"}, labelStyle={"marginRight":"16px"},
                ),
            ]),
        ], style=FILTER_STYLE),
        dcc.Graph(id="bar-graph", style={"height":"500px"}),
    ])


@callback(
    Output("bar-graph", "figure"),
    Input("bar-variable", "value"),
    Input("bar-sort",     "value"),
)
def update_barplot(variable: str, sort: str) -> go.Figure:
    """
    Barplot horizontal du RFR médian (ou autre variable) par région.

    Parameters
    variable : str  Colonne à agréger
    sort     : str  « asc » ou « desc »
    """
    df = load_clean_data().dropna(subset=[variable, "reg_nom"])

    agg = (df.groupby("reg_nom")[variable]
             .median()
             .reset_index()
             .rename(columns={variable: "valeur"}))
    agg = agg.sort_values("valeur", ascending=(sort == "asc"))

    labels = {
        "rfr_moyen":       "RFR moyen médian (€)",
        "taux_imposition": "Taux d'imposition médian (%)",
        "nb_foyers":       "Nb foyers médian",
    }
    fig = go.Figure(go.Bar(
        x=agg["valeur"], y=agg["reg_nom"], orientation="h",
        marker=dict(
            color=agg["valeur"],
            colorscale="Blues",
            showscale=True,
            colorbar=dict(title=labels[variable], thickness=12),
        ),
        text=agg["valeur"].apply(lambda v: f"{v:,.0f}".replace(",","\u202f")),
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>" + labels[variable] + " : %{x:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        title=f"{labels[variable]} par région (médiane des communes)",
        xaxis_title=labels[variable],
        yaxis_title="Région",
        plot_bgcolor="white", paper_bgcolor="white",
        margin={"l": 200, "r": 60, "t": 50, "b": 50},
        height=500,
    )
    fig.update_xaxes(gridcolor="#f0f0f0")
    return fig


# ONGLET 2 : BOXPLOT : distribution du RFR par région

def _tab_boxplot() -> html.Div:
    return html.Div([
        html.H3("Distribution du RFR moyen par région"),
        html.Div([
            html.Div([
                html.Label("Variable", style={"fontWeight":"600","display":"block","marginBottom":"4px"}),
                dcc.RadioItems(
                    id="box-variable",
                    options=[
                        {"label": "RFR moyen (€)",         "value": "rfr_moyen"},
                        {"label": "Taux d'imposition (%)",  "value": "taux_imposition"},
                    ],
                    value="rfr_moyen", inline=True,
                    inputStyle={"marginRight":"4px"}, labelStyle={"marginRight":"16px"},
                ),
            ]),
            html.Div([
                html.Label("Échelle X", style={"fontWeight":"600","display":"block","marginBottom":"4px"}),
                dcc.RadioItems(
                    id="box-scale",
                    options=[{"label":"Linéaire","value":"linear"},{"label":"Log","value":"log"}],
                    value="linear", inline=True,
                    inputStyle={"marginRight":"4px"}, labelStyle={"marginRight":"16px"},
                ),
            ]),
        ], style=FILTER_STYLE),
        dcc.Graph(id="box-graph", style={"height":"580px"}),
    ])


@callback(
    Output("box-graph", "figure"),
    Input("box-variable", "value"),
    Input("box-scale",    "value"),
)
def update_boxplot(variable: str, scale: str) -> go.Figure:
    """Boxplot horizontal du RFR par région, trié par médiane."""
    df = load_clean_data().dropna(subset=[variable, "reg_nom"])

    # Trier les régions par médiane décroissante
    order = (df.groupby("reg_nom")[variable].median()
               .sort_values(ascending=True).index.tolist())

    fig = px.box(
        df, x=variable, y="reg_nom",
        category_orders={"reg_nom": order},
        color="reg_nom",
        color_discrete_sequence=PALETTE,
        labels={variable: "RFR moyen (€)" if variable=="rfr_moyen" else "Taux d'imposition (%)"},
        title=f"Distribution du {'RFR moyen' if variable=='rfr_moyen' else 'taux d imposition'} par région",
        points=False,   # pas de points individuels (trop lourd avec 34 k communes)
    )
    fig.update_layout(
        showlegend=False,
        xaxis_type=scale,
        plot_bgcolor="white", paper_bgcolor="white",
        margin={"l": 200, "r": 40, "t": 50, "b": 50},
        height=580,
    )
    fig.update_xaxes(gridcolor="#f0f0f0", title_text="Valeur")
    fig.update_yaxes(title_text="Région")
    return fig


# ONGLET 3 : SCATTER : RFR vs taux d'imposition

def _tab_scatter() -> html.Div:
    df = load_clean_data()
    options = get_region_options(df)
    return html.Div([
        html.H3("RFR moyen vs taux d'imposition"),
        html.P("Chaque point = une commune. La couleur indique la région.",
               style={"color":"#666","marginBottom":"14px"}),
        html.Div([
            html.Div([
                html.Label("Région", style={"fontWeight":"600","display":"block","marginBottom":"4px"}),
                dcc.Dropdown(id="sc-region", options=options, value="Toutes",
                             clearable=False, style={"minWidth":"240px"}),
            ]),
            html.Div([
                html.Label("Taille des points", style={"fontWeight":"600","display":"block","marginBottom":"4px"}),
                dcc.RadioItems(
                    id="sc-size",
                    options=[{"label":"Uniforme","value":"uniforme"},
                             {"label":"∝ nb foyers","value":"nb_foyers"}],
                    value="uniforme", inline=True,
                    inputStyle={"marginRight":"4px"}, labelStyle={"marginRight":"16px"},
                ),
            ]),
        ], style=FILTER_STYLE),
        dcc.Graph(id="sc-graph", style={"height":"520px"}),
        html.P(id="sc-info", style={"color":"#888","fontSize":"0.85rem","fontStyle":"italic"}),
    ])


@callback(
    Output("sc-graph", "figure"),
    Output("sc-info",  "children"),
    Input("sc-region", "value"),
    Input("sc-size",   "value"),
)
def update_scatter(region: str, size_mode: str) -> tuple:
    """
    Scatter RFR moyen vs taux d'imposition.
    Echantillonne si > 5 000 communes pour fluidité.
    """
    df = filter_by_region(load_clean_data(), region)
    df = df.dropna(subset=["rfr_moyen","taux_imposition"])

    # Sous-échantillonnage pour les performances (France entière = 34 k points)
    sample_info = ""
    if len(df) > 5000:
        df = df.sample(5000, random_state=42)
        sample_info = "⚠ Echantillon de 5 000 communes affiché pour la fluidité."

    size_col = None
    if size_mode == "nb_foyers":
        df = df.copy()
        df["_sz"] = np.sqrt(df["nb_foyers"].clip(lower=1))
        df["_sz"] = df["_sz"].clip(upper=df["_sz"].quantile(0.97))
        size_col = "_sz"

    fig = px.scatter(
        df,
        x="rfr_moyen", y="taux_imposition",
        color="reg_nom" if region == "Toutes" else None,
        size=size_col,
        size_max=16,
        hover_name="nom_standard",
        hover_data={"rfr_moyen":":.0f","taux_imposition":":.1f","dep_nom":True,
                    "_sz":False if size_col else None},
        opacity=0.65,
        color_discrete_sequence=PALETTE,
        labels={"rfr_moyen":"RFR moyen (€)","taux_imposition":"Taux d'imposition (%)"},
        title="RFR moyen vs taux d'imposition effectif",
        trendline="ols",
        trendline_scope="overall",
        trendline_color_override="#e74c3c",
    )
    fig.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                      margin={"t":50,"b":50,"l":60,"r":20})
    fig.update_xaxes(gridcolor="#f0f0f0"); fig.update_yaxes(gridcolor="#f0f0f0")
    return fig, sample_info


# ONGLET 4 : TOP / FLOP 10

def _tab_topflop() -> html.Div:
    df = load_clean_data()
    options = get_region_options(df)
    return html.Div([
        html.H3("Top 10 / Flop 10 communes"),
        html.Div([
            html.Div([
                html.Label("Région", style={"fontWeight":"600","display":"block","marginBottom":"4px"}),
                dcc.Dropdown(id="tf-region", options=options, value="Toutes",
                             clearable=False, style={"minWidth":"240px"}),
            ]),
            html.Div([
                html.Label("Variable", style={"fontWeight":"600","display":"block","marginBottom":"4px"}),
                dcc.RadioItems(
                    id="tf-variable",
                    options=[{"label":"RFR moyen (€)","value":"rfr_moyen"},
                             {"label":"Taux imposition (%)","value":"taux_imposition"},
                             {"label":"Nb foyers","value":"nb_foyers"}],
                    value="rfr_moyen", inline=True,
                    inputStyle={"marginRight":"4px"}, labelStyle={"marginRight":"14px"},
                ),
            ]),
            html.Div([
                html.Label("Nb communes", style={"fontWeight":"600","display":"block","marginBottom":"4px"}),
                dcc.Slider(id="tf-n", min=5, max=20, step=5, value=10,
                           marks={5:"5",10:"10",15:"15",20:"20"},
                           tooltip={"placement":"bottom","always_visible":False}),
            ], style={"minWidth":"220px"}),
        ], style=FILTER_STYLE),
        dcc.Graph(id="tf-graph", style={"height":"560px"}),
    ])


@callback(
    Output("tf-graph","figure"),
    Input("tf-region","value"), Input("tf-variable","value"), Input("tf-n","value"),
)
def update_topflop(region: str, variable: str, n: int) -> go.Figure:
    """Barplot horizontal double : Top N et Flop N côte à côte."""
    df = filter_by_region(load_clean_data(), region).dropna(subset=[variable])
    top  = df.nlargest(n, variable)[["nom_standard","dep_nom",variable]].iloc[::-1]
    flop = df.nsmallest(n, variable)[["nom_standard","dep_nom",variable]]

    label = {"rfr_moyen":"RFR moyen (€)","taux_imposition":"Taux imposition (%)","nb_foyers":"Nb foyers"}[variable]

    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=(f"Top {n} – {label}", f"Flop {n} – {label}"),
                        horizontal_spacing=0.15)

    fig.add_trace(go.Bar(
        x=top[variable], y=top["nom_standard"], orientation="h",
        marker_color="#27ae60", name="Top",
        text=top[variable].apply(lambda v: f"{v:,.0f}".replace(",","\u202f")),
        textposition="outside",
        hovertemplate="<b>%{y}</b> (%{customdata})<br>" + label + " : %{x:,.0f}<extra></extra>",
        customdata=top["dep_nom"],
    ), row=1, col=1)

    fig.add_trace(go.Bar(
        x=flop[variable], y=flop["nom_standard"], orientation="h",
        marker_color="#e74c3c", name="Flop",
        text=flop[variable].apply(lambda v: f"{v:,.0f}".replace(",","\u202f")),
        textposition="outside",
        hovertemplate="<b>%{y}</b> (%{customdata})<br>" + label + " : %{x:,.0f}<extra></extra>",
        customdata=flop["dep_nom"],
    ), row=1, col=2)

    fig.update_layout(showlegend=False, plot_bgcolor="white", paper_bgcolor="white",
                      margin={"l":180,"r":80,"t":60,"b":40}, height=560)
    fig.update_xaxes(gridcolor="#f0f0f0")
    return fig


# ONGLET 5 : POPULATION : RFR par tranche de population

def _tab_population() -> html.Div:
    df = load_clean_data()
    options = get_region_options(df)
    return html.Div([
        html.H3("RFR moyen selon la taille des communes"),
        html.P("Les communes sont regroupées par tranche de population.",
               style={"color":"#666","marginBottom":"14px"}),
        html.Div([
            html.Div([
                html.Label("Région", style={"fontWeight":"600","display":"block","marginBottom":"4px"}),
                dcc.Dropdown(id="pop-region", options=options, value="Toutes",
                             clearable=False, style={"minWidth":"240px"}),
            ]),
            html.Div([
                html.Label("Type de graphique", style={"fontWeight":"600","display":"block","marginBottom":"4px"}),
                dcc.RadioItems(
                    id="pop-type",
                    options=[{"label":"Barplot (médiane)","value":"bar"},
                             {"label":"Violin","value":"violin"}],
                    value="bar", inline=True,
                    inputStyle={"marginRight":"4px"}, labelStyle={"marginRight":"16px"},
                ),
            ]),
        ], style=FILTER_STYLE),
        dcc.Graph(id="pop-graph", style={"height":"480px"}),
    ])


@callback(
    Output("pop-graph","figure"),
    Input("pop-region","value"), Input("pop-type","value"),
)
def update_population(region: str, chart_type: str) -> go.Figure:
    """Barplot ou violin du RFR par tranche de population."""
    df = filter_by_region(load_clean_data(), region).dropna(subset=["rfr_moyen"])
    df = df.copy()
    df["tranche"] = df["population"].apply(tranche_population)
    # Garder uniquement les tranches présentes, dans l'ordre
    order = [t for t in TRANCHE_ORDER if t in df["tranche"].unique()]

    if chart_type == "bar":
        agg = (df.groupby("tranche")["rfr_moyen"]
                 .agg(["median","count"])
                 .reindex(order)
                 .reset_index())
        agg.columns = ["tranche","rfr_median","count"]
        fig = go.Figure(go.Bar(
            x=agg["tranche"], y=agg["rfr_median"],
            marker_color=px.colors.sequential.Blues[3:3+len(order)],
            text=agg["rfr_median"].apply(lambda v: f"{v:,.0f} €".replace(",","\u202f")),
            textposition="outside",
            customdata=agg["count"],
            hovertemplate="<b>%{x}</b><br>RFR médian : %{y:,.0f} €<br>Nb communes : %{customdata}<extra></extra>",
        ))
        fig.update_layout(xaxis_title="Tranche de population", yaxis_title="RFR moyen médian (€)")
    else:
        fig = px.violin(
            df, x="tranche", y="rfr_moyen",
            category_orders={"tranche": order},
            color="tranche", color_discrete_sequence=PALETTE,
            box=True, points=False,
            labels={"rfr_moyen":"RFR moyen (€)","tranche":"Tranche de population"},
        )
        fig.update_layout(showlegend=False)

    fig.update_layout(
        title="RFR moyen par tranche de population",
        plot_bgcolor="white", paper_bgcolor="white",
        margin={"t":50,"b":60,"l":60,"r":20}, height=480,
    )
    fig.update_yaxes(gridcolor="#f0f0f0")
    return fig


# ONGLET 6 : PIE : répartition des foyers par région


def _tab_pie() -> html.Div:
    return html.Div([
        html.H3("Répartition des foyers fiscaux par région"),
        html.Div([
            html.Div([
                html.Label("Variable agrégée", style={"fontWeight":"600","display":"block","marginBottom":"4px"}),
                dcc.RadioItems(
                    id="pie-variable",
                    options=[{"label":"Nb foyers fiscaux","value":"nb_foyers"},
                             {"label":"Nb communes","value":"nb_communes"},
                             {"label":"RFR total (k€)","value":"rfr_total_k"}],
                    value="nb_foyers", inline=True,
                    inputStyle={"marginRight":"4px"}, labelStyle={"marginRight":"16px"},
                ),
            ]),
            html.Div([
                html.Label("Type", style={"fontWeight":"600","display":"block","marginBottom":"4px"}),
                dcc.RadioItems(
                    id="pie-type",
                    options=[{"label":"Camembert","value":"pie"},
                             {"label":"Donut","value":"donut"}],
                    value="donut", inline=True,
                    inputStyle={"marginRight":"4px"}, labelStyle={"marginRight":"16px"},
                ),
            ]),
        ], style=FILTER_STYLE),
        dcc.Graph(id="pie-graph", style={"height":"520px"}),
    ])


@callback(
    Output("pie-graph","figure"),
    Input("pie-variable","value"), Input("pie-type","value"),
)
def update_pie(variable: str, pie_type: str) -> go.Figure:
    """Pie / donut chart des foyers ou communes par région."""
    df = load_clean_data().dropna(subset=["reg_nom"])

    if variable == "nb_communes":
        agg = df.groupby("reg_nom").size().reset_index(name="valeur")
        label_val = "Nb communes"
    else:
        agg = df.groupby("reg_nom")[variable].sum().reset_index(name="valeur")
        label_val = "Nb foyers" if variable == "nb_foyers" else "RFR total (k€)"

    agg = agg.sort_values("valeur", ascending=False)

    fig = go.Figure(go.Pie(
        labels=agg["reg_nom"],
        values=agg["valeur"],
        hole=0.42 if pie_type == "donut" else 0,
        textinfo="label+percent",
        hovertemplate="<b>%{label}</b><br>" + label_val + " : %{value:,.0f}<br>%{percent}<extra></extra>",
        marker=dict(colors=PALETTE * 3),
    ))
    fig.update_layout(
        title=f"{label_val} par région",
        paper_bgcolor="white",
        margin={"t":60,"b":20,"l":20,"r":20},
        height=520,
        legend=dict(orientation="v", x=1.01),
    )
    return fig

# ONGLET 7 : HEATMAP : corrélations entre variables numériques

def _tab_heatmap() -> html.Div:
    df = load_clean_data()
    options = get_region_options(df)
    return html.Div([
        html.H3("Matrice de corrélation entre variables numériques"),
        html.P("Coefficient de Pearson. 1 = corrélation parfaite positive, -1 = parfaite négative.",
               style={"color":"#666","marginBottom":"14px"}),
        html.Div([
            html.Div([
                html.Label("Région", style={"fontWeight":"600","display":"block","marginBottom":"4px"}),
                dcc.Dropdown(id="hm-region", options=options, value="Toutes",
                             clearable=False, style={"minWidth":"240px"}),
            ]),
        ], style=FILTER_STYLE),
        dcc.Graph(id="hm-graph", style={"height":"520px"}),
    ])


@callback(
    Output("hm-graph","figure"),
    Input("hm-region","value"),
)
def update_heatmap(region: str) -> go.Figure:
    """Heatmap de la matrice de corrélation (Pearson) sur les variables numériques."""
    df = filter_by_region(load_clean_data(), region)

    num_cols = {
        "rfr_moyen":       "RFR moyen",
        "taux_imposition": "Taux imposition",
        "nb_foyers":       "Nb foyers",
        "population":      "Population",
        "densite":         "Densité",
        "superficie_km2":  "Superficie",
        "rfr_total_k":     "RFR total",
    }
    available = {k: v for k, v in num_cols.items() if k in df.columns}
    sub = df[list(available.keys())].dropna()
    corr = sub.corr()
    labels = [available[c] for c in corr.columns]

    # Masque triangulaire : on n'affiche que le triangle inférieur
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    corr_masked = corr.where(~mask)

    text_vals = [[f"{v:.2f}" if not np.isnan(v) else "" for v in row] for row in corr_masked.values]

    fig = go.Figure(go.Heatmap(
        z=corr_masked.values,
        x=labels, y=labels,
        text=text_vals,
        texttemplate="%{text}",
        colorscale="RdBu",
        zmid=0, zmin=-1, zmax=1,
        hovertemplate="%{y} × %{x}<br>r = %{z:.3f}<extra></extra>",
        colorbar=dict(title="r de Pearson", thickness=14),
    ))
    fig.update_layout(
        title=f"Corrélations – {'France entière' if region == 'Toutes' else region}",
        paper_bgcolor="white", plot_bgcolor="white",
        margin={"t":60,"b":80,"l":100,"r":20},
        height=520,
        xaxis=dict(side="bottom"),
    )
    return fig
#PYEOF
#echo "analyses.py OK"
#Sortie

#analyses.py OK
