from django import forms
from .models import *

# forms.py

class FiltreAgenceForm(forms.Form):
    agence = forms.CharField(label="Nom de l'agence", required=False)

class AgentForm(forms.ModelForm):
    class Meta:
        model = Agent
        fields = ['nom', 'prenom', 'email', 'telephone', 'agence', 'code_postal_agence', 'ville_agence']

class AcheteurVendeurForm(forms.Form):
    TYPE_CHOICES = [
        ('acheteur', 'Acheteur'),
        ('vendeur', 'Vendeur'),
    ]

    type_personne = forms.ChoiceField(
        choices=TYPE_CHOICES,
        label="Type de personne",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    nom = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    prenom = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    telephone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    code_postal = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    ville = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))


class ChiffreAffairesForm(forms.Form):
    date_debut = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Date de début")
    date_fin = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Date de fin")


class CriteresForm(forms.ModelForm):
    class Meta:
        model = Criteres
        fields = '__all__'  # ou liste personnalisée des champs
        widgets = {
            'date_emmenagement': forms.DateInput(
                attrs={'type': 'date'},
                format='%d/%m/%Y'  # Format français
            ),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date_emmenagement'].input_formats = ['%d/%m/%Y']


class RechercheBienForm(forms.Form):
    type_bien = forms.ChoiceField(choices=[('', '---------')] + list(Criteres._meta.get_field('type_bien').choices), required=True)
    categorie = forms.ChoiceField(choices=[('', '---------')] + list(Criteres._meta.get_field('categorie').choices), required=False)
    nb_pieces_min = forms.IntegerField(required=False, label="Nombre de pièces minimum")
    nb_pieces_max = forms.IntegerField(required=False, label="Nombre de pièces maximum")
    superficie_min = forms.IntegerField(required=False, label="Superficie minimum")
    superficie_max = forms.IntegerField(required=False, label="Superficie maximum")
    budget_max = forms.DecimalField(max_digits=10, decimal_places=2, required=False, label="Prix maximum")
    ville = forms.CharField(max_length=50, required=True, label="Ville")
    code_postal = forms.IntegerField(required=False, label="Code postal")
    rayon_km = forms.IntegerField(
    required=False,
    label="Rayon de recherche (km)",
    min_value=1,
    max_value=100)

    date_emmenagement = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))

    # Options
    parking = forms.BooleanField(required=False)
    balcon = forms.BooleanField(required=False)
    ascenseur = forms.BooleanField(required=False)
    jardin = forms.BooleanField(required=False)
    piscine = forms.BooleanField(required=False)



class AjouterBienForm(forms.Form):
    agent = forms.ModelChoiceField(queryset=Agent.objects.all())
    vendeur = forms.ModelChoiceField(queryset=Vendeur.objects.all())
    
    # Champs du bien à remplir
    type_bien = forms.ChoiceField(choices=[('', '---------')] + list(BienImmobilier._meta.get_field('type_bien').choices), required=True)
    categorie = forms.ChoiceField(choices=[('', '---------')] + list(BienImmobilier._meta.get_field('categorie').choices), required=True)
    numero_voie = forms.CharField()
    type_voie = forms.ChoiceField(choices=[('', '---------')] + list(BienImmobilier._meta.get_field('type_voie').choices), required=True)
    nom_voie = forms.CharField()
    code_postal = forms.IntegerField()
    ville = forms.CharField()
    nb_pieces = forms.IntegerField()
    superficie = forms.IntegerField()
    prix = forms.DecimalField(max_digits=10, decimal_places=2)
    date_disponibilite = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    statut = forms.ChoiceField(choices=[('', '---------')] + list(BienImmobilier._meta.get_field('statut').choices), required=True)
    
    # Champs supplémentaires
    descriptions = forms.CharField(required=False, widget=forms.Textarea)
    latitude = forms.DecimalField(max_digits=9, decimal_places=6, required=False)
    longitude = forms.DecimalField(max_digits=9, decimal_places=6, required=False)
    url_wikipedia = forms.URLField(required=False)

    # Options
    parking = forms.BooleanField(required=False)
    balcon = forms.BooleanField(required=False)
    ascenseur = forms.BooleanField(required=False)
    jardin = forms.BooleanField(required=False)
    piscine = forms.BooleanField(required=False)
    