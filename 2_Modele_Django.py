from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal
from .choices import *

# Create your models here.

# Ce modèle contient les champs created_at et updated_at
# qui sont automatiquement gérés par Django
class TimeStampedModel(models.Model): 
    #Modèle de base avec des champs de date et heure pour le suivi des enregistrements.
    created_at = models.DateTimeField(auto_now_add=True)  # Date de création
    updated_at = models.DateTimeField(auto_now=True)  # Date de mise à jour


    class Meta:
        abstract = True  # Ne crée pas une table pour cette classe


# Modèle pour les agents immobiliers
class Agent(TimeStampedModel):
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    agence = models.CharField(max_length=50, db_index=True) # Ajout de l'index pour l'agence pour améliorer les performances de recherche
    code_postal_agence = models.IntegerField(db_index=True) # Ajout de l'index pour le code postal de l'agence pour améliorer les performances de recherche
    ville_agence = models.CharField(max_length=50, db_index=True) # Ajout de l'index pour la ville de l'agence pour améliorer les performances de recherche
    
    class Meta:
        unique_together = ('nom', 'prenom', 'email') # Empêche les doublons nom-prénom-email
        ordering = ['nom', 'prenom']  # Tri par défaut sur le nom et prénom
    
    def save(self, *args, validate=True, **kwargs):
        # Convertit l'email en minuscule avant de le sauvegarder
        # Cela permet d'éviter les doublons avec des majuscules/minuscules différentes
        self.email = self.email.strip().lower() # Normalisation de l'email
        if validate:
            self.full_clean()  # Valide tous les champs + clean()
        super().save(*args, **kwargs)
        
    def __str__(self):
        # Format pour l'affichage
        # Affiche les informations de l'agent
        return f"{self.nom} {self.prenom}, {self.email}, {self.telephone}, {self.agence}, {self.code_postal_agence}, {self.ville_agence}"
    def __repr__(self):
        # Format pour le debug
        return f"{self.nom} {self.prenom}, {self.email}, {self.telephone}, {self.agence}, {self.code_postal_agence}, {self.ville_agence}"


# Modèle pour les vendeurs
class Vendeur(TimeStampedModel):
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    code_postal = models.IntegerField(blank=True, null=True)
    ville = models.CharField(max_length=50,db_index=True)
    
    class Meta:
        unique_together = ('nom', 'prenom', 'email')
        ordering = ['nom', 'prenom']  
        
    def save(self, *args, validate=True, **kwargs):
        self.email = self.email.strip().lower()
        if validate:
            self.full_clean()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.nom} {self.prenom}, {self.email}, {self.telephone}, {self.code_postal}, {self.ville}"
    def __repr__(self):
        return self.__str__()


# Modèle pour les acheteurs
class Acheteur(TimeStampedModel):
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    code_postal = models.IntegerField(blank=True, null=True)
    ville = models.CharField(max_length=50, db_index=True)
    
    class Meta:
        unique_together = ('nom', 'prenom', 'email')  # Empêche les doublons nom-prénom-email
        ordering = ['nom', 'prenom']  # Tri par défaut sur le nom et prénom
    
    def save(self, *args, validate=True, **kwargs):
        self.email = self.email.strip().lower()
        if validate:
            self.full_clean()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.nom} {self.prenom}, {self.email}, {self.telephone}, {self.code_postal}, {self.ville}"
    def __repr__(self):
         return self.__str__()
 
    
    
# Modèle pour les biens immobiliers
class BienImmobilier(TimeStampedModel):
    type_bien = models.CharField(max_length=50,choices=TYPES_BIEN, db_index=True) 
    categorie = models.CharField(max_length=30, choices=CATEGORIES, db_index=True) 
    numero_voie = models.CharField(max_length=40, db_index=True)
    type_voie = models.CharField(max_length=10, choices=TYPE_VOIE, db_index=True)
    nom_voie = models.CharField(max_length=50)
    code_postal = models.IntegerField(db_index=True) 
    ville = models.CharField(max_length=50, db_index=True) 
    nb_pieces = models.IntegerField(db_index=True) 
    superficie = models.IntegerField()
    parking = models.BooleanField(default=False, db_index=True) 
    balcon = models.BooleanField(default=False, db_index=True)
    ascenseur = models.BooleanField(default=False, db_index=True)
    jardin = models.BooleanField(default=False, db_index=True)
    piscine = models.BooleanField(default=False, db_index=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2, db_index=True) # Ajout de l'index pour le prix pour améliorer les performances de recherche
    date_disponibilite = models.DateField()
    descriptions = models.TextField(blank=True, null=True)
    statut = models.CharField(max_length=20, choices=STATUTS_BIEN, default='disponible')
    url_wikipedia = models.URLField(blank=True, null=True, max_length=200) # URL vers la page Wikipedia du bien
    
    class Meta: 
        # Index composite pour la recherche
        indexes = [ 
            models.Index(fields=['type_bien','categorie', 'nb_pieces', 'superficie','ville', 'code_postal', 'prix']),    
        ]
        ordering = ['date_disponibilite']  # Tri par défaut sur la date de disponibilité
 
    
    # Propriété pour obtenir le titre de l'annonce et l'adresse
    @property 
    def titre_annonce(self):
        return f"{self.type_bien.title()} - Bien {self.statut.title()} "
    @property
    def adresse_annonce(self):
        return f"{self.numero_voie} {self.type_voie} {self.nom_voie}, {self.code_postal} {self.ville}"

    def clean(self): 
        # Vérifie que le prix et la superficie sont positifs
        # Utilisé pour lever une exception si les conditions ne sont pas remplies
        if self.prix <= 0:
            raise ValidationError("Le prix doit être supérieur à 0.")
        if self.superficie <= 0:
            raise ValidationError("La superficie doit être supérieure à 0.")
        if self.nb_pieces < 0:
            raise ValidationError("Le nombre de pièces ne peut pas être négatif.")


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
            f"Prix : {self.prix} € \n"
            f"Options : {options}"
        )

    def __repr__(self):
        return (
            f"<BienImmobilier(type='{self.type_bien}', ville='{self.ville}', surface={self.superficie}m², "
            f"pièces={self.nb_pieces}, prix={self.prix}€, balcon={self.balcon}, jardin={self.jardin}, "
            f"piscine={self.piscine}, ascenseur={self.ascenseur}, parking={self.parking})>"
        )


# Modèle de liaison entre agents et vendeurs
class PortefeuilleVendeur(TimeStampedModel):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, db_index=True,related_name='portefeuille_vendeurs')
    vendeur = models.ForeignKey(Vendeur, on_delete=models.CASCADE, db_index=True, related_name='portefeuille_vendeurs')
    bien = models.OneToOneField(BienImmobilier, on_delete=models.CASCADE, db_index=True, related_name='portefeuille_vendeurs', unique=True ) # Un vendeur peut avoir plusieurs biens, mais un bien ne peut être lié qu'à un seul vendeur

    def __str__(self):
        return (f"Agent : {self.agent.nom} {self.agent.prenom} - "
                f"Vendeur : {self.vendeur.nom} {self.vendeur.prenom} - "
                f"Bien : {self.bien.type_bien} à {self.bien.ville}")

    def __repr__(self):
        return (
            f"<PortefeuilleVendeur(agent_id={self.agent_id}, "
            f"vendeur_id={self.vendeur_id}, bien_id={self.bien_id})>"
        )


# Modèle de liaison entre agents et acheteurs
class PortefeuilleAcheteur(TimeStampedModel):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, db_index=True, related_name='portefeuille_acheteurs')
    acheteur = models.ForeignKey(Acheteur, on_delete=models.CASCADE, db_index=True, related_name='portefeuille_acheteurs')
    bien = models.ForeignKey(BienImmobilier, on_delete=models.CASCADE, db_index=True, related_name='portefeuille_acheteurs')
    
    class Meta:
        unique_together = ('agent','acheteur','bien') # Un agent ne peut pas avoir deux fois le même acheteur pour le même bien
        
    def __str__(self):
        return (f"Agent : {self.agent.nom} {self.agent.prenom} - "
                f"Acheteur : {self.acheteur.nom} {self.acheteur.prenom} - "
                f"Bien : {self.bien.type_bien} à {self.bien.ville}")
   
    def __repr__(self):
        return (
            f"<PortefeuilleAcheteur(agent_id={self.agent_id}, "
            f"acheteur_id={self.acheteur_id}, bien_id={self.bien_id})>"
        )


# Modèle pour les suivis biens- vendeurs
class SuiviBienVendeur(TimeStampedModel):  
    pv = models.ForeignKey(PortefeuilleVendeur, on_delete=models.CASCADE, related_name='suivi_bien_vendeurs')
    canal = models.CharField(max_length=20, choices=CANAL_VENDEURS)
    etat_bien = models.CharField(max_length=50, choices=ETAT_VENDEURS)
    date_suivi = models.DateField(db_index=True)
    commentaire = models.TextField(blank=True, null=True)

    def __str__(self):
        return (
            f"Suivi via {self.get_canal_display()} - {self.pv} "
            f"le {self.date_suivi.strftime('%d/%m/%Y')}\n"
            f"État : {self.get_etat_bien_display()} | Commentaire : {self.commentaire or 'Aucun'}"
        )

    def __repr__(self):
        return (
            f"<SuiviBienVendeur(canal='{self.canal}', "
            f"etat_bien='{self.etat_bien}', date='{self.date_suivi}', "
            f"pv_id={self.pv_id})>"
        )


# Modèle pour les suivi-acheteurs
class SuiviBienAcheteur(TimeStampedModel):   
    pa = models.ForeignKey(PortefeuilleAcheteur, on_delete=models.CASCADE, related_name='suivi_bien_acheteurs')
    canal = models.CharField(max_length=20, choices=CANAL_ACHETEURS)
    etat_bien = models.CharField(max_length=30, choices=ETAT_ACHETEURS)
    date_suivi = models.DateField(db_index=True)
    feedback = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return (
            f"Suivi via {self.get_canal_display()} - {self.pa} "
            f"le {self.date_suivi.strftime('%d/%m/%Y')}\n"
            f"État : {self.get_etat_bien_display()} | Feedback : {self.feedback or 'Aucun'}"
        )

    def __repr__(self):
        return (
            f"<SuiviBienAcheteur(canal='{self.canal}', etat_bien='{self.etat_bien}', "
            f"date_suivi='{self.date_suivi}', pa_id={self.pa_id}, "
            f"feedback='{self.feedback}')>"
        )



# Modèle pour les critères de recherche d'un acheteur
class Criteres(TimeStampedModel):
    acheteur = models.OneToOneField('Acheteur', on_delete=models.CASCADE, related_name='criteres')
    type_bien = models.CharField(default='Appartement', max_length=50,choices=TYPES_BIEN, db_index=True) 
    categorie = models.CharField(default='Location',max_length=30, choices=CATEGORIES, db_index=True) 
    nb_pieces_min = models.IntegerField(blank=True, null=True)
    nb_pieces_max = models.IntegerField(blank=True, null=True)
    superficie_min = models.IntegerField(blank=True, null=True)
    superficie_max = models.IntegerField(blank=True, null=True)
    budget_max = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    parking = models.BooleanField(default=False,blank=True, null=True )
    balcon = models.BooleanField(default=False, blank=True, null=True)
    ascenseur = models.BooleanField(default=False, blank=True, null=True)
    jardin = models.BooleanField(default=False, blank=True, null=True)
    piscine = models.BooleanField(default=False, blank=True, null=True)
    code_postal = models.IntegerField(db_index=True, blank=True, null=True) # Ajout de l'index pour le code postal pour améliorer les performances de recherche
    ville = models.CharField(max_length=50, db_index=True, blank=True, null=True) # Ajout de l'index pour la ville pour améliorer les performances de recherche
    date_emmenagement = models.DateField(blank=True, null=True)


    def clean(self):
        # Vérifier les pièces
        if self.nb_pieces_min is not None and self.nb_pieces_max is not None:
            if self.nb_pieces_min > self.nb_pieces_max:
                raise ValidationError("Le nombre de pièces minimum ne peut pas être supérieur au maximum.")

        # Vérifier les superficies
        if self.superficie_min is not None and self.superficie_max is not None:
            if self.superficie_min > self.superficie_max:
                raise ValidationError("La superficie minimum ne peut pas être supérieure au maximum.")


    def correspondance(self, bien):
        print(f"Comparaison du type : {self.type_bien} vs {bien.type_bien}")  # DEBUG
        
        # Exclusion immédiate si le bien n'est pas disponible
        if getattr(bien, 'statut', '').strip().lower() != 'disponible':
            return False
        
        # Exclusion immédiate si le type de bien ne correspond pas
        if self.type_bien and self.type_bien.strip().lower() != getattr(bien, 'type_bien', '').strip().lower():
            return False
        
        # Vérification souple : on ne rejette pas immédiatement si un champ n'est pas rempli
        score = 0
        total = 0

        # Pièces
        if self.nb_pieces_min is not None:
            total += 1
            if bien.nb_pieces >= self.nb_pieces_min:
                score += 1
        if self.nb_pieces_max is not None:
            total += 1
            if bien.nb_pieces <= self.nb_pieces_max:
                score += 1

        # Superficie
        if self.superficie_min is not None:
            total += 1
            if bien.superficie >= self.superficie_min:
                score += 1
        if self.superficie_max is not None:
            total += 1
            if bien.superficie <= self.superficie_max:
                score += 1

        # Budget
        if self.budget_max is not None:
            total += 1
            if bien.prix <= self.budget_max:
                score += 1

        # Ville (tolérante sur code postal ou ville)
        if self.ville:
            total += 1
            if self.ville.lower() in bien.ville.lower():
                score += 1
        elif self.code_postal:
            total += 1
            if str(bien.code_postal).startswith(str(self.code_postal)[0:2]):
                score += 1

        
        # Catégorie
        if self.categorie:
            total += 1
            if self.categorie.lower() in getattr(bien, 'categorie', '').lower():
                score += 1
        
        # Options (optionnelles : on les compte seulement si demandées)
        for option in ['parking', 'balcon', 'ascenseur', 'jardin', 'piscine']:
            val = getattr(self, option)
            if val:  # Si le critère exige cette option
                total += 1
                if getattr(bien, option, False):
                    score += 1

        # Score final : au moins 70% des critères doivent correspondre
        return total == 0 or (score / total) >= 0.5


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

#--Fin des modèles--#
