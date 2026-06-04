"""
header.py
Composant en-tête du dashboard : titre et sous-titre source.
"""

from dash import html
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import config


def create_header() -> html.Div:
    """Retourne le composant HTML de l'en-tête principal."""
    return html.Div(
        children=[
            html.H1(
                config.APP_TITLE,
                style={"margin": "0", "fontSize": "1.35rem", "fontWeight": "700"},
            ),
            html.Span(
                "Source : DGFiP – IRCOM 2002  |  Référentiel communes 2025 (data.gouv.fr)",
                style={"fontSize": "0.78rem", "opacity": "0.75"},
            ),
        ],
        style={
            "backgroundColor": "#1a252f",
            "color": "white",
            "padding": "14px 28px",
            "display": "flex",
            "flexDirection": "column",
            "gap": "4px",
        },
    )
