# utils.py
import os
from django.conf import settings
from pathlib import Path
import csv
from math import radians, sin, cos, sqrt, atan2


VILLES_CSV_PATH = Path(settings.BASE_DIR) / 'data' / 'villes.csv'
if not VILLES_CSV_PATH.exists():
    raise FileNotFoundError(f"Fichier villes.csv introuvable : {VILLES_CSV_PATH}")

# methode pour calculer la distance entre deux points géographiques
# en utilisant la formule de Haversine 
def haversine(lat1, lon1, lat2, lon2):
    # Rayon de la Terre en km
    R = 6371.0

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c  # Distance en kilomètres

# méthode pour obtenir les coordonnées GPS à partir de la ville et/ou du code postal
def get_reference_coordinates(ville=None, code_postal=None):
    with open(VILLES_CSV_PATH, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if code_postal and row['code_postal'] == str(code_postal):
                return float(row['latitude']), float(row['longitude'])
            if ville and row['ville'].strip().lower() == ville.strip().lower():
                return float(row['latitude']), float(row['longitude'])
    return None, None

