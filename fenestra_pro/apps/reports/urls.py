from django.urls import path
from apps.reports import views

urlpatterns = [
    path('quotation/<str:number>/pdf/', views.download_quotation_pdf, name='download_quotation_pdf'),
    path('boq/<str:code>/pdf/', views.download_boq_pdf, name='download_boq_pdf'),
    path('production/<str:code>/pdf/', views.download_production_pdf, name='download_production_pdf'),
]
