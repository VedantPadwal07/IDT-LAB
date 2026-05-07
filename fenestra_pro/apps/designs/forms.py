"""Design forms for the multi-step wizard."""
from django import forms
from apps.designs.models import WindowDoorDesign


class DesignStep1Form(forms.ModelForm):
    """Step 1: Basic information."""
    class Meta:
        model = WindowDoorDesign
        fields = ['name', 'design_type', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g. Living Room Window'}),
            'description': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Optional description'}),
        }


class DesignStep2Form(forms.ModelForm):
    """Step 2: Dimensions & Glass."""
    class Meta:
        model = WindowDoorDesign
        fields = ['width_mm', 'height_mm', 'num_panels', 'glass_type', 'glass_thickness_mm']
        widgets = {
            'width_mm': forms.NumberInput(attrs={'placeholder': '1200', 'min': 300, 'max': 10000}),
            'height_mm': forms.NumberInput(attrs={'placeholder': '1500', 'min': 300, 'max': 10000}),
            'num_panels': forms.NumberInput(attrs={'min': 1, 'max': 8}),
            'glass_thickness_mm': forms.NumberInput(attrs={'min': 3, 'max': 24}),
        }


class DesignStep3Form(forms.ModelForm):
    """Step 3: Material & Finish."""
    class Meta:
        model = WindowDoorDesign
        fields = ['frame_material', 'finish', 'mesh_required', 'mesh_type', 'quantity', 'notes']
        widgets = {
            'quantity': forms.NumberInput(attrs={'min': 1, 'max': 500}),
            'notes': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Any special requirements?'}),
        }
