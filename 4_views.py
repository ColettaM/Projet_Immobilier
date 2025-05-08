from django.shortcuts import render, redirect,get_object_or_404
from django.db import connection
from django.contrib import messages  # Ajoute cette importation
from django.db.models import Count, Sum, Q
from django.utils.dateparse import parse_date

from .models import *
from .forms import *

# Create your views here.

def accueil(request):
    return render(request, 'MonAppli_Immo/accueil.html')
 

""" **Requêtes sur les agents et agences :** """

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
def portefeuille_agent(request):
    query = request.GET.get('q', '')
    agents = Agent.objects.filter(Q(nom__icontains=query) | Q(prenom__icontains=query)) if query else []
    
    data = []
    for agent in agents:
        with connection.cursor() as cursor:
            
            # Récupère les vendeurs liés à l’agent
            cursor.execute("""
                SELECT nom, prenom, email, telephone
                FROM public."MonAppli_Immo_vendeur" V
                JOIN public."MonAppli_Immo_portefeuillevendeur" PV
                ON V.id = PV.vendeur_id
                WHERE agent_id = %s
            """, [agent.id])
            vendeurs = cursor.fetchall()
            
            # Récupère les acheteurs liés à l’agent
            cursor.execute("""
                SELECT nom, prenom,email, telephone
                FROM public."MonAppli_Immo_acheteur" A
                JOIN public."MonAppli_Immo_portefeuilleacheteur" PA
                ON A.id = PA.acheteur_id
                WHERE agent_id = %s
            """, [agent.id])
            acheteurs = cursor.fetchall()

            
            #Récupère les biens liés à l'agent
            cursor.execute("""
                SELECT B.*
                FROM public."MonAppli_Immo_bienimmobilier" as B
                JOIN public."MonAppli_Immo_portefeuillevendeur" as PV
                ON B.id = PV.bien_id
                JOIN public."MonAppli_Immo_agent" as A
                ON A.id = PV.agent_id
                WHERE A.id = %s
            """, [agent.id])
            biens = cursor.fetchall()
            
        data.append({
            'agent': agent,
            'vendeurs': vendeurs,
            'acheteurs': acheteurs,
            'biens': biens,
        })

    return render(request, 'MonAppli_Immo/portefeuille_agent.html', {
        'data': data,
        'query': query
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
    
    
""" Acheteur et Vendeur"""
  
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
### **Requêtes pour les vendeurs**
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
  


"""
### **Requêtes pour les acheteurs **
"""

#1.**Attributs d'un acheteur (nom, prénom,email,telephone...) déterminé par son nom/prénom**
def search_acheteur(request):
    query = request.GET.get('q', '').strip()
    if query:
        acheteurs = Acheteur.objects.filter(
            Q(nom__iexact=query) | Q(prenom__iexact=query)
        )
    else:
        acheteurs = Acheteur.objects.all()
        
    return render(request, 'MonAppli_Immo/search_acheteur.html', {
        'acheteurs': acheteurs,
        'query': query,
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
