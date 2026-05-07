from django.contrib import admin
from apps.quotations.models import Quotation

@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ['quotation_number', 'customer', 'total', 'status', 'generated_at']
    list_filter = ['status']
    readonly_fields = ['quotation_number']
