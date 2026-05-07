"""
Cutting rule models for FENESTRA PRO.
Defines how profiles are cut for each window/door type.
"""
from django.db import models
from apps.materials.models import ProfileDatabase


class CuttingRule(models.Model):
    """Defines cutting formulas for profiles based on window/door type."""

    class CutAngle(models.TextChoices):
        DEG_90 = '90deg', '90°'
        DEG_45 = '45deg', '45°'

    WINDOW_DOOR_TYPES = [
        ('sliding_window', 'Sliding Window'),
        ('casement_window', 'Casement Window'),
        ('fixed_window', 'Fixed Window'),
        ('sliding_door', 'Sliding Door'),
        ('casement_door', 'Casement Door'),
        ('french_door', 'French Door'),
        ('bi_fold_door', 'Bi-fold Door'),
        ('tilt_turn', 'Tilt & Turn'),
    ]

    applies_to_type = models.CharField(max_length=20, choices=WINDOW_DOOR_TYPES)
    profile = models.ForeignKey(ProfileDatabase, on_delete=models.CASCADE, related_name='cutting_rules')
    description = models.CharField(max_length=200, help_text="e.g. 'Frame Top Rail', 'Sash Left Stile'")
    formula = models.JSONField(
        default=dict,
        help_text='Calculation formula, e.g. {"base": "width", "subtract": 120, "add": 0}'
    )
    quantity_per_unit = models.IntegerField(default=1, help_text="Number of this piece per window/door unit")
    cut_angle = models.CharField(max_length=10, choices=CutAngle.choices, default=CutAngle.DEG_90)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.applies_to_type} → {self.description} ({self.profile.profile_code})"

    class Meta:
        verbose_name = 'Cutting Rule'
        verbose_name_plural = 'Cutting Rules'
        ordering = ['applies_to_type', 'sort_order']
