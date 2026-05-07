"""Account views for FENESTRA PRO."""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.accounts.forms import CustomerRegistrationForm, CustomLoginForm


def landing_page(request):
    """Split-screen landing page with two login portals."""
    if request.user.is_authenticated:
        if request.user.is_maker:
            return redirect('maker_dashboard')
        return redirect('customer_dashboard')
    return render(request, 'landing.html')


def customer_login(request):
    """Customer login view."""
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_customer:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                return redirect('customer_dashboard')
            else:
                messages.error(request, 'This login is for customers only.')
        else:
            messages.error(request, 'Invalid credentials.')
    else:
        form = CustomLoginForm()
    return render(request, 'accounts/login.html', {'form': form, 'portal': 'customer'})


def maker_login(request):
    """Maker login view."""
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_maker:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                return redirect('maker_dashboard')
            else:
                messages.error(request, 'This login is for manufacturers only.')
        else:
            messages.error(request, 'Invalid credentials.')
    else:
        form = CustomLoginForm()
    return render(request, 'accounts/login.html', {'form': form, 'portal': 'maker'})


def customer_register(request):
    """Customer registration view."""
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome to Fenestra Pro.')
            return redirect('customer_dashboard')
    else:
        form = CustomerRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def user_logout(request):
    """Logout view."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('landing')


@login_required
def profile_view(request):
    """User profile view."""
    return render(request, 'accounts/profile.html')
