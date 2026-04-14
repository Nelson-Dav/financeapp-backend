from django.db import models
from django.conf import settings
from transactions.models import Category

class Budget(models.Model):
    """Plafond de dépense par catégorie sur une période."""
    MONTHLY = 'monthly'
    WEEKLY  = 'weekly'
    PERIOD_CHOICES = [(MONTHLY, 'Mensuel'), (WEEKLY, 'Hebdomadaire')]

    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='budgets')
    category   = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='budgets')
    amount     = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Plafond")
    period     = models.CharField(max_length=10, choices=PERIOD_CHOICES, default=MONTHLY)
    month      = models.PositiveIntegerField(null=True, blank=True)  # 1-12
    year       = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Budget"
        unique_together = ('user', 'category', 'month', 'year')

    def __str__(self):
        return f"Budget {self.category} — {self.amount}"


class Debt(models.Model):
    """Dette ou créance : argent dû ou à recevoir."""
    PAYABLE    = 'payable'    # on doit de l'argent à quelqu'un
    RECEIVABLE = 'receivable' # quelqu'un nous doit de l'argent
    TYPE_CHOICES = [(PAYABLE, 'À payer'), (RECEIVABLE, 'À recevoir')]

    user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='debts')
    type        = models.CharField(max_length=15, choices=TYPE_CHOICES)
    contact     = models.CharField(max_length=255, verbose_name="Client / Fournisseur")
    amount      = models.DecimalField(max_digits=15, decimal_places=2)
    due_date    = models.DateField(null=True, blank=True, verbose_name="Échéance")
    is_paid     = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Dette / Créance"
        ordering = ['due_date']

    def __str__(self):
        return f"{self.type} — {self.contact} — {self.amount}"