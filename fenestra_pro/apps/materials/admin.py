from django.contrib import admin
from apps.materials.models import ProfileDatabase, GlassType, HardwareItem

@admin.register(ProfileDatabase)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['profile_code', 'profile_name', 'profile_type', 'material', 'cost_per_meter', 'is_active']
    list_filter = ['profile_type', 'material', 'is_active']
    search_fields = ['profile_code', 'profile_name']

@admin.register(GlassType)
class GlassTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'thickness_mm', 'price_per_sqm', 'is_active']
    list_filter = ['category', 'is_active']

@admin.register(HardwareItem)
class HardwareItemAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'category', 'unit', 'cost_per_unit', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['code', 'name']
