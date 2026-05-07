from django.urls import path
from apps.dashboard import views

urlpatterns = [
    path('', views.dashboard_redirect, name='dashboard'),
    path('customer/', views.customer_dashboard, name='customer_dashboard'),
    path('maker/', views.maker_dashboard, name='maker_dashboard'),
]
