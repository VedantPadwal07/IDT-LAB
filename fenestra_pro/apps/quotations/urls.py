from django.urls import path
from apps.quotations import views

urlpatterns = [
    path('create/', views.create_quotation, name='create_quotation'),
    path('list/', views.quotation_list, name='quotation_list'),
    path('<str:number>/', views.quotation_detail, name='quotation_detail'),
    path('<str:number>/status/', views.quotation_update_status, name='quotation_update_status'),
]
