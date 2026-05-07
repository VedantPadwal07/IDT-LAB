"""
Quotation models for FENESTRA PRO.
Manages customer quotations linked to designs.
"""
import datetime
from django.db import models
from django.conf import settings
from decimal import Decimal
from apps.designs.models import WindowDoorDesign


class Quotation(models.Model):
    """A customer quotation containing one or more designs."""

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        SENT = 'sent', 'Sent'
        ACCEPTED = 'accepted', 'Accepted'
        REJECTED = 'rejected', 'Rejected'
        EXPIRED = 'expired', 'Expired'

    quotation_number = models.CharField(max_length=20, unique=True, editable=False)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quotations',
        limit_choices_to={'role': 'customer'}
    )
    designs = models.ManyToManyField(WindowDoorDesign, related_name='quotations')

    # Cost breakdown stored as JSON
    line_items = models.JSONField(default=list, blank=True)

    # Totals
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))

    # Validity
    validity_days = models.IntegerField(default=30)
    valid_until = models.DateField(null=True, blank=True)

    # Status & notes
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    notes = models.TextField(blank=True)
    terms_conditions = models.TextField(
        blank=True,
        default=(
            "1. Prices are valid for the period mentioned above.\n"
            "2. 50% advance payment required to confirm the order.\n"
            "3. Balance payment before delivery.\n"
            "4. Delivery within 15-20 working days from confirmation.\n"
            "5. Installation charges are included.\n"
            "6. Warranty: 10 years on profiles, 1 year on hardware.\n"
            "7. GST as applicable."
        )
    )

    generated_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.quotation_number:
            self.quotation_number = self._generate_number()
        if not self.valid_until:
            self.valid_until = (
                datetime.datetime.now() + datetime.timedelta(days=self.validity_days)
            ).date()
        super().save(*args, **kwargs)

    def _generate_number(self):
        """Generate auto-incrementing quotation number: QT-YYYY-XXXX"""
        year = datetime.datetime.now().year
        last = Quotation.objects.filter(
            quotation_number__startswith=f'QT-{year}-'
        ).order_by('-quotation_number').first()
        if last:
            last_num = int(last.quotation_number.split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1
        return f'QT-{year}-{new_num:04d}'

    @property
    def is_expired(self):
        if self.valid_until:
            return datetime.date.today() > self.valid_until
        return False

    def __str__(self):
        return f"{self.quotation_number} - {self.customer.company_name or self.customer.username}"

    class Meta:
        verbose_name = 'Quotation'
        verbose_name_plural = 'Quotations'
        ordering = ['-generated_at']
