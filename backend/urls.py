from django.urls import path

from . import views

urlpatterns = [
    path("", views.login, name="login"),
    path("auth", views.auth, name="auth"),
    path("select", views.select, name = "select"),
    path("success", views.success, name = "success")
]