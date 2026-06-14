from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import LoginForm, ProfileForm, CustomPasswordChangeForm
from .models import User


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        
        # Si debe cambiar contraseña, redirigir
        if user.must_change_password:
            messages.warning(request, 'Por seguridad, debes cambiar tu contraseña antes de continuar.')
            return redirect('accounts:change_password')
        
        next_url = request.GET.get('next', 'dashboard:home')
        return redirect(next_url)
    
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('accounts:login')


@login_required
def profile_view(request):
    form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Perfil actualizado correctamente.')
        return redirect('accounts:profile')
    return render(request, 'accounts/profile.html', {'form': form})


@login_required
def change_password_view(request):
    form = CustomPasswordChangeForm(request.user, request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        user.must_change_password = False
        user.save(update_fields=['must_change_password'])
        update_session_auth_hash(request, user)
        messages.success(request, '¡Contraseña actualizada correctamente!')
        return redirect('dashboard:home')
    return render(request, 'accounts/change_password.html', {'form': form})
