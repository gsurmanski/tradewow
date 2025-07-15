from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .forms import *
from django.http import JsonResponse
import json


#import models
from .models import User

# Create your views here.
def index (request):
    return render(request, "index.html")

def dashboard(request):
    return render(request, "dashboard.html")

def features(request):
    return render(request, "features.html")

def company(request):
    return render(request, "company.html")

def product(request):
    return render(request, "product.html")

@login_required
def profile(request):
    user = request.user
    old_file = user.profile_image

    if request.method == "POST":
        form = UploadPic(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            #save new image  
            form.save()
            
            # Now delete the old file from disk, if it was different
            if old_file and old_file != user.profile_image:
                old_file.delete(save=False)

            return HttpResponseRedirect(reverse("profile"))
    else:
        form = UploadPic(instance=request.user)

    return render(request, "profile.html", {'form': form})

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        
        if form.is_valid():                 
            # Attempt to sign user in
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            # Check if authentication successful
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse("dashboard"))
            else:
                form.add_error(None, 'Invalid username or password')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = request.POST["password"]
            confirmation = request.POST["confirm_password"]

            # Validation flags
            has_error = False

            # Check if already logged in
            if request.user.is_authenticated:
                form.add_error(None, 'You already have an account')
                has_error = True

            # Password confirmation check
            if password != confirmation:
                form.add_error('confirm_password', 'Passwords do not match')
                has_error = True

            #check for existing email
            email = form.cleaned_data['email']
            if User.objects.filter(email=email).exists():
                form.add_error('email', "Email already in use")
                has_error = True
    
            # Try creating user
            if not has_error:
                try:
                    user = User.objects.create_user(username, email, password)
                    user.save()
                except IntegrityError:
                    form.add_error("username", "Username already exists")
                else:
                    login(request, user)
                    return HttpResponseRedirect(reverse("index"))
        # Let the form fall through with errors if not valid
    else:
        form = RegisterForm()

    return render(request, "register.html", {'form': form})
