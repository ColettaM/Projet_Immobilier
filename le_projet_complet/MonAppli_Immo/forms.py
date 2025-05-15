from django import forms
from .models import *

# forms.py

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

