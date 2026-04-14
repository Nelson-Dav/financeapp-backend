from rest_framework import viewsets
from django.db.models import Sum
from .models import Budget, Debt
from .serializers import BudgetSerializer, DebtSerializer
from transactions.models import Transaction
import datetime

class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user).select_related('category')

    def list(self, request, *args, **kwargs):
        """Surcharge pour calculer spent/remaining sur chaque budget"""
        response = super().list(request, *args, **kwargs)
        now = datetime.date.today()

        for budget_data in response.data:
            spent = Transaction.objects.filter(
                user=request.user,
                category_id=budget_data['category'],
                type='expense',
                date__month=budget_data.get('month') or now.month,
                date__year=budget_data.get('year') or now.year,
            ).aggregate(total=Sum('amount'))['total'] or 0

            budget_data['spent']     = float(spent)
            budget_data['remaining'] = float(budget_data['amount']) - float(spent)

        return response


class DebtViewSet(viewsets.ModelViewSet):
    serializer_class = DebtSerializer

    def get_queryset(self):
        return Debt.objects.filter(user=self.request.user)