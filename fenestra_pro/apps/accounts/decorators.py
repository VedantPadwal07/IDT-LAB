"""Role-based access decorators for FENESTRA PRO."""
from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required


def maker_required(view_func):
    """Restrict view to maker (manufacturer) users only."""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.is_maker:
            return view_func(request, *args, **kwargs)
        return redirect('customer_dashboard')
    return wrapper


def customer_required(view_func):
    """Restrict view to customer users only."""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.is_customer:
            return view_func(request, *args, **kwargs)
        return redirect('maker_dashboard')
    return wrapper
