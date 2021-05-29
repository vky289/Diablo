from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .forms import LoginForm, SignUpForm, ProfileForm
from django.contrib import messages
from django.views.generic import RedirectView, DetailView, TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin


def login_view(request):
    form = LoginForm(request.POST or None)

    msg = None

    if request.method == "POST":

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating the form'

    return render(request, "accounts/login.html", {"form": form, "msg": msg})


def register_user(request):
    msg = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)

            msg = 'User created - please <a href="/login">login</a>.'
            success = True

            # return redirect("/login/")

        else:
            msg = 'Form is not valid'
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success})


def profile_user(request):
    success = False
    form = ProfileForm(request.POST or {'id': request.user.id, 'username': request.user.username, "firstname": request.user.first_name,
                                        "lastname": request.user.last_name, "email": request.user.email})
    if not form.is_bound:
        form = ProfileForm()

    if request.method == "POST":

        if form.is_valid():
            firstname = form.cleaned_data.get('firstname')
            lastname = form.cleaned_data.get('lastname')
            email = form.cleaned_data.get('email')
            try:
                user = User.objects.get(username=request.user)
                user.email = email
                user.first_name = firstname
                user.last_name = lastname
                user.save()
                messages.info(request, 'Saved successfully!')
                success = True
            except User.DoesNotExist:
                messages.info(request, 'User Doesnt found')

    return render(request, "page-user.html", {"form": form, "success": success})
