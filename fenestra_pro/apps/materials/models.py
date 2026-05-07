"""
Material database models for FENESTRA PRO.
Profiles, hardware items, and glass types used in fabrication.
"""
from django.db import models
from decimal import Decimal


class ProfileDatabase(models.Model):
    """Frame profiles used in window/door fabrication."""

    class ProfileType(models.TextChoices):
        FRAME = 'frame', 'Frame'
        SASH = 'sash', 'Sash'
        MULLION = 'mullion', 'Mullion'
        TRANSOM = 'transom', 'Transom'
        BEAD = 'bead', 'Bead / Glazing Bead'
        THRESHOLD = 'threshold', 'Threshold'
        ADAPTER = 'adapter', 'Adapter'
        INTERLOCK = 'interlock', 'Interlock'
        TRACK = 'track', 'Track'

    class Material(models.TextChoices):
        UPVC = 'upvc', 'uPVC'
        ALUMINIUM_STD = 'aluminium_standard', 'Aluminium (Standard)'
        ALUMINIUM_TB = 'aluminium_thermal_break', 'Aluminium (Thermal Break)'
        WOOD_COMPOSITE = 'wood_composite', 'Wood Composite'

    profile_code = models.CharField(max_length=50, unique=True)
    profile_name = models.CharField(max_length=200)
    profile_type = models.CharField(max_length=20, choices=ProfileType.choices)
    material = models.CharField(max_length=30, choices=Material.choices, default=Material.UPVC)
    standard_bar_length_mm = models.IntegerField(default=6000, help_text="Standard bar length in mm")
    weight_per_meter_kg = models.DecimalField(max_digits=8, decimal_places=3, default=Decimal('0.500'))
    cost_per_meter = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    cutting_waste_factor = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal('5.00'),
        help_text="Waste factor percentage"
    )
    wall_thickness_mm = models.IntegerField(default=60, help_text="Profile wall/depth thickness in mm")
    rebate_depth_mm = models.IntegerField(default=18, help_text="Rebate depth for glass seating in mm")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.profile_code} - {self.profile_name}"

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'
        ordering = ['profile_type', 'profile_code']


class GlassType(models.Model):
    """Glass types with pricing per square meter."""

    class GlassCategory(models.TextChoices):
        CLEAR_FLOAT = 'clear_float', 'Clear Float'
        TINTED = 'tinted', 'Tinted'
        FROSTED = 'frosted', 'Frosted'
        TEMPERED = 'tempered', 'Tempered'
        DOUBLE_GLAZED = 'double_glazed', 'Double Glazed'
        LAMINATED = 'laminated', 'Laminated'
        REFLECTIVE = 'reflective', 'Reflective'

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=GlassCategory.choices, unique=True)
    thickness_mm = models.IntegerField(default=5)
    price_per_sqm = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.thickness_mm}mm)"

    class Meta:
        verbose_name = 'Glass Type'
        verbose_name_plural = 'Glass Types'
        ordering = ['category']


class HardwareItem(models.Model):
    """Hardware items used in window/door assembly."""

    class Category(models.TextChoices):
        HANDLE = 'handle', 'Handle'
        LOCK = 'lock', 'Lock'
        HINGE = 'hinge', 'Hinge'
        ROLLER = 'roller', 'Roller'
        SEAL = 'seal', 'Seal / Gasket'
        SCREW_PACK = 'screw_pack', 'Screw Pack'
        WEATHER_STRIP = 'weather_strip', 'Weather Strip'
        RESTRICTOR = 'restrictor', 'Restrictor'
        MOSQUITO_MESH = 'mosquito_mesh', 'Mosquito Mesh Kit'

    class Unit(models.TextChoices):
        PIECE = 'piece', 'Piece'
        SET = 'set', 'Set'
        METER = 'meter', 'Meter'
        PACK = 'pack', 'Pack'

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

    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=Category.choices)
    unit = models.CharField(max_length=10, choices=Unit.choices, default=Unit.PIECE)
    cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    applies_to_types = models.JSONField(
        default=list,
        help_text="List of window/door types this hardware applies to"
    )
    quantity_formula = models.CharField(
        max_length=200, blank=True,
        help_text="e.g. '2_per_sash', '1_per_unit', 'perimeter_m'"
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        verbose_name = 'Hardware Item'
        verbose_name_plural = 'Hardware Items'
        ordering = ['category', 'code']
