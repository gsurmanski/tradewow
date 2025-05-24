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
                return HttpResponseRedirect(reverse("index"))
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

            #if logged in, can't create account
            if request.user.is_authenticated:
                form.add_error(None, 'You already have an account')

            # Ensure password matches confirmation
            password = request.POST["password"]
            confirmation = request.POST["confirm_password"]
            if password != confirmation:
                form.add_error(None, 'Passwords Do Not Match')

            # Attempt to create new user
            try:
                user = User.objects.create_user(username, email, password)
                user.save()
            except IntegrityError:
                form.add_error(None, 'Username already Exists')

            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            form.add_error(None, 'Invalid username, password, or email')
    else:
        form = RegisterForm()
    return render(request, "register.html", {'form': form})