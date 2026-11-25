from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import re
from MonAppli_Immo.choices import TYPES_BIEN, CATEGORIES, TYPE_VOIE, STATUTS_BIEN
from faker import Faker

class Command(BaseCommand):
    help = "Génère les CSV fictifs de base dans un dossier dédié."

    def add_arguments(self, parser):
        parser.add_argument("--output-dir", type=Path, default=settings.DATA_DIR / "generated")

    def handle(self, *args, **options):
        generer_donnees(options["output_dir"])


def generer_donnees(output_dir):
    fake = Faker('fr_FR')


    # S'assurer que le dossier de données existe
    output_dir.mkdir(parents=True, exist_ok=True)

    # Ajouter une seed pour la reproductibilité
    random.seed(42)
    Faker.seed(42)
    np.random.seed(42)


    # -------------------------------------------------------#
    """ Données """
    # Charger les villes + codes postaux + géopoints depuis le fichier de datagouv
    base = pd.read_csv(settings.DATA_DIR / "reference" / "communes_nettoye.csv", encoding="utf-8")


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
            ville = ville_info["nom_de_la_ville"]

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
    df_agents.to_csv(output_dir / "agents.csv", index=False, encoding='utf-8')
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
            ville = ville_info["nom_de_la_ville"]

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
    df_acheteurs.to_csv(output_dir / "acheteurs.csv", index=False, encoding='utf-8')
    df_vendeurs.to_csv(output_dir / "vendeurs.csv", index=False, encoding='utf-8')
    print("✅ Fichiers 'acheteurs.csv' et 'vendeurs.csv' générés avec succès.")


    # ----------- Création de données fictives pour les biens immobiliers --------------------------------------------#

    biens = []

    for _ in range(20):
        type_bien = random.choice([choice[0] for choice in TYPES_BIEN])
        categorie = random.choice([choice[0] for choice in CATEGORIES])
        numero_voie = str(random.randint(1, 250))
        type_voie = random.choice([choice[0] for choice in TYPE_VOIE])
        nom_voie_complet = fake.street_name()
        nom_voie = " ".join(nom_voie_complet.split()[1:]) if len(nom_voie_complet.split()) > 1 else nom_voie_complet
        ville_info = base.sample(1).iloc[0]
        code_postal = int(ville_info["code_postal"])
        ville = ville_info["nom_de_la_ville"]
        nb_pieces = random.randint(1, 10)
        superficie = random.randint(80, 500)
        prix = round(random.uniform(390, 1500000), 2)
        date_disponibilite = datetime.now().date() + timedelta(days=random.randint(30, 120))
        statut = random.choice([choice[0] for choice in STATUTS_BIEN])
        latitude = float(ville_info["latitude"])
        longitude = float(ville_info["longitude"])
        url_wikipedia = ville_info["url_wikipedia"]

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
            "latitude": latitude,
            "longitude": longitude,
            "url_wikipedia": url_wikipedia
        }

        biens.append(bien)

    # Convertir en DataFrame et exporter
    df_biens = pd.DataFrame(biens)
    df_biens.to_csv(output_dir / "biens.csv", index=False, encoding="utf-8")
    print("✅ Fichier 'biens.csv' généré avec succès.")


    # ----------- Création de données fictives pour les portefeuilles vendeurs et acheteurs --------------------------------------------#
    def generer_portefeuilles_vendeurs(biens, agents, vendeurs):
        portefeuilles = []

        # On vérifie qu'on a assez de biens
        if len(biens) < len(vendeurs):
            raise ValueError("Il faut au moins autant de biens que de vendeurs pour garantir qu'ils en aient un pour chaque vendeur.")

        biens_disponibles = biens.copy()
        random.shuffle(biens_disponibles)

        # Étape 1 : assigner un bien unique à chaque vendeur
        for vendeur, bien in zip(vendeurs, biens_disponibles[:len(vendeurs)]):
            agent_choisi = random.choice(agents)
            portefeuilles.append({
                "agent.email": agent_choisi["email"],
                "vendeur.email": vendeur["email"],
                "bien.url_wikipedia": bien["url_wikipedia"]
            })

        biens_disponibles = biens_disponibles[len(vendeurs):]

        # Mettre en cache les agents déjà utilisés
        agents_utilises = {entry["agent.email"] for entry in portefeuilles}

        # Étape 2 : s'assurer que chaque agent ait AU MOINS un bien
        agents_restants = [a for a in agents if a["email"] not in agents_utilises]
        vendeurs_cycle = vendeurs.copy()
        random.shuffle(vendeurs_cycle)

        for agent in agents_restants:
            vendeur = vendeurs_cycle.pop() if vendeurs_cycle else random.choice(vendeurs)
            bien = biens_disponibles.pop() if biens_disponibles else random.choice(biens)
            portefeuilles.append({
                "agent.email": agent["email"],
                "vendeur.email": vendeur["email"],
                "bien.url_wikipedia": bien["url_wikipedia"]
            })

        # Étape 3 : assigner les biens restants aléatoirement à n'importe quel vendeur
        for bien in biens_disponibles:
            agent_choisi = random.choice(agents)
            vendeur = random.choice(vendeurs)
            portefeuilles.append({
                "agent.email": agent_choisi["email"],
                "vendeur.email": vendeur["email"],
                "bien.url_wikipedia": bien["url_wikipedia"]
            })

        return portefeuilles

    portefeuilles_vendeurs = generer_portefeuilles_vendeurs(biens, agents, vendeurs)
    df_portefeuille_vendeurs = pd.DataFrame(portefeuilles_vendeurs)
    df_portefeuille_vendeurs.to_csv(output_dir / "portefeuille_vendeurs.csv", index=False, encoding='utf-8')
    print("✅ Fichier 'portefeuille_vendeurs.csv' généré avec succès.")


    # ----------- Création de données fictives pour les portefeuilles acheteurs --------------------------------------------#

    def generer_portefeuilles_acheteurs(portefeuilles_vendeurs, acheteurs):
        portefeuilles = []

        for pf_vendeur in portefeuilles_vendeurs:
            agent_email = pf_vendeur["agent.email"]
            bien_url = pf_vendeur["bien.url_wikipedia"]

            # Choisir un nombre aléatoire d'acheteurs (entre 1 et tous les acheteurs dispos)
            nb_acheteurs = random.randint(1, len(acheteurs))
            acheteurs_selectionnes = random.sample(acheteurs, nb_acheteurs)

            for acheteur in acheteurs_selectionnes:
                portefeuilles.append({
                    "agent.email": agent_email,
                    "acheteur.email": acheteur["email"],
                    "bien.url_wikipedia": bien_url
                })

        return portefeuilles

    portefeuilles_acheteurs = generer_portefeuilles_acheteurs(portefeuilles_vendeurs, acheteurs)
    df_portefeuille_acheteurs = pd.DataFrame(portefeuilles_acheteurs)
    df_portefeuille_acheteurs.to_csv(output_dir / "portefeuille_acheteurs.csv", index=False, encoding='utf-8')
    print("✅ Fichier 'portefeuille_acheteurs.csv' généré avec succès.")
