# immobilier/choices.py

CATEGORIES = [
        ('vente', 'Vente'),
        ('location', 'Location'),
        ('colocation', 'Colocation'),
        ('bureaux et commerce', 'Bureaux et Commerce'),
    ]
TYPES = [ 
        ('rue', 'Rue'),
        ('avenue', 'Avenue'),
        ('boulevard', 'Boulevard'),
        ('chemin', 'Chemin'),
        ('impasse', 'Impasse'),
        ('place', 'Place'),
        ('route', 'Route'),
        ('allée', 'Allée'),
        ('quai', 'Quai'),
        ('cours', 'Cours'),
        ('esplanade', 'Esplanade'),
        ('promenade', 'Promenade'),
        ('passage', 'Passage'),
        ('voie', 'Voie'),
    ]
ETATS = [
        ('prospection', 'Prospection'),
        ('estimation', 'Estimation'),
        ('mise en vente', 'Mise en vente'),
        ('compromis signé', 'Compromis signé'),
        ('signature de la vente', 'Signature de la vente'),
    ]
  
  
OBJECTIFS_ACHETEUR = [
        ('consultation', 'Consultation'),
        ('visite', 'Visite'),
        ('negociation', 'Négociation'),
    ]
FEEDBACK_CHOICES = [
        ('intéressé', 'Intéressé'),
        ('pas intéressé', 'Pas intéressé'),
        ('en attente', 'En attente'),
        ('marché conclu', 'Marché conclu'),
    ] 

OBJECTIFS_VENDEUR = [
    ('visite', 'Visite'),
    ('évaluation', 'Évaluation'),
    ('discussion', 'Discussion'),
]

ETAPES_ACHAT = [
    ('offre faite', 'Offre faite'),
    ('négociation', 'Négociation'),
    ('compromis signé', 'Compromis signé'),
    ('vente finalisée', 'Vente finalisée'),
]
