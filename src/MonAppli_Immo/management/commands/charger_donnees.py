from datetime import datetime
from pathlib import Path
import re
import unicodedata

import pandas as pd
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.db import DatabaseError, transaction

from MonAppli_Immo.models import (
    Acheteur, Agent, BienImmobilier, Criteres, PortefeuilleAcheteur,
    PortefeuilleVendeur, SuiviBienAcheteur, SuiviBienVendeur, Vendeur,
)


class Command(BaseCommand):
    help = "Charge les CSV de démonstration dans la base Django."

    def add_arguments(self, parser):
        parser.add_argument("--data-dir", type=Path, default=settings.DATA_DIR / "demo")

    def handle(self, *args, **options):
        dossier = options["data_dir"]
        try:
            with transaction.atomic():
                importer_agents(dossier / "agents.csv")
                importer_vendeurs(dossier / "vendeurs.csv")
                acheteurs = importer_acheteurs(dossier / "acheteurs.csv")
                importer_biens(dossier / "biens.csv")
                vendeurs = importer_portefeuilles(
                    dossier / "portefeuille_vendeurs.csv", PortefeuilleVendeur, Vendeur, "vendeur"
                )
                portefeuilles_acheteurs = importer_portefeuilles(
                    dossier / "portefeuille_acheteurs.csv", PortefeuilleAcheteur, Acheteur, "acheteur"
                )
                suivis = (
                    ("suivi_bien_vendeurs.csv", importer_suivi_vendeurs, vendeurs),
                    ("suivi_bien_acheteurs.csv", importer_suivi_acheteurs, portefeuilles_acheteurs),
                    ("criteres.csv", importer_criteres, acheteurs),
                )
                for nom, importer, references in suivis:
                    chemin = dossier / nom
                    if chemin.is_file() or dossier == settings.DATA_DIR / "demo":
                        importer(chemin, references)
        except (OSError, ValueError, KeyError, ObjectDoesNotExist, DatabaseError) as exc:
            raise CommandError(f"Échec du chargement depuis {dossier} : {exc}") from exc
        self.stdout.write(self.style.SUCCESS("Données de démonstration chargées."))


def normalize_email(email):
    return unicodedata.normalize('NFKD', email).encode('ASCII', 'ignore').decode('utf-8') # Normalisation de l'email

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None # Vérification de la validité de l'email

def parse_bool(val):
    return str(val).strip().lower() in ['1', 'true', 'oui', 'yes'] # Conversion de la valeur en booléen

# --- Fonctions d'import ---
def importer_agents(path):
    df = pd.read_csv(path, encoding='utf-8', keep_default_na=False)
    for _, row in df.iterrows():
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

def importer_vendeurs(path):
    df = pd.read_csv(path, encoding='utf-8', keep_default_na=False)
    for _, row in df.iterrows():
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

def importer_acheteurs(path):
    references = {}
    df = pd.read_csv(path, encoding='utf-8', keep_default_na=False)
    for index, row in df.iterrows():
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
        references[index + 1] = Acheteur.objects.get(email=email)
    return references

def importer_biens(path):
    df = pd.read_csv(path, encoding='utf-8', keep_default_na=False)
    for _, row in df.iterrows():
        if not BienImmobilier.objects.filter(url_wikipedia=row["url_wikipedia"]).exists():
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
                latitude=float(row["latitude"]),
                longitude=float(row["longitude"]),
                url_wikipedia=row["url_wikipedia"]
            )

def importer_portefeuilles(path, modele, personne, cle_personne):
    references = {}
    for _, row in pd.read_csv(path, keep_default_na=False).iterrows():
        agent = Agent.objects.get(email=normalize_email(row["agent.email"]))
        contact = personne.objects.get(email=normalize_email(row[f"{cle_personne}.email"]))
        bien = BienImmobilier.objects.get(url_wikipedia=row["bien.url_wikipedia"])
        contact_et_agent = {"agent": agent, cle_personne: contact}
        if personne is Vendeur:
            portefeuille, _ = modele.objects.get_or_create(bien=bien, defaults=contact_et_agent)
        else:
            portefeuille, _ = modele.objects.get_or_create(bien=bien, **contact_et_agent)

        if portefeuille not in references.values():
            references[len(references) + 1] = portefeuille
    return references


def importer_suivi_vendeurs(path, references):
    df = pd.read_csv(path, encoding='utf-8', keep_default_na=False)
    for _, row in df.iterrows():
        portefeuille_vendeur = references[int(row["pv.id"])]
        SuiviBienVendeur.objects.get_or_create(
            pv=portefeuille_vendeur,
            canal=row["canal"],
            etat_bien=row["etat_bien"],
            date_suivi=datetime.strptime(row["date_suivi"], "%Y-%m-%d").date(),
            commentaire=row["commentaire"]
        )

def importer_suivi_acheteurs(path, references):
    df = pd.read_csv(path, encoding='utf-8', keep_default_na=False)
    for _, row in df.iterrows():
        portefeuille_acheteur = references[int(row["pa.id"])]
        SuiviBienAcheteur.objects.get_or_create(
            pa=portefeuille_acheteur,
            canal=row["canal"],
            etat_bien=row["etat_bien"],
            date_suivi=datetime.strptime(row["date_suivi"], "%Y-%m-%d").date(),
            feedback=row["feedback"]
        )

def importer_criteres(path, references):
    df = pd.read_csv(path, encoding='utf-8', keep_default_na=False)
    for _, row in df.iterrows():
        acheteur = references[int(row["acheteur.id"])]
        Criteres.objects.get_or_create(
            acheteur=acheteur,
            type_bien=row["type_bien"],
            categorie=row["categorie"],
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
