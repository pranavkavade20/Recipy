from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from .forms import UserRegistrationForm

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            # Auto-login after successful registration so the user doesn't
            # have to immediately log in again on the next page.
            auth_login(request, new_user)
            return redirect('recipes:home')
    else:
        user_form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'user_form': user_form})

