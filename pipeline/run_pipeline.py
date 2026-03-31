"""
Orchestrateur Principal du Pipeline Urban Data Explorer
Auteurs : Adam BELOUCIF, Arnaud DISSONGO, Emilien MORICE
Rôle : Exécution séquentielle des phases Bronze, Silver et Gold.
       Audit final de la qualité des données.
"""

import sys
import os
import time

# Ajouter le chemin courant pour les imports locaux
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import ingest
import transform
import aggregate
import data_quality

def run_main_pipeline():
    """Point d'entrée global pour le rafraîchissement des données."""
    start_time = time.time()
    
    print("\n" + "#"*60)
    print("STARTING URBAN DATA EXPLORER PIPELINE")
    print("#"*60)
    
    # Étape 1 : Ingestion (Bronze Layer)
    ingest.ingest_all()
    
    # Étape 2 : Transformation Spatiale (Silver Layer)
    transform.process_all()
    
    # Étape 3 : Calcul des Indicateurs (Gold Layer)
    aggregate.process_all()
    
    # Étape 4 : Audit de Qualité (DataOps Phase)
    data_quality.audit_pipeline()
    
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "="*60)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print(f"Total Duration: {duration:.2f} seconds")
    print("="*60 + "\n")

if __name__ == "__main__":
    run_main_pipeline()
