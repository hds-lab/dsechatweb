from django.contrib import admin
from models import User
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _
from django import forms

class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # You cannot change your email to another user's email
        if email and User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(_('A user with that email address already exists.'))
        else:
            return email

    def clean(self):
        over18 = self.cleaned_data.get('over18')
        gives_consent = self.cleaned_data.get('gives_consent')
        if gives_consent and not over18:
            raise forms.ValidationError(_('You must be at least 18 years old to participate in the research.'))
        return self.cleaned_data


class MyUserAdmin(UserAdmin):
    form = MyUserChangeForm

    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('over18', 'gives_consent',)}),
    )

admin.site.register(User, MyUserAdmin)
