from django.db import models

# Create your models here.

# Modèle pour les agents immobiliers
class Agent(models.Model):
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        unique_together = ('nom', 'prenom')  # Empêche les doublons nom-prénom

    def __str__(self):
        # Format pour l'affichage
        # Affiche le nom, prénom, email et téléphone de l'agent
        return f"{self.nom} {self.prenom}, {self.email}, {self.telephone}"
    def __repr__(self):
        # Format pour le debug
        return f"{self.nom} {self.prenom}, {self.email}, {self.telephone}"


# Modèle pour les vendeurs
class Vendeur(models.Model):
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    
    class Meta:
        unique_together = ('nom', 'prenom')
    
    def __str__(self):
        return f"{self.nom} {self.prenom}, {self.email}, {self.telephone}"
    def __repr__(self):
        return f"{self.nom} {self.prenom}, {self.email}, {self.telephone}"

# Modèle pour les biens immobiliers
class BienImmobilier(models.Model):
    CATEGORIES = [
        ('vente', 'Vente'),
        ('location', 'Location'),
        ('colocation', 'Colocation'),
        ('bureaux et commerce', 'Bureaux et Commerce'),
    ]
    ETATS = [
        ('prospection', 'Prospection'),
        ('estimation', 'Estimation'),
        ('mise en vente', 'Mise en vente'),
        ('compromis signé', 'Compromis signé'),
        ('signature de la vente', 'Signature de la vente'),
    ]
    
    type_bien = models.CharField(max_length=50)
    categorie = models.CharField(max_length=20, choices=CATEGORIES)
    nb_pieces = models.IntegerField()
    superficie = models.IntegerField()
    adresse = models.TextField()
    ville = models.CharField(max_length=20)
    date_disponibilite = models.DateField()
    prix = models.DecimalField(max_digits=13, decimal_places=2)
    descriptions = models.TextField(blank=True, null=True)
    etat = models.CharField(max_length=30, choices=ETATS)
    image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        # Format pour l'affichage
        # Affiche le type de bien, la catégorie, la ville, le nombre de pièces, la superficie,
        # l'adresse, la date de disponibilité, le prix, l'état et l'URL de l'image
        # ou "Aucune image" si l'URL est vide
        # ou "Aucune description" si la description est vide 
        return (
            f"{self.type_bien.title()} en {self.categorie.title()} à {self.ville.title()} - "
            f"{self.nb_pieces} pièce(s), {self.superficie} m²\n"
            f"Adresse : {self.adresse}\n"
            f"Disponible à partir du {self.date_disponibilite.strftime('%d/%m/%Y')}\n"
            f"Prix : {self.prix} €\n"
            f"État : {self.etat.title()}\n"
            f"Image : {self.image_url or 'Aucune image'}\n"
            f"Description : {self.descriptions or 'Aucune description'}"
        )
    def __repr__(self):
        return (
            f"<BienImmobilier(type='{self.type_bien}', ville='{self.ville}', "
            f"catégorie='{self.categorie}', surface={self.superficie}m², "
            f"pièces={self.nb_pieces}, prix={self.prix}€, état='{self.etat}')>"
        )


# Modèle de liaison entre agents et vendeurs
class PortefeuilleVendeur(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    vendeur = models.ForeignKey(Vendeur, on_delete=models.CASCADE)
    bien = models.ForeignKey(BienImmobilier, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('agent', 'vendeur', 'bien')  # Unicité de la relation

    def __str__(self):
        return (f"Agent : {self.agent.nom} {self.agent.prenom} - "
                f"Vendeur : {self.vendeur.nom} {self.vendeur.prenom} - "
                f"Bien : {self.bien.type_bien} à {self.bien.ville}")

    def __repr__(self):
        return (
            f"<PortefeuilleVendeur(agent_id={self.agent_id}, "
            f"vendeur_id={self.vendeur_id}, bien_id={self.bien_id})>"
        )

# Modèle pour les rendez-vous des vendeurs
class RdvVendeur(models.Model):
    OBJECTIFS = [
        ('visite', 'Visite'),
        ('évaluation', 'Évaluation'),
        ('discussion', 'Discussion'),
    ]
    
    portefeuille_vendeur = models.ForeignKey(PortefeuilleVendeur, on_delete=models.CASCADE)
    object_rdv = models.CharField(max_length=30, choices=OBJECTIFS)
    date_rdv = models.DateField()
    commentaire = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return (
            f"Rdv {self.get_object_rdv_display()} - {self.portefeuille_vendeur} "
            f"le {self.date_rdv.strftime('%d/%m/%Y')}\n"
            f"Commentaire : {self.commentaire or 'Aucun commentaire'}"
        )

    def __repr__(self):
        return (
            f"<RdvVendeur(objectif='{self.object_rdv}', "
            f"date='{self.date_rdv}', portefeuille_vendeur_id={self.portefeuille_vendeur_id})>"
        )



# Modèle pour les acheteurs
class Acheteur(models.Model):
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    
    class Meta:
        unique_together = ('nom', 'prenom')
    
    def __str__(self):
        return f"{self.nom} {self.prenom}, {self.email}, {self.telephone}"
    def __repr__(self):
        return f"{self.nom} {self.prenom}, {self.email}, {self.telephone}" 

# Modèle de liaison entre agents et acheteurs
class PortefeuilleAcheteur(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    acheteur = models.ForeignKey(Acheteur, on_delete=models.CASCADE)
    bien = models.ForeignKey(BienImmobilier, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('agent', 'acheteur', 'bien')
        
    def __str__(self):
        return (f"Agent : {self.agent.nom} {self.agent.prenom} - "
                f"Acheteur : {self.acheteur.nom} {self.acheteur.prenom} - "
                f"Bien : {self.bien.type_bien} à {self.bien.ville}")
    def __repr__(self):
        return (
            f"<PortefeuilleAcheteur(agent_id={self.agent_id}, "
            f"acheteur_id={self.acheteur_id}, bien_id={self.bien_id})>"
        )


# Modèle pour les critères de recherche d'un acheteur
class Criteres(models.Model):
    acheteur = models.OneToOneField(Acheteur, on_delete=models.CASCADE)
    nb_pieces_min = models.IntegerField()
    nb_pieces_max = models.IntegerField(blank=True, null=True)
    superficie_min = models.IntegerField()
    superficie_max = models.IntegerField(blank=True, null=True)
    budget_max = models.DecimalField(max_digits=13, decimal_places=2)
    garage = models.BooleanField(default=False)
    balcon = models.BooleanField(default=False)
    ascenseur = models.BooleanField(default=False)
    jardin = models.BooleanField(default=False)
    ville = models.CharField(max_length=20)
    date_emmenagement = models.DateField()
    
    def correspondance(self, bien):
    # Ex : retourner True si le bien correspond aux critères
        return (
            self.nb_pieces_min <= bien.nb_pieces and
            (self.nb_pieces_max is None or bien.nb_pieces <= self.nb_pieces_max) and
            self.superficie_min <= bien.superficie and
            (self.superficie_max is None or bien.superficie <= self.superficie_max) and
            bien.ville.lower() == self.ville.lower()
        )
        
    def __str__(self):
        return (f"Critères de recherche pour {self.acheteur.nom} {self.acheteur.prenom} : "
                f"{self.nb_pieces_min}-{self.nb_pieces_max} pièces, "
                f"{self.superficie_min}-{self.superficie_max} m², "
                f"Budget max : {self.budget_max} €, "
                f"Ville : {self.ville}")

    def __repr__(self):
        return (
            f"<Criteres(acheteur_id={self.acheteur_id}, "
            f"nb_pieces_min={self.nb_pieces_min}, superficie_min={self.superficie_min}, "
            f"budget_max={self.budget_max})>"
        )


# Modèle pour les rendez-vous avec les acheteurs
class RdvAcheteur(models.Model):
    OBJECTIFS = [
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
    
    portefeuille_acheteur = models.ForeignKey(PortefeuilleAcheteur, on_delete=models.CASCADE)
    object_rdv = models.CharField(max_length=30, choices=OBJECTIFS)
    date_rdv = models.DateField()
    feedback = models.CharField(max_length=30, choices=FEEDBACK_CHOICES, blank=True, null=True)

    def __str__(self):
        return (
            f"Rdv {self.get_object_rdv_display()} - {self.portefeuille_acheteur} "
            f"le {self.date_rdv.strftime('%d/%m/%Y')}\n"
            f"Feedback : {self.get_feedback_display() or 'Aucun feedback'}"
        )

    def __repr__(self):
        return (
            f"<RdvAcheteur(objectif='{self.object_rdv}', "
            f"date='{self.date_rdv}', portefeuille_acheteur_id={self.portefeuille_acheteur_id}, "
            f"feedback='{self.feedback}')>"
        )
    

# Modèle pour suivre les étapes d'un achat immobilier
class EtapesAchat(models.Model):
    ETAPES = [
        ('offre faite', 'Offre faite'),
        ('négociation', 'Négociation'),
        ('compromis signé', 'Compromis signé'),
        ('vente finalisée', 'Vente finalisée'),
    ]
    
    portefeuille_acheteur = models.ForeignKey(PortefeuilleAcheteur, on_delete=models.CASCADE)
    etape = models.CharField(max_length=30, choices=ETAPES)
    date_etape = models.DateField()
    
    def __str__(self):
        return (
            f"Etape : {self.get_etape_display()} - {self.portefeuille_acheteur} "
            f"le {self.date_etape.strftime('%d/%m/%Y')}"
        )
    def __repr__(self):
        return (
            f"<EtapesAchat(portefeuille_acheteur_id={self.portefeuille_acheteur_id}, "
            f"etape='{self.etape}', date_etape='{self.date_etape}')>"
        )
       
         
         