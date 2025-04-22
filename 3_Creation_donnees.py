import os
import django

# 🛠 Configuration Django AVANT d'importer les modèles
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projet_Immobilier.settings")
django.setup()

# ✅ Django est prêt, maintenant tu peux importer les modèles
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import re
from MonAppli_Immo.models import PortefeuilleVendeur, PortefeuilleAcheteur, Acheteur
from MonAppli_Immo.choices import *
from faker import Faker

fake = Faker('fr_FR')


# S'assurer que le dossier de données existe
os.makedirs("data", exist_ok=True)

# Ajouter une seed pour la reproductibilité
random.seed(42)
Faker.seed(42)

# -------------------------------------------------------#
""" Données """
# Charger les villes + codes postaux + géopoints depuis le fichier de datagouv
try:
    base = pd.read_csv("data/base_code.csv", encoding="utf-8")
except FileNotFoundError:
    print("❌ Le fichier 'base_code.csv' est introuvable. Vérifiez le chemin.")
    exit(1)
# Nettoyage : On supprime les lignes où il n'y a pas de nom de commune, code postal ou géopoint
base = base.dropna(subset=["nom_de_la_commune", "code_postal", "_geopoint"])
# On supprime les doublons sur commune + code postal pour ne pas avoir trop de redondance
base = base.drop_duplicates(subset=["nom_de_la_commune", "code_postal"])


# ----------- Création de données fictives pour les agents -------------------------------------------#

def nom_agence_en_domaine(nom_agence):
    domaine = re.sub(r"[^a-zA-Z0-9]", "", nom_agence.replace(" ", "")).lower()
    return f"{domaine}.fr"

def genere_email(prenom, nom, agence):
    formats = [
        f"{prenom}.{nom}",
        f"{prenom[0]}.{nom}",
        f"{prenom}{random.randint(1,99)}",
        f"{nom}_{prenom}",
        f"{prenom}.{nom}{random.randint(10,99)}",
        f"{prenom[0]}{nom}",
        f"{nom}.{prenom[0]}",
    ]
    base_email = random.choice(formats).lower().replace(" ", "")
    domaine = nom_agence_en_domaine(agence)
    return f"{base_email}@{domaine}"

def genere_telephone():
    prefixe = random.choice(["06", "07", "01", "02"])
    return f"{prefixe} {fake.msisdn()[2:4]} {fake.msisdn()[4:6]} {fake.msisdn()[6:8]} {fake.msisdn()[8:10]}"

def generer_agents(nb=10):
    agents = []
    for _ in range(nb):
        prenom = fake.first_name()
        nom = fake.last_name()
        agence = fake.company()
        email = genere_email(prenom, nom, agence)
        telephone = genere_telephone()

        ville_info = base.sample(1).iloc[0]
        code_postal = int(ville_info["code_postal"])
        ville = ville_info["nom_de_la_commune"]

        agents.append({
            "nom": nom,
            "prenom": prenom,
            "email": email,
            "telephone": telephone,
            "agence": agence,
            "code_postal_agence": code_postal,
            "ville_agence": ville
        })
    return agents

# Convertir en DataFrame et exporter
agents = generer_agents(10)
df_agents = pd.DataFrame(agents)
df_agents.to_csv("data/agents.csv", index=False, encoding='utf-8')
print("✅ Fichier 'agents.csv' généré avec succès.")

# ----------- Création de données fictives pour les vendeurs et acheteurs --------------------------------------------#

def generer_email_vendeur_acheteur(prenom, nom):
    domaines = ["gmail.com", "orange.fr", "laposte.net", "free.fr", "protonmail.com", "yahoo.fr", "hotmail.fr"]
    formats = [
        f"{prenom}.{nom}",
        f"{prenom[0]}.{nom}",
        f"{prenom}{random.randint(1,99)}",
        f"{nom}_{prenom}",
        f"{prenom}.{nom}{random.randint(10,99)}",
        f"{prenom[0]}{nom}",
        f"{nom}.{prenom[0]}",
    ]
    base_format = random.choice(formats).lower().replace(" ", "")
    domaine = random.choice(domaines)
    return f"{base_format}@{domaine}"

def generer_personnes(nb=15):
    personnes = []
    for _ in range(nb):
        prenom = fake.first_name()
        nom = fake.last_name()
        email = generer_email_vendeur_acheteur(prenom, nom)
        telephone = genere_telephone()

        ville_info = base.sample(1).iloc[0]
        code_postal = int(ville_info["code_postal"])
        ville = ville_info["nom_de_la_commune"]

        personnes.append({
            "nom": nom,
            "prenom": prenom,
            "email": email,
            "telephone": telephone,
            "code_postal": code_postal,
            "ville": ville
        })
    return personnes

# Générer les acheteurs et vendeurs
acheteurs = generer_personnes(15)
vendeurs = generer_personnes(15)

# Convertir en DataFrame et exporter
df_acheteurs = pd.DataFrame(acheteurs)
df_vendeurs = pd.DataFrame(vendeurs)
df_acheteurs.to_csv("data/acheteurs.csv", index=False, encoding='utf-8')
df_vendeurs.to_csv("data/vendeurs.csv", index=False, encoding='utf-8')
print("✅ Fichiers 'acheteurs.csv' et 'vendeurs.csv' générés avec succès.")

# ----------- Création de données fictives pour les biens immobiliers --------------------------------------------#

biens = []

for _ in range(15):
    ville_info = base.sample(1).iloc[0]
    type_bien = random.choice([choice[0] for choice in TYPES_BIEN])
    categorie = random.choice([choice[0] for choice in CATEGORIES])
    numero_voie = str(random.randint(1, 250))
    type_voie = random.choice([choice[0] for choice in TYPE_VOIE])
    nom_voie_complet = fake.street_name()
    nom_voie = " ".join(nom_voie_complet.split()[1:]) if len(nom_voie_complet.split()) > 1 else nom_voie_complet
    code_postal = int(ville_info["code_postal"])
    ville = ville_info["nom_de_la_commune"]
    coordonnees_gps = ville_info["_geopoint"]
    nb_pieces = random.randint(1, 10)
    superficie = random.randint(80, 500)
    prix = round(random.uniform(390, 1500000), 2)
    date_disponibilite = datetime.now().date() + timedelta(days=random.randint(30, 120))
    statut = random.choice([choice[0] for choice in STATUTS_BIEN])

    bien = {
        "type_bien": type_bien,
        "categorie": categorie,
        "numero_voie": numero_voie,
        "type_voie": type_voie,
        "nom_voie": nom_voie,
        "code_postal": code_postal,
        "ville": ville,
        "nb_pieces": nb_pieces,
        "superficie": superficie,
        "parking": bool(random.getrandbits(1)),
        "balcon": bool(random.getrandbits(1)),
        "ascenseur": bool(random.getrandbits(1)),
        "jardin": bool(random.getrandbits(1)),
        "piscine": bool(random.getrandbits(1)),
        "prix": prix,
        "date_disponibilite": date_disponibilite,
        "descriptions": fake.text(max_nb_chars=200),
        "statut": statut,
        "coordonnees_gps": coordonnees_gps,
    }

    biens.append(bien)

# Convertir en DataFrame et exporter
df_biens = pd.DataFrame(biens)
df_biens.to_csv("data/biens.csv", index=False, encoding="utf-8")
print("✅ Fichier 'biens.csv' généré avec succès.")

# ----------- Création de données fictives pour les portefeuilles vendeurs et acheteurs --------------------------------------------#

def generer_portefeuilles_vendeurs():
    portefeuilles = []
    for i in range(len(biens)):
        agent_choisi = random.choice(agents)
        vendeur = random.choice(vendeurs)
        bien = biens[i]  # On prend le bien dans l'ordre de la liste

        portefeuilles.append({
            "email_agent": agent_choisi["email"],
            "email_vendeur": vendeur["email"],
            "coordonnees_gps_bien": bien["coordonnees_gps"]
        })
    return portefeuilles

def generer_portefeuilles_acheteurs():
    portefeuilles = []
    for _ in range(len(biens)):
        agent_choisi = random.choice(agents)
        acheteur = random.choice(acheteurs)
        bien = random.choice(biens)

        portefeuilles.append({
            "email_agent": agent_choisi["email"],
            "email_acheteur": acheteur["email"],
            "coordonnees_gps_bien": bien["coordonnees_gps"]
        })
    return portefeuilles
 

portefeuilles_vendeurs = generer_portefeuilles_vendeurs()
portefeuilles_acheteurs = generer_portefeuilles_acheteurs()

df_portefeuille_acheteurs = pd.DataFrame(portefeuilles_acheteurs)
df_portefeuille_vendeurs = pd.DataFrame(portefeuilles_vendeurs)
df_portefeuille_acheteurs.to_csv("data/portefeuille_acheteurs.csv", index=False, encoding='utf-8')
df_portefeuille_vendeurs.to_csv("data/portefeuille_vendeurs.csv", index=False, encoding='utf-8')
print("✅ Fichiers 'portefeuille_acheteurs.csv' et 'portefeuille_vendeurs.csv' générés avec succès.")


#""" LANCER APRÈS AVOIR FAIT 1er PEUPLEMENT DE LA BASE DE DONNÉES """

"""
# ----------- Création de données fictives pour les suivis des biens vendeurs et acheteurs --------------------------------------------#

def generer_suivi_bien_vendeur(portefeuilles_vendeur, nb=30):
    suivis = []
    for _ in range(nb):
        pv = random.choice(portefeuilles_vendeur)
        suivis.append({
            "id_pv": pv.id,  # 🔁 utilise le vrai id en base
            "canal": random.choice([choice[0] for choice in CANAL_VENDEURS]),
            "etat_bien": random.choice([choice[0] for choice in ETAT_VENDEURS]),
            "date_suivi": datetime.now().date() - timedelta(days=random.randint(0, 60)),
            "commentaire": fake.sentence(nb_words=10)
        })
    return suivis

def generer_suivi_bien_acheteur(portefeuilles_acheteur, nb=30):
    suivis = []
    for _ in range(nb):
        pa = random.choice(portefeuilles_acheteur)
        suivis.append({
            "id_pa": pa.id,  # 🔁 utilise le vrai id en base
            "canal": random.choice([choice[0] for choice in CANAL_ACHETEURS]),
            "etat_bien": random.choice([choice[0] for choice in ETAT_ACHETEURS]),
            "date_suivi": datetime.now().date() - timedelta(days=random.randint(0, 60)),
            "feedback": fake.sentence(nb_words=12)
        })
    return suivis

portefeuilles_vendeurs = list(PortefeuilleVendeur.objects.all())
suivis_vendeur = generer_suivi_bien_vendeur(portefeuilles_vendeurs)

portefeuilles_acheteurs = list(PortefeuilleAcheteur.objects.all())
suivis_acheteur = generer_suivi_bien_acheteur(portefeuilles_acheteurs)

df_suivi_vendeur = pd.DataFrame(suivis_vendeur)
df_suivi_acheteur = pd.DataFrame(suivis_acheteur)
df_suivi_vendeur.to_csv("data/suivibien_vendeurs.csv", index=False, encoding='utf-8')
df_suivi_acheteur.to_csv("data/suivibien_acheteurs.csv", index=False, encoding='utf-8')
print("✅ Fichiers 'suivibien_vendeurs.csv' et 'suivibien_acheteurs.csv' générés avec succès.")

# ----------- Création de données fictives pour les critères de recherches --------------------------------------------#

def generer_criteres(acheteurs):
    criteres = []
    acheteurs =Acheteur.objects.all()
    for acheteur in acheteurs :
        nb_pieces_min = random.randint(1, 3)
        nb_pieces_max = random.randint(nb_pieces_min + 1, 10)
        superficie_min = random.randint(80, 150)
        superficie_max = superficie_min + random.randint(20, 500)
        budget_max = round(random.uniform(400, 2000000), 2)
        ville_info = base.sample(1).iloc[0]

        criteres.append({
            "id_acheteur": acheteur.id,  # 🔁 utilise le vrai id en base
            "nb_pieces_min": nb_pieces_min,
            "nb_pieces_max": nb_pieces_max,
            "superficie_min": superficie_min,
            "superficie_max": superficie_max,
            "budget_max": budget_max,
            "parking": bool(random.getrandbits(1)),
            "balcon": bool(random.getrandbits(1)),
            "ascenseur": bool(random.getrandbits(1)),
            "jardin": bool(random.getrandbits(1)),
            "piscine": bool(random.getrandbits(1)),
            "code_postal": int(ville_info["code_postal"]),
            "ville": ville_info["nom_de_la_commune"],
            "date_emmenagement": datetime.now().date() + timedelta(days=random.randint(30, 120))
        })
    return criteres

criteres_acheteurs = generer_criteres(acheteurs)
df_criteres = pd.DataFrame(criteres_acheteurs)
df_criteres.to_csv("data/criteres.csv", index=False, encoding='utf-8')
print("✅ Fichier 'criteres.csv' généré avec succès.")

"""