"""
navbar.py
Barre de navigation entre les pages du dashboard.
"""

from dash import html, dcc


def create_navbar() -> html.Nav:
    pages = [
        ("Accueil",      "/"),
        ("Histogramme",  "/histogramme"),
        ("Analyses",     "/analyses"),
        ("Carte",        "/carte"),
      #  ("Analyses",  "/analyses"),
        ("À propos",     "/about"),
    ]
    return html.Nav(
        children=[
            dcc.Link(
                label, href=href,
                style={
                    "color": "white",
                    "textDecoration": "none",
                    "padding": "8px 18px",
                    "borderRadius": "4px",
                    "fontSize": "0.9rem",
                    "fontWeight": "500",
                    "transition": "background 0.2s",
                },
            )
            for label, href in pages
        ],
        style={
            "backgroundColor": "#2c3e50",
            "padding": "6px 16px",
            "display": "flex",
            "gap": "4px",
        },
    )
