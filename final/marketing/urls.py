from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("register", views.register, name="register"),
    path("logout", views.logout_view, name="logout"),
    path("dashboard", views.dashboard, name="dashboard"),
    path("features", views.features, name="features"),
    path("company", views.company, name="company"),
    path("product", views.product, name="product"),
    path("profile", views.profile, name="profile"),
    path("favorites", views.favorites, name="favorites"),
    path("chatroom", views.chatroom, name="chatroom"),


    #API routes
    path("api_reddit", views.api_reddit, name="reddit"),
    path("api_alpaca", views.api_alpaca, name="alpaca"),
    path("toggle_favorite_stock", views.toggle_favorite_stock, name="toggle_favorite_stock"),
    path("check_favorite_status", views.check_favorite_status, name="check_favorite_status"),
    path("favorites_data", views.favorites_data, name="favorites_data"),
    path('send_message', views.send_message, name='send_message'),
    path('get_messages', views.get_messages, name='get_messages'),
]

#for image urls
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)