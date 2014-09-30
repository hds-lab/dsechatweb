from django import forms
from django.utils.translation import ugettext_lazy as _
from registration.models import UserModel
from models import User as AccountsUser


class UserRegistrationForm(forms.Form):
    """
    Form for registering a new user account.

    Validates that the requested username is not already in use, and
    requires the password to be entered twice to catch typos.

    Subclasses should feel free to add any additional validation they
    need, but should avoid defining a ``save()`` method -- the actual
    saving of collected user data is delegated to the active
    registration backend.
    """
    required_css_class = 'required'

    username = forms.RegexField(regex=r'^[\w.@+-]+$',
                                max_length=30,
                                label=_("Create a username"),
                                error_messages={'invalid': _(
                                    "Your username may contain only letters, numbers and @/./+/-/_ characters.")})
    email = forms.EmailField(label=_("Your email address"))

    first_name = forms.CharField(label=_("First Name"))
    last_name = forms.CharField(label=_("Last Name"))

    password1 = forms.CharField(widget=forms.PasswordInput,
                                label=_("Create a password"))
    password2 = forms.CharField(widget=forms.PasswordInput,
                                label=_("Your password again"))

    def clean_username(self):
        """
        Validate that the username is alphanumeric and is not already
        in use.

        """
        existing = UserModel().objects.filter(username__iexact=self.cleaned_data['username'])
        if existing.exists():
            raise forms.ValidationError(_("A user with that username already exists."))
        else:
            return self.cleaned_data['username']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and UserModel().objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(_('A user with that email address already exists.'))
        else:
            return email

    def clean(self):
        """
        Verifiy that the values entered into the two password fields
        match. Note that an error here will end up in
        ``non_field_errors()`` because it doesn't apply to a single
        field.

        """
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_("The two password fields didn't match."))
        return self.cleaned_data


class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserModel()
        fields = ['email', 'first_name', 'last_name']

    required_css_class = 'required'

    email = forms.EmailField(label=_("Your email address"))

    first_name = forms.CharField(label=_("First Name"))
    last_name = forms.CharField(label=_("Last Name"))

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # You cannot change your email to another user's email
        if email and UserModel().objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(_('A user with that email address already exists.'))
        else:
            return email


class ConsentForm(forms.ModelForm):
    class Meta:
        model = AccountsUser
        fields = ['gives_consent', 'over18']

    required_css_class = 'required'

    gives_consent = forms.BooleanField(label=_("I agree to participate in the research"),
                                       required=False)

    over18 = forms.BooleanField(label=_("I am 18 years of age or older"),
                                required=False)

    def clean(self):
        over18 = self.cleaned_data.get('over18')
        gives_consent = self.cleaned_data.get('gives_consent')
        if gives_consent and not over18:
            raise forms.ValidationError(_('You must be at least 18 years old to participate in the research.'))
        return self.cleaned_data
