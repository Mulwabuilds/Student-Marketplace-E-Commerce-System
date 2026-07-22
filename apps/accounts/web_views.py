from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import RegistrationForm, ProfileForm
from .models import Profile


def register_view(request):
    """
    No-OTP registration for the MVP demo (OTP flow deferred; see
    apps/accounts/views.py + docs/flags.md for the existing DRF OTP path,
    which this does not touch or replace).
    """
    if request.user.is_authenticated:
        return redirect('marketplace:browse')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_email_verified = True
            user.save()
            Profile.objects.get_or_create(user=user)
            login(request, user)
            return redirect('marketplace:browse')
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile_edit_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('accounts:profile-edit')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'accounts/profile_edit.html', {'form': form})
