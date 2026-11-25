# Projet immobilier

Application Django de gestion immobilière pour un réseau d’agences, réalisée en équipe dans le cadre du Master 2 Data Science. Elle centralise les biens et les contacts et permet de suivre les étapes des transactions.

## Fonctionnalités

- Gestion des biens, vendeurs, acheteurs et agents.
- Recherche de biens et rapprochement avec les critères des acheteurs.
- Consultation du portefeuille d’un agent et du chiffre d’affaires.

## Structure

- [Application Django](src/), avec ses modèles, vues, formulaires et migrations.
- [Schéma relationnel](docs/base-de-donnees/schema-relationnel.pdf) et [modèle SQL](docs/base-de-donnees/modele-relationnel.sql).
- [Données de démonstration](data/demo/) et [référentiels géographiques](data/reference/).
- [Suivi du projet](docs/suivi-projet.txt) et [archives](docs/archives/).

## Lancement local

Prévoir Python 3.11 ou 3.12 et un serveur PostgreSQL avec une base vide dont le compte utilisé peut créer les tables. Depuis la racine du dépôt, sous Bash :

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

export POSTGRES_DB=immo_db
export POSTGRES_USER=postgres
read -rsp 'Mot de passe PostgreSQL : ' POSTGRES_PASSWORD
export POSTGRES_PASSWORD

python src/manage.py migrate
python src/manage.py charger_donnees  # facultatif
python src/manage.py runserver
```

Ouvre [http://127.0.0.1:8000/](http://127.0.0.1:8000/). PostgreSQL utilise par défaut `localhost:5432`. Tu peux régler l’adresse avec `POSTGRES_HOST` et `POSTGRES_PORT`, et définir `DJANGO_SECRET_KEY` pour conserver la même clé entre les redémarrages.

## Générer des données d’exemple

Les CSV fournis dans `data/demo/` couvrent aussi les suivis et les critères.
La génération produit un jeu fictif de base distinct dans `data/generated/`
et laisse les CSV de démonstration en place. Pour charger ce jeu, utilise une
base de test dédiée.

```bash
python src/manage.py generer_donnees
python src/manage.py charger_donnees --data-dir data/generated
```
