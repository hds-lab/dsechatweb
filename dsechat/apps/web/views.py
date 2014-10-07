from django.shortcuts import render
from django.views.generic import TemplateView
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

# Create your views here.

class HomeView(TemplateView):
    template_name = "web/home.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['contact_email'] = settings.SITE_CONTACT_EMAIL
        return context


class SetupView(TemplateView):
    template_name = "web/setup.html"

    def get_context_data(self, **kwargs):
        context = super(SetupView, self).get_context_data(**kwargs)
        context['xmpp_server'] = settings.XMPP_SERVER
        context['xmpp_server_port'] = settings.XMPP_SERVER_PORT
        context['xmpp_muc_room'] = settings.XMPP_MUC_ROOM
        context['xmpp_muc_server'] = settings.XMPP_MUC_SERVER
        return context


class RegisterView(TemplateView):
    template_name = "web/signup.html"


class ChatView(TemplateView):
    template_name = "web/chat.html"

    def get_context_data(self, **kwargs):
        context = super(ChatView, self).get_context_data(**kwargs)
        context['xmpp_server'] = settings.XMPP_SERVER
        context['xmpp_bosh_url'] = settings.XMPP_BOSH_URL
        context['session_cookie_name'] = settings.SESSION_COOKIE_NAME
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ChatView, self).dispatch(*args, **kwargs)

class ConsentInfoView(TemplateView):
    template_name = 'web/consent_page.html'


class ContactView(TemplateView):
    template_name = "web/contact.html"

    def get_context_data(self, **kwargs):
        context = super(ContactView, self).get_context_data(**kwargs)
        context['study_contact_name'] = settings.STUDY_CONTACT_NAME
        context['study_contact_email'] = settings.STUDY_CONTACT_EMAIL
        context['site_contact_email'] = settings.SITE_CONTACT_EMAIL
        return context


class ResearchView(TemplateView):
    template_name = "web/research.html"
