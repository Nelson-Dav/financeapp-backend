from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Utilisateur personnalisé — étend le User Django de base.
    AbstractUser = comme hériter d'IdentityUser en ASP.NET
    """
    company_name = models.CharField(max_length=255, blank=True, verbose_name="Nom de l'entreprise")
    phone        = models.CharField(max_length=10, blank=True, verbose_name="Téléphone")
    currency     = models.CharField(max_length=10, default='XOF', verbose_name="Devise")
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Utilisateur"

    def __str__(self):
        return f"{self.username} — {self.company_name}"