"""Dashboard views for FENESTRA PRO."""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from decimal import Decimal
from apps.accounts.decorators import maker_required, customer_required
from apps.designs.models import WindowDoorDesign
from apps.quotations.models import Quotation
from apps.accounts.models import CustomUser


@login_required
def dashboard_redirect(request):
    """Redirect to appropriate dashboard based on role."""
    if request.user.is_maker:
        return redirect('maker_dashboard')
    return redirect('customer_dashboard')


@customer_required
def customer_dashboard(request):
    """Customer dashboard with overview cards."""
    designs = WindowDoorDesign.objects.filter(created_by=request.user)
    quotations = Quotation.objects.filter(customer=request.user)
    context = {
        'total_designs': designs.count(),
        'draft_designs': designs.filter(status='draft').count(),
        'quoted_designs': designs.filter(status='quoted').count(),
        'approved_designs': designs.filter(status='approved').count(),
        'in_production': designs.filter(status='in_production').count(),
        'completed': designs.filter(status='completed').count(),
        'recent_designs': designs[:5],
        'quotations': quotations[:5],
        'total_quoted': quotations.aggregate(t=Sum('total'))['t'] or Decimal('0'),
    }
    return render(request, 'customer/dashboard.html', context)


@maker_required
def maker_dashboard(request):
    """Maker dashboard with analytics."""
    designs = WindowDoorDesign.objects.all()
    quotations = Quotation.objects.all()
    customers = CustomUser.objects.filter(role='customer')
    context = {
        'total_orders': designs.count(),
        'pending_approvals': designs.filter(status='quoted').count(),
        'in_production': designs.filter(status='in_production').count(),
        'completed': designs.filter(status='completed').count(),
        'total_customers': customers.count(),
        'total_revenue': quotations.filter(status='accepted').aggregate(t=Sum('total'))['t'] or Decimal('0'),
        'recent_orders': designs[:10],
        'recent_quotations': quotations[:5],
        'status_counts': {
            'draft': designs.filter(status='draft').count(),
            'quoted': designs.filter(status='quoted').count(),
            'approved': designs.filter(status='approved').count(),
            'in_production': designs.filter(status='in_production').count(),
            'completed': designs.filter(status='completed').count(),
        },
    }
    return render(request, 'maker/dashboard.html', context)
