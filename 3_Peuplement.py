import os
import django
import pandas as pd
from datetime import datetime
import re
import unicodedata
import logging

# --- Configuration Django ---
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projet_Immobilier.settings")
django.setup()

# --- Logger ---
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# --- Imports des modèles ---
from MonAppli_Immo.models import *

# --- Fonctions utilitaires ---
def normalize_email(email):
    return unicodedata.normalize('NFKD', email).encode('ASCII', 'ignore').decode('utf-8')

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

def parse_bool(val):
    return str(val).strip().lower() in ['1', 'true', 'oui', 'yes']

# --- Fonctions d'import ---
def importer_agents(path='data/agents.csv'):
    df = pd.read_csv(path, encoding='utf-8')
    for _, row in df.iterrows():
        try:
            email = normalize_email(row["email"])
            if not is_valid_email(email):
                raise ValueError("Email invalide après nettoyage.")

            if not Agent.objects.filter(email=email).exists():
                Agent.objects.create(
                    nom=row["nom"],
                    prenom=row["prenom"],
                    email=email,
                    telephone=row.get("telephone", ""),
                    agence=row["agence"],
                    code_postal_agence=int(row["code_postal_agence"]),
                    ville_agence=row["ville_agence"]
                )
        except Exception as e:
            logger.error(f"Erreur agent : {e} - ligne: {row.to_dict()}")

def importer_vendeurs(path='data/vendeurs.csv'):
    df = pd.read_csv(path, encoding='utf-8')
    for _, row in df.iterrows():
        try:
            email = normalize_email(row["email"])
            if not is_valid_email(email):
                raise ValueError("Email invalide après nettoyage.")

            if not Vendeur.objects.filter(email=email).exists():
                Vendeur.objects.create(
                    nom=row["nom"],
                    prenom=row["prenom"],
                    email=email,
                    telephone=row.get("telephone", ""),
                    code_postal=int(row["code_postal"]),
                    ville=row["ville"]
                )
        except Exception as e:
            logger.error(f"Erreur vendeur : {e} - ligne: {row.to_dict()}")

def importer_acheteurs(path='data/acheteurs.csv'):
    df = pd.read_csv(path, encoding='utf-8')
    for _, row in df.iterrows():
        try:
            email = normalize_email(row["email"])
            if not is_valid_email(email):
                raise ValueError("Email invalide après nettoyage.")

            if not Acheteur.objects.filter(email=email).exists():
                Acheteur.objects.create(
                    nom=row["nom"],
                    prenom=row["prenom"],
                    email=email,
                    telephone=row.get("telephone", ""),
                    code_postal=int(row["code_postal"]),
                    ville=row["ville"]
                )
        except Exception as e:
            logger.error(f"Erreur acheteur : {e} - ligne: {row.to_dict()}")

def importer_biens(path='data/biens.csv'):
    df = pd.read_csv(path, encoding='utf-8')
    for _, row in df.iterrows():
        try:
            if not BienImmobilier.objects.filter(coordonnees_gps=row["coordonnees_gps"]).exists():
                BienImmobilier.objects.create(
                    type_bien=row["type_bien"],
                    categorie=row["categorie"],
                    numero_voie=row["numero_voie"],
                    type_voie=row["type_voie"],
                    nom_voie=row["nom_voie"],
                    code_postal=int(row["code_postal"]),
                    ville=row["ville"],
                    nb_pieces=int(row["nb_pieces"]),
                    superficie=int(row["superficie"]),
                    parking=parse_bool(row["parking"]),
                    balcon=parse_bool(row["balcon"]),
                    ascenseur=parse_bool(row["ascenseur"]),
                    jardin=parse_bool(row["jardin"]),
                    piscine=parse_bool(row["piscine"]),
                    prix=float(row["prix"]),
                    date_disponibilite=datetime.strptime(row["date_disponibilite"], "%Y-%m-%d").date(),
                    descriptions=row.get("descriptions", ""),
                    statut=row["statut"],
                    coordonnees_gps=row["coordonnees_gps"]
                )
        except Exception as e:
            logger.error(f"Erreur bien immobilier : {e} - ligne: {row.to_dict()}")

def importer_portefeuille_vendeurs(path="data/portefeuille_vendeurs.csv"):
    df = pd.read_csv(path, encoding='utf-8')
    for _, row in df.iterrows():
        try:
            agent = Agent.objects.filter(email=normalize_email(row["agent.email"])).first()
            vendeur = Vendeur.objects.filter(email=normalize_email(row["vendeur.email"])).first()
            bien = BienImmobilier.objects.filter(coordonnees_gps=row["bien.coordonnees_gps"]).first()

            if agent and vendeur and bien:
                # Vérification uniquement sur le bien
                if not PortefeuilleVendeur.objects.filter(bien=bien).exists():
                    PortefeuilleVendeur.objects.create(agent=agent, vendeur=vendeur, bien=bien)
                else:
                    logger.warning(f"🔁 Le bien ID {bien.id} est déjà dans un portefeuille vendeur. Ligne ignorée : {row.to_dict()}")
        except Exception as e:
            logger.error(f"Erreur portefeuille vendeur : {e} - ligne: {row.to_dict()}")

def importer_portefeuille_acheteurs(path="data/portefeuille_acheteurs.csv"):
    df = pd.read_csv(path, encoding='utf-8')
    for _, row in df.iterrows():
        try:
            agent = Agent.objects.filter(email=normalize_email(row["agent.email"])).first()
            acheteur = Acheteur.objects.filter(email=normalize_email(row["acheteur.email"])).first()
            bien = BienImmobilier.objects.filter(coordonnees_gps=row["bien.coordonnees_gps"]).first()

            if agent and acheteur and bien:
                if not PortefeuilleAcheteur.objects.filter(agent=agent, acheteur=acheteur, bien=bien).exists():
                    PortefeuilleAcheteur.objects.create(agent=agent, acheteur=acheteur, bien=bien)
        except Exception as e:
            logger.error(f"Erreur portefeuille acheteur : {e} - ligne: {row.to_dict()}")

# --- Vider la base ---
def reset_base():
    logger.warning("⚠️ Suppression de toutes les données existantes...")
    for model in [SuiviBienAcheteur, SuiviBienVendeur, Criteres, PortefeuilleAcheteur, PortefeuilleVendeur, BienImmobilier, Acheteur, Vendeur, Agent]:
        model.objects.all().delete()
    logger.info("✅ Base réinitialisée.")
"""
# --- Exécution principale ---
if __name__ == "__main__":
    # Décommenter pour réinitialiser
    #reset_base()
    
    logger.info("Importation des agents")
    importer_agents()

    logger.info("Importation des vendeurs")
    importer_vendeurs()

    logger.info("Importation des acheteurs")
    importer_acheteurs()

    logger.info("Importation des biens immobiliers")
    importer_biens()

    logger.info("Importation des portefeuilles vendeurs")
    importer_portefeuille_vendeurs()

    logger.info("Importation des portefeuilles acheteurs")
    importer_portefeuille_acheteurs()
    
    logger.info("✅ Base de données peuplée avec succès Phase 1.")
"""

#""" A LANCER EN DEUXIEME TEMPS """

"""
# --- Importation des suivis et critères ---
def importer_suivi_vendeurs(path="data/suivi_bien_vendeurs.csv"):
    df = pd.read_csv(path, encoding='utf-8')
    for _, row in df.iterrows():
        try:
            portefeuille_vendeur = PortefeuilleVendeur.objects.get(pk=int(row["pv.id"]))
            SuiviBienVendeur.objects.create(
                pv=portefeuille_vendeur, 
                canal=row["canal"],
                etat_bien=row["etat_bien"],
                date_suivi=datetime.strptime(row["date_suivi"], "%Y-%m-%d").date(),
                commentaire=row["commentaire"]
            )
        except Exception as e:
            logger.error(f"Erreur suivi vendeur : {e} - ligne: {row.to_dict()}")

def importer_suivi_acheteurs(path="data/suivi_bien_acheteurs.csv"):
    df = pd.read_csv(path, encoding='utf-8')
    for _, row in df.iterrows():
        try:
            portefeuille_acheteur = PortefeuilleAcheteur.objects.get(pk=int(row["pa.id"]))
            SuiviBienAcheteur.objects.create(
                pa=portefeuille_acheteur,
                canal=row["canal"],
                etat_bien=row["etat_bien"],
                date_suivi=datetime.strptime(row["date_suivi"], "%Y-%m-%d").date(),
                feedback=row["feedback"]
            ) 
        except Exception as e:
            logger.error(f"Erreur suivi acheteur : {e} - ligne: {row.to_dict()}")

def importer_criteres(path="data/criteres.csv"):
    df = pd.read_csv(path, encoding='utf-8')
    for _, row in df.iterrows():
        try:
            acheteur = Acheteur.objects.get(pk=int(row["acheteur.id"]))
            Criteres.objects.create(
                acheteur=acheteur,
                nb_pieces_min=int(row["nb_pieces_min"]),
                nb_pieces_max=int(row["nb_pieces_max"]),
                superficie_min=int(row["superficie_min"]),
                superficie_max=int(row["superficie_max"]),
                budget_max=float(row["budget_max"]),
                parking=parse_bool(row["parking"]),
                balcon=parse_bool(row["balcon"]),
                ascenseur=parse_bool(row["ascenseur"]),
                jardin=parse_bool(row["jardin"]),
                piscine=parse_bool(row["piscine"]),
                code_postal=int(row["code_postal"]),
                ville=row["ville"],
                date_emmenagement=datetime.strptime(row["date_emmenagement"], "%Y-%m-%d").date()
            )
        except Exception as e:
            logger.error(f"Erreur critère de recherche : {e} - ligne: {row.to_dict()}")

# --- Seconde Execution ---
if __name__ == "__main__":
    logger.info("Importation des suivis vendeurs")
    importer_suivi_vendeurs()

    logger.info("Importation des suivis acheteurs")
    importer_suivi_acheteurs()
    
    logger.info("Importation des criteres")
    importer_criteres()

    logger.info("✅ Seconde données importées avec succès.")
   
"""
# --- Fin du script ---