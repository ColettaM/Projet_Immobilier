from django.shortcuts import render, get_object_or_404
from django.db import connection
from django.db.models import Count, Sum, Q
from django.utils.dateparse import parse_date

from .models import *
from .forms import *

# Create your views here.

def accueil(request):
    return render(request, 'MonAppli_Immo/accueil.html')
 
"""
### **Requêtes sur les agents et agences :**
3. **Afficher les clients (acheteurs/vendeurs) suivis par un agent donné (requete SQL)**
4. **Afficher le chiffre d'affaires par agence / par agent sur une période donnée**
"""

#1.**Attributs d'un agent(nom, prénom,email,telephone,agence) 
# déterminé par son nom/prénom ou par son email**
def search_agent(request):
    query = request.GET.get('q', '')  # On récupère le mot-clé
    if query:
        agents = Agent.objects.filter(
            Q(nom__icontains=query) | Q(prenom__icontains=query) | Q(email__icontains=query)
        )
    else:
        agents = Agent.objects.all()
    return render(request, 'MonAppli_Immo/search_agent.html', {
        'agents': agents,
        'query': query,
    })


#2.**Afficher le portefeuilles Agent**(code SQL)
def portefeuille_agent(request):
    query = request.GET.get('q', '')
    agents = Agent.objects.filter(Q(nom__icontains=query) | Q(prenom__icontains=query)) if query else []
    
    data = []
    for agent in agents:
        with connection.cursor() as cursor:
            # Récupère les acheteurs liés à l’agent
            cursor.execute("""
                SELECT nom, prenom, email, telephone
                FROM public."MonAppli_Immo_acheteur" A
                JOIN public."MonAppli_Immo_portefeuilleacheteur" PA
                ON A.id = PA.acheteur_id
                WHERE agent_id = %s
            """, [agent.id])
            acheteurs = cursor.fetchall()

            # Récupère les vendeurs liés à l’agent
            cursor.execute("""
                SELECT nom, prenom, email, telephone
                FROM public."MonAppli_Immo_vendeur" V
                JOIN public."MonAppli_Immo_portefeuillevendeur" PV
                ON V.id = PV.vendeur_id
                WHERE agent_id = %s
            """, [agent.id])
            vendeurs = cursor.fetchall()
            
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
            'acheteurs': acheteurs,
            'vendeurs': vendeurs,
            'biens': biens,
        })

    return render(request, 'MonAppli_Immo/portefeuille_agent.html', {
        'data': data,
        'query': query
})
