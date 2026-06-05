"""
get_data.py
Vérifie la présence des fichiers bruts dans data/raw/.
Les fichiers sont fournis localement (Open Data statique).
Le dashboard peut s'exécuter sans connexion internet.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import config


def check_raw_files() -> bool:
    """
    Vérifie que les deux fichiers bruts nécessaires sont présents.

    Returns
    bool
        True si tous les fichiers sont présents.
    """
    required = {
        "Revenus IRCOM 2002 (DGFiP)":   config.RAW_REVENUS,
        "Référentiel communes 2025":     config.RAW_COMMUNES,
    }
    all_ok = True
    for name, path in required.items():
        status = "OK" if path.exists() else "MANQUANT"
        print(f"  [{status}] {name} → {path.name}")
        if not path.exists():
            all_ok = False
    return all_ok


if __name__ == "__main__":
    ok = check_raw_files()
    if not ok:
        sys.exit(1)
