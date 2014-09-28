from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.

class HomeView(TemplateView):
    template_name = "web/home.html"

class SetupView(TemplateView):
    template_name = "web/setup.html"

class RegisterView(TemplateView):
    template_name = "web/signup.html"

class ChatView(TemplateView):
    template_name = "web/chat.html"
