"""
footer.py
Pied de page du dashboard.
"""

from dash import html


def create_footer() -> html.Div:
    """Retourne le composant pied de page."""
    return html.Div(
        html.P(
            "Données publiques Open Data – DGFiP / data.gouv.fr – "
            "Visualisation réalisée avec Dash & Plotly",
            style={"textAlign": "center", "fontSize": "0.75rem",
                   "color": "#888", "margin": "0"},
        ),
        style={
            "padding": "14px",
            "marginTop": "20px",
            "borderTop": "1px solid #e0e0e0",
        },
    )
