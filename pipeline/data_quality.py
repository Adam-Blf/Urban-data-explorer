"""
Module Data Quality Audit (Phase DataOps)
Auteur : Arnaud DISSONGO (Panason1c)
Rôle : Vérification de la complétude et de l'intégrité des couches Silver et Gold.
"""

import os
import json
import pandas as pd
from config import SILVER_DIR, GOLD_DIR

def check_completeness(file_path, required_columns):
    """Calcule le taux de complétude d'un dataset JSON."""
    if not os.path.exists(file_path):
        return "MISSING"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if not data:
        return "EMPTY"
    
    df = pd.DataFrame(data)
    total_cells = len(df) * len(required_columns)
    missing_cells = df[required_columns].isnull().sum().sum()
    
    completeness = (1 - (missing_cells / total_cells)) * 100
    return f"{completeness:.1f}%"

def audit_pipeline():
    """Lance un audit complet sur les couches Silver et Gold."""
    print("\n--- Data Quality Audit (DataOps Phase) ---")
    print("=" * 50)
    
    datasets_to_check = {
        "velib": ["nom", "lat", "lon", "arrondissement"],
        "espaces_verts": ["nom", "surface", "arrondissement"],
        "ecoles": ["nom", "lat", "lon", "arrondissement"],
        "logements_sociaux": ["nb_logements", "arrondissement"]
    }
    
    results = {}
    for name, cols in datasets_to_check.items():
        path = os.path.join(SILVER_DIR, f"{name}.json")
        results[name] = check_completeness(path, cols)
        print(f"Dataset: {name.ljust(25)} | Completeness: {results[name]}")
        
    # Vérification Gold
    gold_path = os.path.join(GOLD_DIR, "indicateurs.json")
    if os.path.exists(gold_path):
        with open(gold_path, 'r', encoding='utf-8') as f:
            gold_data = json.load(f)
        print(f"Gold Layer: {len(gold_data)} districts calculated.")
    else:
        print("Gold Layer: ERROR - indicateurs.json MISSING.")

    print("=" * 50)
    print("Audit finished.\n")

if __name__ == "__main__":
    audit_pipeline()
