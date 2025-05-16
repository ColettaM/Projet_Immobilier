from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import (
    Agent, Vendeur, Acheteur, BienImmobilier,
    PortefeuilleVendeur,PortefeuilleAcheteur, 
    SuiviBienVendeur,SuiviBienAcheteur, Criteres
)

admin.site.register(Agent)
admin.site.register(Vendeur)
admin.site.register(Acheteur)
admin.site.register(BienImmobilier)
admin.site.register(PortefeuilleVendeur)
admin.site.register(PortefeuilleAcheteur)
admin.site.register(SuiviBienAcheteur)
admin.site.register(SuiviBienVendeur)
admin.site.register(Criteres)
