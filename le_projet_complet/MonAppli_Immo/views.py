from django.shortcuts import render, redirect,get_object_or_404
from django.db import connection
from django.contrib import messages  # Ajoute cette importation
from django.db.models import Count, Sum, Q, Prefetch, Max
from django.utils.dateparse import parse_date

from .models import *
from .forms import *

# Create your views here.

def accueil(request):
    return render(request, 'MonAppli_Immo/accueil.html')
 

""" 
### Requêtes sur les agents et agences 
"""

#1.**Attributs d'un agent(nom, prénom,email,telephone,agence) déterminé par son nom/prénom ou par son email**
def search_agent(request):
    query = request.GET.get('q', '').strip()  # Récupère la valeur du paramètre 'q' dans la requête GET et supprime les espaces inutiles

    # Si une requête de recherche a été saisie
    if query:
        # Recherche dans le modèle Agent où le nom OU le prénom correspond exactement à la requête (sans tenir compte de la casse)
        agents = Agent.objects.filter(
            Q(nom__iexact=query) | Q(prenom__iexact=query) | Q(email__iexact=query)
        )
    else:
        # Si aucune recherche n'a été saisie, récupérer tous les acheteurs
        agents = Agent.objects.all()
        
    # Retourne la page HTML 'search_agent.html' avec les résultats de la recherche et la requête saisie
    return render(request, 'MonAppli_Immo/search_agent.html', {
        'agents': agents,  # liste des agents trouvés
        'query': query,    # requête de recherche (pour l'afficher dans la barre de recherche)
    })

#2.** Ajouter un agent**
def ajouter_agent(request):
    if request.method == 'POST':
        form = AgentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('search_agent')
    else:
        form = AgentForm()

    return render(request, 'MonAppli_Immo/ajouter_agent.html', {'form': form})

#3.**Afficher le portefeuille Agent(les vendeurs, les acheteurs et les biens)**(code SQL)
def portefeuille_agent(request, agent_id):
    agent = get_object_or_404(Agent, pk=agent_id)
    
    with connection.cursor() as cursor:
        # Vendeurs
        cursor.execute("""
            SELECT DISTINCT V.id,nom, prenom, email, telephone
            FROM public."MonAppli_Immo_vendeur" V
            JOIN public."MonAppli_Immo_portefeuillevendeur" PV
            ON V.id = PV.vendeur_id
            WHERE PV.agent_id = %s
        """, [agent.id])
        vendeurs_raw = cursor.fetchall()
        
        # Supprimer doublons par ID
        vendeurs_dict = {}
        for v in vendeurs_raw:
            vendeurs_dict[v[0]] = v[1:]  # id -> (nom, prenom, email, tel)
        vendeurs = [(k, *v) for k, v in vendeurs_dict.items()]

        # Acheteurs
        cursor.execute("""
            SELECT DISTINCT A.id, nom, prenom, email, telephone
            FROM public."MonAppli_Immo_acheteur" A
            JOIN public."MonAppli_Immo_portefeuilleacheteur" PA
            ON A.id = PA.acheteur_id
            WHERE PA.agent_id = %s
        """, [agent.id])
        acheteurs_raw = cursor.fetchall()
        
        # Supprimer doublons par ID
        acheteurs_dict = {}
        for a in acheteurs_raw:
            acheteurs_dict[a[0]] = a[1:]
        acheteurs = [(k, *v) for k, v in acheteurs_dict.items()]
        
        # Tri par nom et prénom
        acheteurs.sort(key=lambda x: (x[1].lower(), x[2].lower()))


        # Biens (tu peux aussi utiliser DISTINCT si nécessaire)
        cursor.execute("""
            SELECT DISTINCT B.*
            FROM public."MonAppli_Immo_bienimmobilier" B
            JOIN public."MonAppli_Immo_portefeuillevendeur" PV
            ON B.id = PV.bien_id
            WHERE PV.agent_id = %s
        """, [agent.id])
        biens = cursor.fetchall()

    return render(request, 'MonAppli_Immo/portefeuille_agent.html', {
        'agent': agent,
        'vendeurs': vendeurs,
        'acheteurs': acheteurs,
        'biens': biens,
    })
    

#4.**Afficher le chiffre d'affaires par agence / par agent sur une période donnée(code SQL)**
def chiffre_affaires(request):
    ca_agents = []
    ca_agences = []
    form = ChiffreAffairesForm(request.GET or None)

    if form.is_valid():
        date_debut = form.cleaned_data['date_debut']
        date_fin = form.cleaned_data['date_fin']

        with connection.cursor() as cursor:
            # 1. Chiffre d'affaires par agent
            cursor.execute("""
                SELECT a.nom, a.prenom, SUM(b.prix) AS chiffre_affaires
                FROM public."MonAppli_Immo_agent" a
                JOIN public."MonAppli_Immo_portefeuillevendeur" pv ON a.id = pv.agent_id
                JOIN public."MonAppli_Immo_bienimmobilier" b ON pv.bien_id = b.id
                WHERE b.statut='vendu'
                GROUP BY a.nom, a.prenom
                ORDER BY chiffre_affaires DESC
            """, [date_debut, date_fin])
            ca_agents = cursor.fetchall()

            # 2. Chiffre d'affaires par agence
            cursor.execute("""
                SELECT a.agence, SUM(b.prix) AS chiffre_affaires
                FROM public."MonAppli_Immo_agent" a
                JOIN public."MonAppli_Immo_portefeuillevendeur" pv ON a.id = pv.agent_id
                JOIN public."MonAppli_Immo_bienimmobilier" b ON pv.bien_id = b.id
                WHERE b.statut='vendu'
                GROUP BY a.agence
                ORDER BY chiffre_affaires DESC
            """, [date_debut, date_fin])
            ca_agences = cursor.fetchall()

    return render(request, 'MonAppli_Immo/chiffre_affaires.html', {
        'form': form,
        'ca_agents': ca_agents,
        'ca_agences': ca_agences,
    })
    
    
""" 
### Acheteur et Vendeur
"""
  
# ** Ajouter un acheteur/vendeur **
def ajouter_personne(request):
    if request.method == 'POST':
        form = AcheteurVendeurForm(request.POST)
        if form.is_valid():
            type_personne = form.cleaned_data['type_personne']
            donnees = {
                'nom': form.cleaned_data['nom'],
                'prenom': form.cleaned_data['prenom'],
                'email': form.cleaned_data['email'],
                'telephone': form.cleaned_data['telephone'],
                'code_postal': form.cleaned_data['code_postal'],
                'ville': form.cleaned_data['ville'],
            }

            try:
                # Enregistrer l'acheteur ou le vendeur selon le choix
                if type_personne == 'acheteur':
                    Acheteur.objects.create(**donnees)
                    messages.success(request, "L'acheteur a été ajouté avec succès.")
                    return redirect('ajouter_personne')
                elif type_personne == 'vendeur':
                    Vendeur.objects.create(**donnees)
                    messages.success(request, "Le vendeur a été ajouté avec succès.")
                    return redirect('ajouter_personne')

            except Exception as e:
                messages.error(request, f"Une erreur est survenue : {e}")
                return render(request, 'MonAppli_Immo/ajouter_personne.html', {'form': form})

    else:
        form = AcheteurVendeurForm()

    return render(request, 'MonAppli_Immo/ajouter_personne.html', {'form': form})



"""
### Requêtes pour les vendeurs
"""

#1.**Attributs d'un vendeur (nom, prénom,email,telephone...) déterminé par son nom/prénom**
def search_vendeur(request):
    query = request.GET.get('q', '').strip()
    if query:
        vendeurs = Vendeur.objects.filter(
            Q(nom__iexact=query) | Q(prenom__iexact=query)
        )
    else:
        vendeurs = Vendeur.objects.all()
        
    return render(request, 'MonAppli_Immo/search_vendeur.html', {
        'vendeurs': vendeurs,
        'query': query,
    })


#2.**Afficher les biens d'un vendeur **
def afficher_biens_vendeur(request, vendeur_id):
    vendeur = get_object_or_404(Vendeur, id=vendeur_id)
    biens = BienImmobilier.objects.filter(portefeuille_vendeurs__vendeur=vendeur)

    return render(request, 'MonAppli_Immo/afficher_biens_vendeur.html', {
        'vendeur': vendeur,
        'biens': biens,
    })

    
"""
#3.**Ajouter un bien à un vendeur (code SQL)**
def ajouter_bien_vendeur(request, vendeur_id):
    vendeur = get_object_or_404(Vendeur, id=vendeur_id)
    
    if request.method == 'POST':
        form = BienImmobilierForm(request.POST)
        if form.is_valid():
            bien = form.save(commit=False)
            bien.save()
            PortefeuilleVendeur.objects.create(vendeur=vendeur, bien=bien)
            messages.success(request, "Le bien a été ajouté avec succès.")
            return redirect('afficher_biens_vendeur', vendeur_id=vendeur.id)
    else:
        form = BienImmobilierForm()

    return render(request, 'MonAppli_Immo/ajouter_bien_vendeur.html', {
        'form': form,
        'vendeur': vendeur,
    })

"""
#4.**Afficher les etats des biens d'un vendeur **
def etat_biens_par_vendeur(request, vendeur_id):
    vendeur = get_object_or_404(Vendeur, id=vendeur_id)

    suivis = (
        SuiviBienVendeur.objects
        .filter(pv__vendeur=vendeur)
        .select_related('pv__bien', 'pv__vendeur', 'pv__agent')
        .order_by('pv__bien_id', '-date_suivi')
    )

    etats_biens = {}
    agent_id = None

    for suivi in suivis:
        bien_id = suivi.pv.bien.id
        if bien_id not in etats_biens:
            etats_biens[bien_id] = {
                'bien': suivi.pv.bien,
                'etat': suivi.etat_bien,
                'date': suivi.date_suivi,
                'agent': suivi.pv.agent,
                'commentaire': suivi.commentaire,
                'canal': suivi.get_canal_display(),
            }
            if not agent_id:
                agent_id = suivi.pv.agent.id  # On récupère l'agent associé

    return render(request, 'MonAppli_Immo/etat_biens_par_vendeur.html', {
        'vendeur': vendeur,
        'etats_biens': etats_biens.values(),
        'agent_id': agent_id,
    })


#5.**Afficher les rdv avec le vendeur **
def liste_rdv_vendeurs(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT s.date_suivi, s.etat_bien, s.commentaire, v.nom, v.prenom
            FROM public."MonAppli_Immo_suivibienvendeur" s
            JOIN public."MonAppli_Immo_portefeuillevendeur" p 
                ON s.pv_id = p.id
            JOIN public."MonAppli_Immo_vendeur" v 
                ON p.vendeur_id = v.id
            WHERE s.canal = 'rdv'
            ORDER BY s.date_suivi DESC;
        """)
        resultats = cursor.fetchall()

    rendezvous = [
        {
            'date': row[0],
            'etat': row[1],
            'commentaire': row[2],
            'nom': row[3],
            'prenom': row[4],
        }
        for row in resultats
    ]

    return render(request, 'MonAppli_Immo/liste_rdv_vendeurs.html', {
        'rendezvous': rendezvous
    })



"""
### Requêtes pour les acheteurs
"""
#1.**Attributs d'un acheteur (nom, prénom,email,telephone...) déterminé par son nom/prénom**
def search_acheteur(request):
    query = request.GET.get('q', '').strip()
    acheteurs = Acheteur.objects.all()

    if query:
        acheteurs = acheteurs.filter( Q(nom__iexact=query) | Q(prenom__iexact=query))

        if acheteurs.count() == 1:
            # Redirige directement vers la page des biens si un seul résultat
            return redirect('correspondances_biens', acheteur_id=acheteurs.first().id)

    return render(request, 'MonAppli_Immo/search_acheteur.html', {
        'query': query,
        'acheteurs': acheteurs
    })
   
#2.**Afficher les criteres d'un acheteur**
def afficher_criteres(request, acheteur_id):
    acheteur = get_object_or_404(Acheteur, id=acheteur_id)
    criteres = Criteres.objects.filter(acheteur=acheteur)
    
    return render(request, 'MonAppli_Immo/afficher_criteres.html', {
        'acheteur': acheteur,
        'criteres': criteres,
    })

#3.** Creer ou modifier les criteres Acheteurs **
def creer_ou_modifier_criteres(request, acheteur_id):
    acheteur = get_object_or_404(Acheteur, pk=acheteur_id)
    
    # On récupère les critères liés à l'acheteur s'ils existent
    criteres, created = Criteres.objects.get_or_create(acheteur=acheteur)

    if request.method == 'POST':
        form = CriteresForm(request.POST, instance=criteres)
        if form.is_valid():
            crit = form.save(commit=False)
            crit.acheteur = acheteur  # Assure que l'acheteur est bien assigné
            crit.save()
            return redirect('afficher_criteres', acheteur_id=acheteur.id)
    else:
        form = CriteresForm(instance=criteres)

    return render(request, 'MonAppli_Immo/criteres_form.html', {
        'form': form,
        'acheteur': acheteur,
    })
    
#4.**Afficher les biens correspondant aux critères d'un acheteur(meme approximatif)**
def correspondances_biens(request, acheteur_id):
    acheteur = get_object_or_404(Acheteur, id=acheteur_id)
    criteres = getattr(acheteur, 'criteres', None)

    biens_correspondants = []
    if criteres:
        tous_les_biens = BienImmobilier.objects.all()
        biens_correspondants = [
            bien for bien in tous_les_biens if criteres.correspondance(bien)
        ]

    return render(request, 'MonAppli_Immo/correspondances_biens.html', {
        'acheteur': acheteur,
        'biens': biens_correspondants,
    })

#5.** Gérer les étapes d’achat **
def etapes_achat_par_acheteur(request, acheteur_id):
    acheteur = get_object_or_404(Acheteur, id=acheteur_id)

    # Récupérer tous les suivis liés à ses biens
    suivis = SuiviBienAcheteur.objects.filter(pa__acheteur=acheteur).select_related('pa', 'pa__bien', 'pa__agent')

    # Trouver l’agent depuis le premier suivi si disponible
    agent_id = suivis.first().pa.agent.id if suivis.exists() else None

    etapes_par_bien = {}
    for suivi in suivis:
        bien = suivi.pa.bien
        agent = suivi.pa.agent
        if bien not in etapes_par_bien:
            etapes_par_bien[bien] = {
                'agent': agent,
                'etapes': []
            }
        etapes_par_bien[bien]['etapes'].append(suivi)

    # Tri des étapes par date
    for bien_info in etapes_par_bien.values():
        bien_info['etapes'] = sorted(bien_info['etapes'], key=lambda s: s.date_suivi)


    return render(request, 'MonAppli_Immo/etapes_achat_par_acheteur.html', {
        'acheteur': acheteur,
        'etapes_par_bien': etapes_par_bien,
        'agent_id': agent_id,
    })



