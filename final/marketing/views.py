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
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from django.views.decorators.http import require_POST

#import user creds for apis
from django.conf import settings

#for reddit
import praw

#for alpaca
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from django.utils.dateparse import parse_datetime
from datetime import datetime, timedelta
import pytz

#import config for api keys
from decouple import config

#import models
from .models import User, FavoriteStock, ChatMessage

# Create your views here.
def index (request):
    return render(request, "index.html")

@login_required
def dashboard(request):
    return render(request, "dashboard.html")

def features(request):
    return render(request, "features.html")

def company(request):
    return render(request, "company.html")

def product(request):
    return render(request, "product.html")

def api_reddit(request):
    try:
        reddit = praw.Reddit(
            client_id=settings.CLIENT_ID,
            client_secret=settings.CLIENT_SECRET,
            user_agent='wsb-readonly-script'
        )
        subreddit = reddit.subreddit('wallstreetbets')
        top_posts = subreddit.top(time_filter='day', limit=10)

        post_list = [{
            "title": post.title,
            "url": post.url,
            "score": post.score
        } for post in top_posts]

        return JsonResponse({"success": True, "news": post_list}, status=200)

    except Exception as e:
        print(f"Reddit API error: {e}")
        return JsonResponse({"success": False, "error": "Failed to fetch Reddit data."}, status=500)

def api_alpaca(request):
    try:
        symbol = request.GET.get("symbol", "GLD").upper()
        start_str = request.GET.get("start")
        end_str = request.GET.get("end")

        print(f"Received symbol={symbol}, start={start_str}, end={end_str}")

        # Convert start and end to datetime, remove timezone if needed
        start = parse_datetime(start_str) if start_str else datetime.now() - timedelta(days=30)
        end = parse_datetime(end_str) if end_str else datetime.now()

        if start is None or end is None:
            return JsonResponse({"success": False, "error": "Invalid start or end date format."}, status=400)

        # Remove timezone if present (for Alpaca API)
        if start.tzinfo:
            start = start.astimezone(pytz.UTC).replace(tzinfo=None)
        if end.tzinfo:
            end = end.astimezone(pytz.UTC).replace(tzinfo=None)

        client = StockHistoricalDataClient(settings.API_KEY, settings.SECRET_KEY)
        stock_params = StockBarsRequest(
            symbol_or_symbols=[symbol],
            timeframe=TimeFrame.Day,
            start=start,
            end=end
        )
        bars = client.get_stock_bars(stock_params)
        stock_bars = bars[symbol]  # <- Fix here

        if not stock_bars:
            return JsonResponse({"success": False, "error": "No data found for symbol."}, status=404)

        serialized_bars = [{
            "timestamp": bar.timestamp.isoformat(),
            "open": bar.open,
            "high": bar.high,
            "low": bar.low,
            "close": bar.close,
            "volume": bar.volume,
            "vwap": bar.vwap,
            "trade_count": bar.trade_count
        } for bar in stock_bars]

        return JsonResponse({"success": True, "news": serialized_bars}, status=200)

    except Exception as e:
        print(f"Alpaca API error: {e}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)

@csrf_exempt
def toggle_favorite_stock(request):
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "message": "You must be logged in."}, status=401)

    if request.method == "PUT":
        data = json.loads(request.body)
        symbol = data.get("symbol", "").upper()

        if not symbol:
            return JsonResponse({"success": False, "message": "Symbol required."}, status=400)

        favorite, created = FavoriteStock.objects.get_or_create(user=request.user, symbol=symbol)

        if not created:
            favorite.delete()
            return JsonResponse({"success": True, "favorited": False})
        else:
            return JsonResponse({"success": True, "favorited": True})

    return JsonResponse({"success": False, "message": "Invalid method."}, status=405)

@require_GET
def check_favorite_status(request):
    if not request.user.is_authenticated:
        return JsonResponse({"favorited": False})

    symbol = request.GET.get("symbol", "").upper()
    favorited = FavoriteStock.objects.filter(user=request.user, symbol=symbol).exists()
    return JsonResponse({"favorited": favorited})

@login_required
def favorites(request):
    return render(request, "favorites.html")

@login_required
def favorites_data(request):
    try:
        end = datetime.now() - timedelta(days=1)  # Avoid recent SIP data
        start = end - timedelta(days=40)

        # Normalize timezone
        if start.tzinfo:
            start = start.astimezone(pytz.UTC).replace(tzinfo=None)
        if end.tzinfo:
            end = end.astimezone(pytz.UTC).replace(tzinfo=None)

        # Get user's favorite stock symbols
        favorites = FavoriteStock.objects.filter(user=request.user).values_list('symbol', flat=True)
        client = StockHistoricalDataClient(settings.API_KEY, settings.SECRET_KEY)

        all_data = {}

        for symbol in favorites:
            stock_params = StockBarsRequest(
                symbol_or_symbols=[symbol],
                timeframe=TimeFrame.Day,
                start=start,
                end=end
            )

            try:
                bars = client.get_stock_bars(stock_params)
                symbol_bars = bars[symbol]

                if not symbol_bars:
                    continue

                serialized = [{
                    "timestamp": bar.timestamp.isoformat(),
                    "open": bar.open,
                    "high": bar.high,
                    "low": bar.low,
                    "close": bar.close,
                    "volume": bar.volume,
                    "vwap": bar.vwap,
                    "trade_count": bar.trade_count
                } for bar in symbol_bars]

                all_data[symbol] = serialized

            except Exception as e:
                print(f"Error retrieving data for {symbol}: {e}")
                continue

        return JsonResponse({"success": True, "data": all_data}, status=200)

    except Exception as e:
        print(f"favorites_data error: {e}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)
    
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

@login_required
def chatroom(request):
    return render(request, "chatroom.html")

@login_required
@require_POST
def send_message(request):
    msg_text = request.POST.get("message", "").strip()
    if msg_text:
        msg = ChatMessage.objects.create(user=request.user, message=msg_text)
        return JsonResponse({
            "success": True,
            "user": msg.user.username,
            "message": msg.message,
            "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        })
    return JsonResponse({"success": False, "error": "Empty message"})

@login_required
def get_messages(request):
    # Return last 50 messages in chronological order
    messages = ChatMessage.objects.select_related("user").order_by("-timestamp")[:50]
    messages = reversed(messages)  # oldest first

    data = [{
        "user": msg.user.username,
        "message": msg.message,
        "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    } for msg in messages]

    return JsonResponse({"messages": list(data)})