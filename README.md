# Inégalités de revenus par commune en France (2002)

Dashboard interactif explorant la distribution et la géographie des revenus
fiscaux de référence des communes françaises, à partir des données publiques DGFiP.

---

## User Guide

### Prérequis
- Python 3.11 ou supérieur
- pip

Le dashboard génère automatiquement les données nettoyées au premier lancement.

### Pages disponibles

| Page | URL | Description |
|---|---|---|
| Accueil | `/` | KPIs et navigation |
| Histogramme | `/histogramme` | Distribution du RFR moyen, filtre région + nb classes |
| Carte | `/carte` | Scatter map géolocalisé, 3 variables disponibles |
| À propos | `/about` | Sources, technologies, installation |

---

## Data

| Fichier | Source | Description |
|---|---|---|
| `data/raw/ircom-communes-revenus-2002.xlsx` | [DGFiP / data.gouv.fr](https://www.data.gouv.fr/fr/datasets/impot-sur-le-revenu-par-commune/) | Revenus fiscaux de référence par tranche et par commune (36 000+ communes) |
| `data/raw/communes-france-2025.csv` | [data.gouv.fr](https://www.data.gouv.fr/fr/datasets/communes-de-france-base-des-codes-postaux/) | Référentiel géographique des communes (coordonnées GPS, population, région…) |
| `data/cleaned/revenus_communes.csv` | Généré automatiquement | Fusion et nettoyage des deux sources ci-dessus |

La jointure est faite sur le **code INSEE** à 5 caractères (2 chiffres département + 3 chiffres commune).

---
### Architecture du code

```mermaid
flowchart TD
    A[main.py] --> B[prepare_data]
    B --> C[src/utils/get_data.py\nVérification fichiers bruts]
    B --> D[src/utils/clean_data.py\nNettoyage et fusion]
    D --> E[data/cleaned/revenus_communes.csv]

    A --> F[Dash App]
    F --> G[src/components/header.py]
    F --> H[src/components/navbar.py]
    F --> I[src/components/footer.py]
    F --> J[Callback routing\nurl → page-content]

    J --> K[src/pages/home.py]
    J --> L[src/pages/histogramme.py]
    J --> M[src/pages/carte.py]
    J --> N[src/pages/about.py]

    L --> O[src/utils/common_functions.py\nload_clean_data / filter_by_region]
    M --> O
    K --> O
```

### Ajouter une page

1. Créer `src/pages/ma_page.py` avec une fonction `layout() -> html.Div`.
2. L'importer dans `main.py` : `from src.pages import ma_page`
3. Ajouter l'entrée dans `_ROUTES` dans `main.py`.
4. Ajouter le lien dans `src/components/navbar.py`.

### Ajouter un graphique à une page existante

1. Créer (ou modifier) un composant dans `src/components/`.
2. Insérer le composant dans le `layout()` de la page.
3. Déclarer le `@callback` dans le même fichier avec des IDs uniques.

---

## Rapport d'analyse

### Conclusions principales

- **Forte inégalité** : le RFR moyen par foyer varie de ~2 100 € à ~189 000 € selon les communes.
- **Distribution asymétrique** : la grande majorité des communes se situe entre 8 000 € et 20 000 €, avec une longue queue vers les hauts revenus.
- **Concentration géographique** : les communes à forts revenus se concentrent en Île-de-France, sur la Côte d'Azur et dans les grandes métropoles.
- **Médiane nationale** : ~13 650 € par foyer fiscal, significativement inférieure à la moyenne (~15 800 €), ce qui confirme l'asymétrie de la distribution.

---
