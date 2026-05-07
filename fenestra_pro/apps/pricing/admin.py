from django.contrib import admin
from apps.pricing.models import PricingConfig

@admin.register(PricingConfig)
class PricingConfigAdmin(admin.ModelAdmin):
    list_display = ['name', 'currency_symbol', 'tax_rate_percent', 'is_active']
