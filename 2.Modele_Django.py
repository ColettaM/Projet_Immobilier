from django.db import models
from .choices import *

# Create your models here.

# Modèle pour les agents immobiliers
class Agent(models.Model):
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        unique_together = ('nom', 'prenom', 'email') # Empêche les doublons nom-prénom-email
        ordering = ['nom', 'prenom']  # Tri par défaut sur le nom et prénom
    
    def save(self, *args, validate=True, **kwargs):
        # Convertit l'email en minuscule avant de le sauvegarder
        # Cela permet d'éviter les doublons avec des majuscules/minuscules différentes
        self.email = self.email.lower()  # Normalisation 
        if validate:
            self.full_clean()  # Valide tous les champs + clean()
        super().save(*args, **kwargs)
        
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
        unique_together = ('nom', 'prenom', 'email')
        ordering = ['nom', 'prenom']  
        
    def save(self, *args, validate=True, **kwargs):
        self.email = self.email.lower()
        if validate:
            self.full_clean()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.nom} {self.prenom}, {self.email}, {self.telephone}"
    def __repr__(self):
        return self.__str__()
    
    
# Modèle pour les biens immobiliers
class BienImmobilier(models.Model):
    type_bien = models.CharField(max_length=50, db_index=True) # Ajout de l'index pour le type de bien pour améliorer les performances de recherche
    categorie = models.CharField(max_length=20, choices=CATEGORIES)
    numero_voie = models.CharField(max_length=5)
    type_voie = models.CharField(max_length=10, choices=TYPES)
    nom_voie = models.CharField(max_length=50)
    code_postal = models.IntegerField(db_index=True) # Ajout de l'index pour le code postal pour améliorer les performances de recherche
    ville = models.CharField(max_length=20, db_index=True) # Ajout de l'index pour la ville pour améliorer les performances de recherche
    commune = models.CharField(max_length=50, db_index=True) # Ajout de l'index pour la commune pour améliorer les performances de recherche
    nb_pieces = models.IntegerField(db_index=True) # Ajout de l'index pour le nombre de pièces pour améliorer les performances de recherche
    superficie = models.IntegerField()
    parking = models.BooleanField(default=False)
    balcon = models.BooleanField(default=False)
    ascenseur = models.BooleanField(default=False)
    jardin = models.BooleanField(default=False)
    piscine = models.BooleanField(default=False)
    prix = models.DecimalField(max_digits=13, decimal_places=2)
    date_disponibilite = models.DateField()
    descriptions = models.TextField(blank=True, null=True)
    etat = models.CharField(max_length=30, choices=ETATS)
    image_url = models.URLField(blank=True, null=True)

    def clean(self): 
        # Vérifie que le prix et la superficie sont positifs
        # Utilisé pour lever une exception si les conditions ne sont pas remplies
        from django.core.exceptions import ValidationError
        if self.prix <= 0:
            raise ValidationError("Le prix doit être supérieur à 0.")
        if self.superficie <= 0:
            raise ValidationError("La superficie doit être supérieure à 0.")

    def __str__(self):
        # Format pour l'affichage
        options = ', '.join([
            opt for opt, val in {
                'parking': self.parking,
                'balcon': self.balcon,
                'ascenseur': self.ascenseur,
                'jardin': self.jardin,
                'piscine': self.piscine
            }.items() if val
        ]) or "Aucune option"

        return (
            f"{self.type_bien.title()} en {self.categorie.title()} à {self.ville.title()} - "
            f"{self.nb_pieces} pièce(s), {self.superficie} m²\n"
            f"Adresse : {self.numero_voie} {self.type_voie} {self.nom_voie}, {self.code_postal} {self.ville}\n"
            f"Disponible : {self.date_disponibilite.strftime('%d/%m/%Y')} | "
            f"Prix : {self.prix} € | État : {self.etat.title()}\n"
            f"Options : {options}"
        )

    def __repr__(self):
        return (
            f"<BienImmobilier(type='{self.type_bien}', ville='{self.ville}', surface={self.superficie}m², "
            f"pièces={self.nb_pieces}, prix={self.prix}€, balcon={self.balcon}, jardin={self.jardin}, "
            f"piscine={self.piscine}, ascenseur={self.ascenseur}, parking={self.parking})>"
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
    portefeuille_vendeur = models.ForeignKey(PortefeuilleVendeur, on_delete=models.CASCADE)
    object_rdv = models.CharField(max_length=30, choices=OBJECTIFS_VENDEUR)
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
        unique_together = ('nom', 'prenom', 'email')  # Empêche les doublons nom-prénom-email
        ordering = ['nom', 'prenom']  # Tri par défaut sur le nom et prénom
    
    def save(self, *args, validate=True, **kwargs):
        self.email = self.email.lower()
        if validate:
            self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nom} {self.prenom}, {self.email}, {self.telephone}"
    def __repr__(self):
         return self.__str__()


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
    acheteur = models.OneToOneField('Acheteur', on_delete=models.CASCADE)
    nb_pieces_min = models.IntegerField()
    nb_pieces_max = models.IntegerField(blank=True, null=True)
    superficie_min = models.IntegerField()
    superficie_max = models.IntegerField(blank=True, null=True)
    budget_max = models.DecimalField(max_digits=13, decimal_places=2)
    parking = models.BooleanField(default=False)
    balcon = models.BooleanField(default=False)
    ascenseur = models.BooleanField(default=False)
    jardin = models.BooleanField(default=False)
    piscine = models.BooleanField(default=False)
    code_postal = models.IntegerField(db_index=True) # Ajout de l'index pour le code postal pour améliorer les performances de recherche
    ville = models.CharField(max_length=20, db_index=True) # Ajout de l'index pour la ville pour améliorer les performances de recherche
    commune = models.CharField(max_length=50, db_index=True) # Ajout de l'index pour la commune pour améliorer les performances de recherche
    date_emmenagement = models.DateField()

    def correspondance(self, bien):
        # Vérifie si le bien correspond aux critères de l'acheteur
        return (
            self.nb_pieces_min <= bien.nb_pieces and
            (self.nb_pieces_max is None or bien.nb_pieces <= self.nb_pieces_max) and
            self.superficie_min <= bien.superficie and
            (self.superficie_max is None or bien.superficie <= self.superficie_max) and
            bien.code_postal == self.code_postal and
            bien.ville.lower() == self.ville.lower() and
            (not self.balcon or bien.balcon) and
            (not self.jardin or bien.jardin) and
            (not self.ascenseur or bien.ascenseur) and
            (not self.piscine or bien.piscine) and
            (not self.parking or bien.parking) and
            bien.prix <= self.budget_max
        )

    def __str__(self):
        return (
            f"Critères de {self.acheteur.nom} {self.acheteur.prenom} : "
            f"{self.nb_pieces_min}-{self.nb_pieces_max or '?'} pièces, "
            f"{self.superficie_min}-{self.superficie_max or '?'} m², "
            f"max {self.budget_max} €, à {self.ville} ({self.code_postal})"
        )

    def __repr__(self):
        return (
            f"<Criteres(acheteur_id={self.acheteur_id}, pièces=[{self.nb_pieces_min}-{self.nb_pieces_max}], "
            f"surface=[{self.superficie_min}-{self.superficie_max}], budget={self.budget_max}, "
            f"ville={self.ville}, options=[balcon={self.balcon}, jardin={self.jardin}, "
            f"ascenseur={self.ascenseur}, piscine={self.piscine}, parking={self.parking}])>"
        )


# Modèle pour les rendez-vous avec les acheteurs
class RdvAcheteur(models.Model):   
    portefeuille_acheteur = models.ForeignKey(PortefeuilleAcheteur, on_delete=models.CASCADE)
    object_rdv = models.CharField(max_length=30, choices=OBJECTIFS_ACHETEUR)
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
    portefeuille_acheteur = models.ForeignKey(PortefeuilleAcheteur, on_delete=models.CASCADE)
    etape = models.CharField(max_length=30, choices=ETAPES_ACHAT)
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
       
         
         