from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BudgetViewSet, DebtViewSet

router = DefaultRouter()
router.register('budgets', BudgetViewSet, basename='budget')
router.register('debts',   DebtViewSet,   basename='debt')

urlpatterns = [path('', include(router.urls))]