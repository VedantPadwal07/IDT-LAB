"""Account URL configuration."""
from django.urls import path
from apps.accounts import views

urlpatterns = [
    path('login/customer/', views.customer_login, name='customer_login'),
    path('login/maker/', views.maker_login, name='maker_login'),
    path('register/', views.customer_register, name='customer_register'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile_view, name='profile'),
]
