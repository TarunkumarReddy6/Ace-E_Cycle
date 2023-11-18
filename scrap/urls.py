"""scrap URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from scrapweb.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',index),
    path('index',index),
    path('logout',logout),
    path('login',login),
    path('login_check',login_check),
    path('register',register),
    path('register_check',register_check),
    path('shop',shop),
    path('shop-single',shopsingle),
    path('newauction',newauction),
    path('auction',auction),
    path('about',about),
    path('contact',contact),
    path('sell',sell),
    path('cart',cart),
    path('profile',profile),
    path('profile_edit',profile_edit),
    path('signinup',signinup),
    path('save_product',add_product),
    path('add_cart',add_cart),
    path('remove_cart',remove_cart),
    path('payment',payment),
    path('remove_product',remove_product),
    path('remove_auction',remove_auction),
    path('save_auction',add_auction),
    path('admin_dashboard',admin_dashboard),
    path('productset',productset),
    path('auctionset',auctionset),
    path('accept_product',accept_product),
    path('media/<str:filename>/', serve_image),
    path('recovery', pass_recovery),
    path('live_auction', live_auction),
    path('stop_auction', stop_auction),
    path('bid_data', bid_data),



    # path('api/upcoming_auctions/',upcoming_auctions),







    
]
