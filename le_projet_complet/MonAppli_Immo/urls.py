from django.urls import path
from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'), 
    path('search-agent/', views.search_agent, name='search_agent'),
    path('ajouter-agent/', views.ajouter_agent, name='ajouter_agent'),
    path('portefeuille-agent/<int:agent_id>/', views.portefeuille_agent, name='portefeuille_agent'),
    path('chiffre-affaires/', views.chiffre_affaires, name='chiffre_affaires'),

    path('ajouter-personne/', views.ajouter_personne, name='ajouter_personne'),

    path('search-acheteur/', views.search_acheteur, name='search_acheteur'),
    path('acheteur/<int:acheteur_id>/criteres/afficher/', views.afficher_criteres, name='afficher_criteres'),
    path('acheteur/<int:acheteur_id>/criteres/modifier/', views.creer_ou_modifier_criteres, name='criteres_form'),
    path('acheteur/<int:acheteur_id>/criteres/biens/', views.correspondances_biens, name='correspondances_biens'),
    path('etapes/achat/<int:acheteur_id>/', views.etapes_achat_par_acheteur, name='etapes_achat_par_acheteur'),

    
    path('search-vendeur/', views.search_vendeur, name='search_vendeur'),
    path('vendeur/<int:vendeur_id>/biens/afficher/', views.afficher_biens_vendeur, name='afficher_biens_vendeur'),
    path('etat-biens-vendeur/<int:vendeur_id>/', views.etat_biens_par_vendeur, name='etat_biens_par_vendeur'),

]
