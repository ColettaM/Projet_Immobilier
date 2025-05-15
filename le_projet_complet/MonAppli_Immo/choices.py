# MonAppli_Immo/choices.py

TYPES_BIEN = [
        ('maison', 'Maison'),
        ('appartement', 'Appartement'),
        ('bureau', 'Bureau'),
        ('local commercial', 'Local Commercial'),
]

CATEGORIES = [
        ('vente', 'Vente'),
        ('location', 'Location'),
]

TYPE_VOIE = [
        ('rue', 'Rue'),
        ('avenue', 'Avenue'),
        ('boulevard', 'Boulevard'),
        ('chemin', 'Chemin'),
        ('impasse', 'Impasse'),
        ('place', 'Place'),
        ('allée', 'Allée'),
        ('quai', 'Quai'),
        ('route', 'Route'),
        ('cours', 'Cours'),
        ('esplanade', 'Esplanade'),
        ('promenade', 'Promenade'),
        ('parc', 'Parc'),
        ('voie', 'Voie'),
]
        

STATUTS_BIEN = [
    ('disponible', 'Disponible'),
    ('sous_offre', 'Sous Offre'),
    ('vendu', 'Vendu'),
    ('loué', 'Loué'),
    ('retiré', 'Retiré'),
]

CANAL_VENDEURS= [
        ('rdv', 'Rendez-vous'),
        ('email', 'Email'),
        ('appel', 'Appel'),
        ('sms', 'SMS'),
        ('autre', 'Autre'),
]

ETAT_VENDEURS= [
        ('prospection', 'Prospection'),
        ('estimation', 'Estimation'),
        ('signature du compromis', 'Signature du compromis'),
        ('négociation', 'Négociation'),
        ('mise en vente', 'Mise en vente'),
        ('annulation', 'Annulation'),
        ('signature de la vente', 'Signature de la vente'),
]

CANAL_ACHETEURS = [
        ('rdv', 'Rendez-vous'),
        ('email', 'Email'),
        ('appel', 'Appel'),
        ('sms', 'SMS'),
        ('autre', 'Autre'),
]

ETAT_ACHETEURS = [
        ('communiqué', 'Communiqué'),
        ('visité', 'Visité'),
        ('refusé', 'Refusé'),
        ('offre faite', 'Offre faite'),
        ('offre acceptée', 'Offre acceptée'),
        ('signature du compromis', 'Signature du compromis'),
        ('négocié', 'Négocié'),
        ('annulé', 'Annulé'),
        ('acte final signé', 'Acte final signé'),
]