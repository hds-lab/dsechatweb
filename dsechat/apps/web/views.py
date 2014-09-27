from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.

class HomeView(TemplateView):
    template_name = "web/home.html"

class SetupView(TemplateView):
    template_name = "web/setup.html"


