from django.shortcuts import render
from django.views.generic import TemplateView


# Create your views here.
class welcomeView(TemplateView):
    template_name = 'welcome.html'

class loginView(TemplateView):
    template_name = "login.html"
