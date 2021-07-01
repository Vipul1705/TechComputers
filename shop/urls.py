from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="ShopHome"),
    path("about/", views.about, name="About Us"),
    path("products/", views.products, name="Products"),
    path("contact/", views.contact, name="Contact Us"),
    path("tracker/", views.tracker, name="Tracking Status"),
    path("search/", views.search, name="Search"),
    path("products/<int:myid>", views.productView, name="Product View"),
    path("checkout/", views.checkout, name="Checkout"),
    path("checkout/order_address", views.checkout_address, name="Checkout Address"),
    path("form1/", views.form1, name="Loginform"),
    path("form2/", views.form2, name="Registerform"),
    path("signup/", views.handleSignup, name="handleSignup"),
    path("login/", views.handleLogin, name="handleLogin"),
    path("logout/", views.handleLogout, name="handleLogout"),
    
]
