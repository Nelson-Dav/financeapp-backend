from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Count
from django.utils import timezone
from transactions.models import Transaction
from budgets.models import Budget, Debt
import datetime


class DashboardView(APIView):
    def get(self, request):
        user  = request.user
        today = timezone.now().date()
        month = today.month
        year  = today.year

        month_qs = Transaction.objects.filter(user=user, date__month=month, date__year=year)

        total_income  = month_qs.filter(type='income').aggregate(t=Sum('amount'))['t'] or 0
        total_expense = month_qs.filter(type='expense').aggregate(t=Sum('amount'))['t'] or 0
        balance       = total_income - total_expense

        all_income  = Transaction.objects.filter(user=user, type='income').aggregate(t=Sum('amount'))['t'] or 0
        all_expense = Transaction.objects.filter(user=user, type='expense').aggregate(t=Sum('amount'))['t'] or 0
        global_balance = all_income - all_expense

        debts_due = Debt.objects.filter(user=user, is_paid=False, type='payable').aggregate(t=Sum('amount'))['t'] or 0
        recv_due  = Debt.objects.filter(user=user, is_paid=False, type='receivable').aggregate(t=Sum('amount'))['t'] or 0

        recent = Transaction.objects.filter(user=user).select_related('category').order_by('-date', '-created_at')[:5]
        recent_data = [
            {
                'id':          t.id,
                'type':        t.type,
                'amount':      float(t.amount),
                'description': t.description,
                'date':        t.date.strftime('%d/%m/%Y'),
                'category':    t.category.name if t.category else '—',
                'color':       t.category.color if t.category else '#6b7280',
            }
            for t in recent
        ]

        by_category = (
            month_qs.filter(type='expense')
            .values('category__name', 'category__color')
            .annotate(total=Sum('amount'))
            .order_by('-total')[:6]
        )
        chart_data = [
            {
                'name':  item['category__name'] or 'Sans catégorie',
                'value': float(item['total']),
                'color': item['category__color'] or '#6b7280',
            }
            for item in by_category
        ]

        monthly_trend = []
        for i in range(5, -1, -1):
            d = today.replace(day=1) - datetime.timedelta(days=i * 30)
            m_income  = Transaction.objects.filter(user=user, type='income',  date__month=d.month, date__year=d.year).aggregate(t=Sum('amount'))['t'] or 0
            m_expense = Transaction.objects.filter(user=user, type='expense', date__month=d.month, date__year=d.year).aggregate(t=Sum('amount'))['t'] or 0
            monthly_trend.append({
                'month':   d.strftime('%b %Y'),
                'income':  float(m_income),
                'expense': float(m_expense),
            })

        return Response({
            'global_balance':      float(global_balance),
            'month_income':        float(total_income),
            'month_expense':       float(total_expense),
            'month_balance':       float(balance),
            'debts_due':           float(debts_due),
            'receivable_due':      float(recv_due),
            'recent_transactions': recent_data,
            'chart_by_category':   chart_data,
            'monthly_trend':       monthly_trend,
        })


class MonthlyReportView(APIView):
    def get(self, request):
        user  = request.user
        today = timezone.now().date()
        month = int(request.query_params.get('month', today.month))
        year  = int(request.query_params.get('year',  today.year))

        qs = Transaction.objects.filter(user=user, date__month=month, date__year=year).select_related('category')

        total_income  = qs.filter(type='income').aggregate(t=Sum('amount'))['t'] or 0
        total_expense = qs.filter(type='expense').aggregate(t=Sum('amount'))['t'] or 0

        # Détail par catégorie
        by_cat = (
            qs.values('category__name', 'category__color', 'type')
            .annotate(total=Sum('amount'), count=Count('id'))
            .order_by('type', '-total')
        )

        # Toutes les transactions du mois
        transactions = [
            {
                'id':          t.id,
                'date':        t.date.strftime('%d/%m/%Y'),
                'type':        t.type,
                'amount':      float(t.amount),
                'description': t.description or '—',
                'reference':   t.reference or '—',
                'category':    t.category.name if t.category else '—',
            }
            for t in qs.order_by('-date')
        ]

        return Response({
            'month':         month,
            'year':          year,
            'total_income':  float(total_income),
            'total_expense': float(total_expense),
            'net':           float(total_income - total_expense),
            'by_category':   [
                {
                    'category': item['category__name'] or 'Sans catégorie',
                    'color':    item['category__color'] or '#6b7280',
                    'type':     item['type'],
                    'total':    float(item['total']),
                    'count':    item['count'],
                }
                for item in by_cat
            ],
            'transactions': transactions,
        })


class AlertsView(APIView):
    """
    Analyse intelligente : génère des recommandations automatiques
    basées sur les données financières de l'utilisateur.
    """
    def get(self, request):
        user  = request.user
        today = timezone.now().date()
        month = today.month
        year  = today.year

        alerts = []

        # 1. Budgets dépassés ou proches du plafond
        budgets = Budget.objects.filter(user=user, month=month, year=year).select_related('category')
        for b in budgets:
            spent = Transaction.objects.filter(
                user=user, type='expense',
                category=b.category,
                date__month=month, date__year=year
            ).aggregate(t=Sum('amount'))['t'] or 0

            pct = (float(spent) / float(b.amount) * 100) if b.amount > 0 else 0

            if pct >= 100:
                alerts.append({
                    'type':    'danger',
                    'icon':    '🚨',
                    'title':   f'Budget dépassé — {b.category.name}',
                    'message': f'Vous avez dépensé {int(pct)}% de votre budget {b.category.name}. '
                               f'Plafond : {float(b.amount):,.0f} XOF | Dépensé : {float(spent):,.0f} XOF.',
                })
            elif pct >= 80:
                alerts.append({
                    'type':    'warning',
                    'icon':    '⚠️',
                    'title':   f'Budget presque atteint — {b.category.name}',
                    'message': f'{int(pct)}% de votre budget {b.category.name} utilisé. '
                               f'Il vous reste {float(b.amount - spent):,.0f} XOF.',
                })

        # 2. Dettes en retard
        overdue_debts = Debt.objects.filter(
            user=user, is_paid=False, type='payable',
            due_date__lt=today
        )
        for d in overdue_debts:
            jours = (today - d.due_date).days
            alerts.append({
                'type':    'danger',
                'icon':    '📅',
                'title':   f'Paiement en retard — {d.contact}',
                'message': f'Vous devez {float(d.amount):,.0f} XOF à {d.contact}. '
                           f'Échéance dépassée depuis {jours} jour(s).',
            })

        # 3. Créances en retard (relancer le client)
        overdue_recv = Debt.objects.filter(
            user=user, is_paid=False, type='receivable',
            due_date__lt=today
        )
        for d in overdue_recv:
            jours = (today - d.due_date).days
            alerts.append({
                'type':    'warning',
                'icon':    '📬',
                'title':   f'Relancer {d.contact}',
                'message': f'{d.contact} vous doit {float(d.amount):,.0f} XOF depuis {jours} jour(s). '
                           f'Pensez à envoyer un rappel de paiement.',
            })

        # 4. Analyse trésorerie : dépenses en hausse vs mois précédent
        prev_month = month - 1 if month > 1 else 12
        prev_year  = year if month > 1 else year - 1

        curr_expense = Transaction.objects.filter(
            user=user, type='expense', date__month=month, date__year=year
        ).aggregate(t=Sum('amount'))['t'] or 0

        prev_expense = Transaction.objects.filter(
            user=user, type='expense', date__month=prev_month, date__year=prev_year
        ).aggregate(t=Sum('amount'))['t'] or 0

        if prev_expense > 0 and curr_expense > 0:
            variation = ((float(curr_expense) - float(prev_expense)) / float(prev_expense)) * 100
            if variation >= 30:
                alerts.append({
                    'type':    'warning',
                    'icon':    '📈',
                    'title':   'Dépenses en forte hausse',
                    'message': f'Vos dépenses ce mois sont en hausse de {variation:.0f}% '
                               f'par rapport au mois précédent. Analysez vos postes de dépenses.',
                })

        # 5. Solde faible
        all_income  = Transaction.objects.filter(user=user, type='income').aggregate(t=Sum('amount'))['t'] or 0
        all_expense = Transaction.objects.filter(user=user, type='expense').aggregate(t=Sum('amount'))['t'] or 0
        solde = float(all_income) - float(all_expense)

        month_expense_avg = float(curr_expense)
        if month_expense_avg > 0 and solde < month_expense_avg:
            alerts.append({
                'type':    'danger',
                'icon':    '💸',
                'title':   'Trésorerie critique',
                'message': f'Votre solde ({solde:,.0f} XOF) est inférieur à vos dépenses mensuelles '
                           f'({month_expense_avg:,.0f} XOF). Anticipez vos entrées d\'argent.',
            })

        # 6. Bonne nouvelle : mois excédentaire
        curr_income = Transaction.objects.filter(
            user=user, type='income', date__month=month, date__year=year
        ).aggregate(t=Sum('amount'))['t'] or 0

        if float(curr_income) > 0 and float(curr_income) > float(curr_expense) * 1.5:
            alerts.append({
                'type':    'success',
                'icon':    '✅',
                'title':   'Excellent mois !',
                'message': f'Vos entrées ({float(curr_income):,.0f} XOF) dépassent largement vos dépenses '
                           f'({float(curr_expense):,.0f} XOF). Pensez à épargner l\'excédent.',
            })

        if not alerts:
            alerts.append({
                'type':    'success',
                'icon':    '🟢',
                'title':   'Situation saine',
                'message': 'Aucune alerte ce mois. Continuez sur cette lancée !',
            })

        return Response({'alerts': alerts})