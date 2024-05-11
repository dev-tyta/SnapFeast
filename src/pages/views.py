from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def welcomeView(request):
    return HttpResponse("Welcome to SnapFeast")

def loginView(request):
    return HttpResponse("Login Page")
