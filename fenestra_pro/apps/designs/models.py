"""
Window/Door Design models for FENESTRA PRO.
Core design entity storing all specifications.
"""
import datetime
from django.db import models
from django.conf import settings
from decimal import Decimal


class WindowDoorDesign(models.Model):
    """A window or door design specification with all parameters."""

    class DesignType(models.TextChoices):
        SLIDING_WINDOW = 'sliding_window', 'Sliding Window'
        CASEMENT_WINDOW = 'casement_window', 'Casement Window'
        FIXED_WINDOW = 'fixed_window', 'Fixed Window'
        SLIDING_DOOR = 'sliding_door', 'Sliding Door'
        CASEMENT_DOOR = 'casement_door', 'Casement Door'
        FRENCH_DOOR = 'french_door', 'French Door'
        BI_FOLD_DOOR = 'bi_fold_door', 'Bi-fold Door'
        TILT_TURN = 'tilt_turn', 'Tilt & Turn'

    class GlassChoice(models.TextChoices):
        CLEAR_FLOAT = 'clear_float', 'Clear Float'
        TINTED = 'tinted', 'Tinted'
        FROSTED = 'frosted', 'Frosted'
        TEMPERED = 'tempered', 'Tempered'
        DOUBLE_GLAZED = 'double_glazed', 'Double Glazed'
        LAMINATED = 'laminated', 'Laminated'
        REFLECTIVE = 'reflective', 'Reflective'

    class FrameMaterial(models.TextChoices):
        UPVC = 'upvc', 'uPVC'
        ALUMINIUM_STD = 'aluminium_standard', 'Aluminium (Standard)'
        ALUMINIUM_TB = 'aluminium_thermal_break', 'Aluminium (Thermal Break)'
        WOOD_COMPOSITE = 'wood_composite', 'Wood Composite'

    class Finish(models.TextChoices):
        WHITE = 'white', 'White'
        BLACK = 'black', 'Black'
        GREY = 'grey', 'Grey'
        BRONZE = 'bronze', 'Bronze'
        CHAMPAGNE = 'champagne', 'Champagne'
        WOOD_GRAIN_OAK = 'wood_grain_oak', 'Wood Grain (Oak)'
        WOOD_GRAIN_TEAK = 'wood_grain_teak', 'Wood Grain (Teak)'
        CUSTOM_RAL = 'custom_ral', 'Custom RAL Color'

    class MeshType(models.TextChoices):
        NONE = 'none', 'None'
        FIBERGLASS = 'fiberglass', 'Fiberglass'
        STAINLESS_STEEL = 'stainless_steel', 'Stainless Steel'

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        QUOTED = 'quoted', 'Quoted'
        APPROVED = 'approved', 'Approved'
        IN_PRODUCTION = 'in_production', 'In Production'
        COMPLETED = 'completed', 'Completed'

    # Auto-generated code
    code = models.CharField(max_length=20, unique=True, editable=False)
    name = models.CharField(max_length=200, help_text="Design name/label")
    description = models.TextField(blank=True)

    # Type & Dimensions
    design_type = models.CharField(max_length=20, choices=DesignType.choices)
    width_mm = models.IntegerField(help_text="Width in millimeters")
    height_mm = models.IntegerField(help_text="Height in millimeters")
    num_panels = models.IntegerField(default=2, help_text="Number of panels/leaves")

    # Glass
    glass_type = models.CharField(max_length=20, choices=GlassChoice.choices, default=GlassChoice.CLEAR_FLOAT)
    glass_thickness_mm = models.IntegerField(default=5)

    # Frame
    frame_material = models.CharField(max_length=30, choices=FrameMaterial.choices, default=FrameMaterial.UPVC)
    finish = models.CharField(max_length=20, choices=Finish.choices, default=Finish.WHITE)

    # Mesh
    mesh_required = models.BooleanField(default=False)
    mesh_type = models.CharField(max_length=20, choices=MeshType.choices, default=MeshType.NONE)

    # Quantity
    quantity = models.IntegerField(default=1, help_text="Number of units to fabricate")

    # Typology configuration (panel layout)
    typology_config = models.JSONField(default=dict, blank=True)

    # Status
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)

    # Relationships
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='designs'
    )

    # Calculation results cached
    calculation_data = models.JSONField(default=dict, blank=True, help_text="Cached calculation results")
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Notes
    notes = models.TextField(blank=True, help_text="Customer notes or comments")

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self._generate_code()
        super().save(*args, **kwargs)

    def _generate_code(self):
        """Generate auto-incrementing code: WD-YYYY-XXXX"""
        year = datetime.datetime.now().year
        last = WindowDoorDesign.objects.filter(
            code__startswith=f'WD-{year}-'
        ).order_by('-code').first()
        if last:
            last_num = int(last.code.split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1
        return f'WD-{year}-{new_num:04d}'

    @property
    def area_sqm(self):
        """Calculate area in square meters."""
        return (self.width_mm * self.height_mm) / 1_000_000

    @property
    def is_door(self):
        return self.design_type in [
            self.DesignType.SLIDING_DOOR,
            self.DesignType.CASEMENT_DOOR,
            self.DesignType.FRENCH_DOOR,
            self.DesignType.BI_FOLD_DOOR,
        ]

    @property
    def is_window(self):
        return not self.is_door

    @property
    def type_display_name(self):
        return self.get_design_type_display()

    def __str__(self):
        return f"{self.code} - {self.name} ({self.get_design_type_display()})"

    class Meta:
        verbose_name = 'Design'
        verbose_name_plural = 'Designs'
        ordering = ['-created_at']


class DesignRevision(models.Model):
    """Track changes made to a design."""
    design = models.ForeignKey(WindowDoorDesign, on_delete=models.CASCADE, related_name='revisions')
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    changes = models.JSONField(default=dict, help_text="Fields that changed with old/new values")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Revision for {self.design.code} at {self.created_at}"

    class Meta:
        ordering = ['-created_at']
