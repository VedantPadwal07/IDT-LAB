"""Design views for FENESTRA PRO."""
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from apps.designs.models import WindowDoorDesign
from apps.designs.forms import DesignStep1Form, DesignStep2Form, DesignStep3Form
from apps.calculations.engine import CalculationEngine
from apps.accounts.decorators import customer_required, maker_required


@customer_required
def design_wizard(request):
    """Multi-step design creation wizard."""
    if request.method == 'POST':
        form1 = DesignStep1Form(request.POST)
        form2 = DesignStep2Form(request.POST)
        form3 = DesignStep3Form(request.POST)
        if form1.is_valid() and form2.is_valid() and form3.is_valid():
            design = WindowDoorDesign()
            for form in [form1, form2, form3]:
                for field, value in form.cleaned_data.items():
                    setattr(design, field, value)
            design.created_by = request.user
            design.save()
            # Run calculations
            try:
                engine = CalculationEngine()
                result = engine.calculate(design)
                design.calculation_data = {
                    'cut_pieces': result.cut_pieces,
                    'glass_pieces': result.glass_pieces,
                    'hardware_items': result.hardware_items,
                    'bar_optimizations': result.bar_optimizations,
                    'cost_breakdown': result.cost_breakdown,
                }
                from decimal import Decimal
                design.estimated_cost = Decimal(result.cost_breakdown.get('total', '0'))
                design.save()
            except Exception as e:
                messages.warning(request, f'Design saved but calculations pending: {str(e)}')
            messages.success(request, f'Design {design.code} created successfully!')
            return redirect('design_detail', code=design.code)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form1 = DesignStep1Form()
        form2 = DesignStep2Form()
        form3 = DesignStep3Form()
    return render(request, 'customer/design_wizard.html', {
        'form1': form1, 'form2': form2, 'form3': form3
    })


@login_required
def design_list(request):
    """List designs - filtered by user role."""
    if request.user.is_maker:
        designs = WindowDoorDesign.objects.all()
    else:
        designs = WindowDoorDesign.objects.filter(created_by=request.user)

    # Filtering
    status = request.GET.get('status')
    design_type = request.GET.get('type')
    search = request.GET.get('q')
    if status:
        designs = designs.filter(status=status)
    if design_type:
        designs = designs.filter(design_type=design_type)
    if search:
        designs = designs.filter(name__icontains=search)

    template = 'maker/orders.html' if request.user.is_maker else 'customer/design_list.html'
    return render(request, template, {
        'designs': designs,
        'statuses': WindowDoorDesign.Status.choices,
        'types': WindowDoorDesign.DesignType.choices,
        'current_status': status,
        'current_type': design_type,
        'search_query': search or '',
    })


@login_required
def design_detail(request, code):
    """Design detail with full calculation breakdown."""
    design = get_object_or_404(WindowDoorDesign, code=code)
    if request.user.is_customer and design.created_by != request.user:
        messages.error(request, 'Access denied.')
        return redirect('design_list')
    template = 'maker/order_detail.html' if request.user.is_maker else 'customer/design_detail.html'
    calc_data = design.calculation_data or {}
    return render(request, template, {
        'design': design,
        'cut_pieces': calc_data.get('cut_pieces', []),
        'glass_pieces': calc_data.get('glass_pieces', []),
        'hardware_items': calc_data.get('hardware_items', []),
        'bar_optimizations': calc_data.get('bar_optimizations', []),
        'cost_breakdown': calc_data.get('cost_breakdown', {}),
    })


@login_required
def design_recalculate(request, code):
    """Recalculate a design."""
    design = get_object_or_404(WindowDoorDesign, code=code)
    engine = CalculationEngine()
    try:
        result = engine.calculate(design)
        design.calculation_data = {
            'cut_pieces': result.cut_pieces,
            'glass_pieces': result.glass_pieces,
            'hardware_items': result.hardware_items,
            'bar_optimizations': result.bar_optimizations,
            'cost_breakdown': result.cost_breakdown,
        }
        from decimal import Decimal
        design.estimated_cost = Decimal(result.cost_breakdown.get('total', '0'))
        design.save()
        messages.success(request, 'Calculations updated!')
    except Exception as e:
        messages.error(request, f'Calculation error: {e}')
    return redirect('design_detail', code=code)


@maker_required
def design_update_status(request, code):
    """Maker updates design status."""
    if request.method == 'POST':
        design = get_object_or_404(WindowDoorDesign, code=code)
        new_status = request.POST.get('status')
        if new_status in dict(WindowDoorDesign.Status.choices):
            design.status = new_status
            design.save()
            messages.success(request, f'Status updated to {design.get_status_display()}')
    return redirect('design_detail', code=code)


@login_required
def design_delete(request, code):
    """Delete a design."""
    design = get_object_or_404(WindowDoorDesign, code=code)
    if request.user.is_customer and design.created_by != request.user:
        messages.error(request, 'Access denied.')
        return redirect('design_list')
    if request.method == 'POST':
        design.delete()
        messages.success(request, 'Design deleted.')
        return redirect('design_list')
    return redirect('design_detail', code=code)


@login_required
def calculate_live(request):
    """AJAX endpoint for live cost estimation."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Create a temporary design object (not saved)
            design = WindowDoorDesign(
                design_type=data.get('design_type', 'sliding_window'),
                width_mm=int(data.get('width_mm', 1200)),
                height_mm=int(data.get('height_mm', 1500)),
                num_panels=int(data.get('num_panels', 2)),
                glass_type=data.get('glass_type', 'clear_float'),
                glass_thickness_mm=int(data.get('glass_thickness_mm', 5)),
                frame_material=data.get('frame_material', 'upvc'),
                quantity=int(data.get('quantity', 1)),
                created_by=request.user,
            )
            engine = CalculationEngine()
            result = engine.calculate(design)
            return JsonResponse({'success': True, 'cost': result.cost_breakdown})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'POST required'})
