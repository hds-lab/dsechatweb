from django.contrib import messages

from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.auth import authenticate, login
from django.views.generic import DetailView, FormView
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from registration.models import UserModel
from registration import signals
from registration.backends.simple.views import RegistrationView as SimpleRegistrationView

from forms import UserRegistrationForm


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
        return ('profile', (user), {})


class UserProfileView(DetailView):
    model = get_user_model()
    slug_field = 'username'
    template_name = 'accounts/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UserProfileView, self).dispatch(*args, **kwargs)


class PasswordChangeView(FormView):
    template_name = 'registration/password_change_form.html'
    form_class = PasswordChangeForm
    success_url = reverse_lazy('accounts:profile')

    @method_decorator(sensitive_post_parameters())
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(PasswordChangeView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(PasswordChangeView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        update_session_auth_hash(self.request, form.user)
        messages.success(self.request, "Your password has been changed.")
        return super(PasswordChangeView, self).form_valid(form)
