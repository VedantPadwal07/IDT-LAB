"""
Pricing configuration for FENESTRA PRO.
Singleton model for system-wide pricing parameters.
"""
from django.db import models
from decimal import Decimal


class PricingConfig(models.Model):
    """System-wide pricing configuration. Only one instance should exist."""

    name = models.CharField(max_length=100, default='Default Pricing')

    # Markup percentages
    profile_markup_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal('25.00'),
        help_text="Markup on profile material costs"
    )
    glass_markup_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal('20.00'),
        help_text="Markup on glass costs"
    )
    hardware_markup_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal('30.00'),
        help_text="Markup on hardware costs"
    )

    # Labour & Overhead
    labour_cost_per_unit = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('500.00'),
        help_text="Labour cost per window/door unit"
    )
    overhead_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal('10.00'),
        help_text="Overhead percentage on total cost"
    )

    # Tax
    tax_rate_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal('18.00'),
        help_text="Tax rate (e.g. GST)"
    )

    # Currency
    currency_symbol = models.CharField(max_length=10, default='₹')
    currency_code = models.CharField(max_length=5, default='INR')

    # Cutting parameters
    saw_kerf_mm = models.IntegerField(default=3, help_text="Saw blade kerf in mm")
    clearance_gap_mm = models.IntegerField(default=4, help_text="Glass clearance gap in mm")

    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @classmethod
    def get_active(cls):
        """Get the active pricing configuration."""
        config, _ = cls.objects.get_or_create(is_active=True, defaults={'name': 'Default Pricing'})
        return config

    class Meta:
        verbose_name = 'Pricing Configuration'
        verbose_name_plural = 'Pricing Configurations'
