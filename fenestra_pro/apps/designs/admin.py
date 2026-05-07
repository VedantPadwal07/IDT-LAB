from django.contrib import admin
from apps.designs.models import WindowDoorDesign, DesignRevision

@admin.register(WindowDoorDesign)
class DesignAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'design_type', 'width_mm', 'height_mm', 'status', 'created_by']
    list_filter = ['design_type', 'status', 'frame_material']
    search_fields = ['code', 'name']
    readonly_fields = ['code']

@admin.register(DesignRevision)
class RevisionAdmin(admin.ModelAdmin):
    list_display = ['design', 'changed_by', 'created_at']
