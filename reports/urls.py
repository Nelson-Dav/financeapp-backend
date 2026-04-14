from django.urls import path
from .views import DashboardView, MonthlyReportView, AlertsView

urlpatterns = [
    path('reports/dashboard/', DashboardView.as_view()),
    path('reports/monthly/',   MonthlyReportView.as_view()),
    path('reports/alerts/',    AlertsView.as_view()),
]