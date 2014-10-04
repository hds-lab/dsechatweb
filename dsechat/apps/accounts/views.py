from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.template.response import TemplateResponse
from django.views.decorators.cache import never_cache
from django.core.urlresolvers import reverse_lazy, reverse
from django.shortcuts import resolve_url
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.auth import authenticate, login
from django.views import generic
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.forms import SetPasswordForm
from django.utils.http import urlsafe_base64_decode
from registration.models import UserModel
from registration import signals
from registration.backends.simple.views import RegistrationView as SimpleRegistrationView
from django.conf import settings

from forms import UserRegistrationForm, UserProfileUpdateForm, ConsentForm
from models import User as AccountsUser
import auth_cbv


class UserRegistrationView(SimpleRegistrationView):
    form_class = UserRegistrationForm

    def register(self, request, **cleaned_data):
        username, email, password = cleaned_data['username'], cleaned_data['email'], cleaned_data['password1']
        first_name, last_name = cleaned_data['first_name'], cleaned_data['last_name']

        UserModel().objects.create_user(username, email, password,
                                        first_name=first_name, last_name=last_name)

        new_user = authenticate(username=username, password=password)
        login(request, new_user)
        signals.user_registered.send(sender=self.__class__,
                                     user=new_user,
                                     request=request)
        return new_user

    def get_success_url(self, request, user):
        return ('accounts:consent', (), {})


class UserProfileView(generic.DetailView):
    model = get_user_model()
    template_name = 'accounts/profile.html'

    def get_object(self, queryset=None):
        return self.request.user

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UserProfileView, self).dispatch(*args, **kwargs)


class UserProfileUpdateView(generic.UpdateView):
    model = UserModel()
    template_name = 'accounts/profile_update.html'
    form_class = UserProfileUpdateForm
    success_url = reverse_lazy('accounts:profile')

    def get_object(self, queryset=None):
        return self.request.user

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UserProfileUpdateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        result = super(UserProfileUpdateView, self).form_valid(form)
        messages.success(self.request, "Your profile has been updated.")
        return result


class UserConsentView(generic.UpdateView):
    model = AccountsUser
    template_name = 'accounts/consent_form.html'
    form_class = ConsentForm
    success_url = reverse_lazy('accounts:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def get(self, request, *args, **kwargs):
        # you can't use this form if you've already consented
        if self.request.user and self.request.user.is_authenticated and self.request.user.gives_consent:
            return redirect('web:consent_info')
        return super(UserConsentView, self).get(request, *args, **kwargs)


    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UserConsentView, self).dispatch(*args, **kwargs)


class PasswordChangeView(auth_cbv.PasswordChangeView):
    success_url = reverse_lazy('accounts:profile')

    def form_valid(self, form):
        result = super(PasswordChangeView, self).form_valid(form)
        update_session_auth_hash(self.request, form.user)
        messages.success(self.request, "Your password has been changed.")
        return result


class LogoutView(auth_cbv.LogoutView):
    def get_success_url(self):
        return reverse('accounts:login')

    def get(self, request, *args, **kwargs):
        messages.success(self.request, "You have been signed out.")
        return super(LogoutView, self).get(request, *args, **kwargs)


class PasswordResetView(auth_cbv.PasswordResetView):
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        response = super(PasswordResetView, self).form_valid(form)
        messages.success(self.request, "An email has been sent with a link to choose a new password.")
        return response


# Doesn't need csrf_protect since no-one can guess the URL
@sensitive_post_parameters()
@never_cache
def password_reset_confirm(request, uidb64=None, token=None,
                           template_name='registration/password_reset_confirm.html',
                           token_generator=default_token_generator,
                           set_password_form=SetPasswordForm,
                           post_reset_redirect=None,
                           current_app=None, extra_context=None):
    """
    View that checks the hash in a password reset link and presents a
    form for entering a new password.
    """
    UserModel = get_user_model()
    assert uidb64 is not None and token is not None  # checked by URLconf
    if post_reset_redirect is None:
        post_reset_redirect = reverse('password_reset_complete')
    else:
        post_reset_redirect = resolve_url(post_reset_redirect)
    try:
        uid = urlsafe_base64_decode(uidb64)
        user = UserModel._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None

    if user is not None and token_generator.check_token(user, token):
        validlink = True
        title = _('Enter new password')
        if request.method == 'POST':
            form = set_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Your password has been changed. Please log in.")
                return HttpResponseRedirect(post_reset_redirect)
        else:
            form = set_password_form(user)
    else:
        validlink = False
        form = None
        title = _('Password reset unsuccessful')
    context = {
        'form': form,
        'title': title,
        'validlink': validlink,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)
