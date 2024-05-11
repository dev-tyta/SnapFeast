from django.urls import path

from .views import welcomeView, loginView

urlpatterns = [
    path("", welcomeView, name="welcome"),
    path("login/", loginView, name="login")
]