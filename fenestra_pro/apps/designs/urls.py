from django.urls import path
from apps.designs import views

urlpatterns = [
    path('new/', views.design_wizard, name='design_wizard'),
    path('list/', views.design_list, name='design_list'),
    path('<str:code>/', views.design_detail, name='design_detail'),
    path('<str:code>/recalculate/', views.design_recalculate, name='design_recalculate'),
    path('<str:code>/status/', views.design_update_status, name='design_update_status'),
    path('<str:code>/delete/', views.design_delete, name='design_delete'),
    path('api/calculate/', views.calculate_live, name='calculate_live'),
]
