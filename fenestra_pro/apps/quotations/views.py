"""Quotation views for FENESTRA PRO."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal
from apps.quotations.models import Quotation
from apps.designs.models import WindowDoorDesign
from apps.pricing.models import PricingConfig
from apps.accounts.decorators import customer_required, maker_required


@customer_required
def create_quotation(request):
    """Create quotation from selected designs."""
    if request.method == 'POST':
        design_ids = request.POST.getlist('design_ids')
        if not design_ids:
            messages.error(request, 'Select at least one design.')
            return redirect('design_list')
        designs = WindowDoorDesign.objects.filter(
            code__in=design_ids, created_by=request.user, status='draft'
        )
        if not designs.exists():
            messages.error(request, 'No valid designs selected.')
            return redirect('design_list')
        pricing = PricingConfig.get_active()
        line_items = []
        subtotal = Decimal('0')
        for d in designs:
            cost = d.estimated_cost or Decimal('0')
            line_items.append({
                'design_code': d.code, 'description': f'{d.get_design_type_display()} - {d.name}',
                'dimensions': f'{d.width_mm}×{d.height_mm}mm', 'quantity': d.quantity,
                'unit_price': str(cost / d.quantity if d.quantity else cost),
                'total': str(cost),
            })
            subtotal += cost
        tax = subtotal * pricing.tax_rate_percent / 100
        total = subtotal + tax
        quot = Quotation(customer=request.user, subtotal=subtotal, tax_amount=tax, total=total,
                         line_items=line_items)
        quot.save()
        quot.designs.set(designs)
        designs.update(status='quoted')
        messages.success(request, f'Quotation {quot.quotation_number} generated!')
        return redirect('quotation_detail', number=quot.quotation_number)
    return redirect('design_list')


@login_required
def quotation_list(request):
    """List quotations."""
    if request.user.is_maker:
        quotations = Quotation.objects.all()
    else:
        quotations = Quotation.objects.filter(customer=request.user)
    return render(request, 'customer/quotation_list.html', {'quotations': quotations})


@login_required
def quotation_detail(request, number):
    """Quotation detail view."""
    quot = get_object_or_404(Quotation, quotation_number=number)
    if request.user.is_customer and quot.customer != request.user:
        messages.error(request, 'Access denied.')
        return redirect('quotation_list')
    return render(request, 'customer/quotation_detail.html', {'quotation': quot})


@maker_required
def quotation_update_status(request, number):
    """Maker updates quotation status."""
    if request.method == 'POST':
        quot = get_object_or_404(Quotation, quotation_number=number)
        new_status = request.POST.get('status')
        if new_status in dict(Quotation.Status.choices):
            quot.status = new_status
            quot.save()
            if new_status == 'accepted':
                quot.designs.update(status='approved')
            messages.success(request, f'Quotation status updated to {quot.get_status_display()}')
    return redirect('quotation_detail', number=number)
