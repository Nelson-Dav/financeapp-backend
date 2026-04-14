from django.db import models
from django.conf import settings

class Category(models.Model):
    """Catégorie de transaction : Vente, Loyer, Salaire, etc."""
    INCOME  = 'income'
    EXPENSE = 'expense'
    TYPE_CHOICES = [(INCOME, 'Entrée'), (EXPENSE, 'Sortie')]

    user      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='categories')
    name      = models.CharField(max_length=100)
    type      = models.CharField(max_length=10, choices=TYPE_CHOICES)
    icon      = models.CharField(max_length=50, blank=True)  # nom d'icône pour le frontend
    color     = models.CharField(max_length=7, default='#3B82F6')  # hex color

    class Meta:
        verbose_name = "Catégorie"
        unique_together = ('user', 'name', 'type')  # pas de doublon par user

    def __str__(self):
        return f"{self.name} ({self.type})"


class Transaction(models.Model):
    """
    Entrée ou sortie d'argent.
    """
    INCOME  = 'income'
    EXPENSE = 'expense'
    TYPE_CHOICES = [(INCOME, 'Entrée'), (EXPENSE, 'Sortie')]

    user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    category    = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    type        = models.CharField(max_length=10, choices=TYPE_CHOICES)
    amount      = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField(blank=True)
    date        = models.DateField()
    reference   = models.CharField(max_length=100, blank=True)  # numéro facture, etc.
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Transaction"
        ordering = ['-date', '-created_at']  # plus récentes en premier

    def __str__(self):
        return f"{self.type} — {self.amount} — {self.date}"