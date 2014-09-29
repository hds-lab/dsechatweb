from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView
from django.contrib.auth import views as auth_views
from django.core.urlresolvers import reverse_lazy
import views
import auth_cbv

urlpatterns = patterns('',

                       # User profile
                       url(r'^profile/$',
                           views.UserProfileView.as_view(),
                           name='profile'),

                        url(r'^update/$',
                            views.UserProfileUpdateView.as_view(),
                            name='profile_update'),

                       # Registration urls
                       url(r'^register/$',
                           views.UserRegistrationView.as_view(),
                           name='registration_register'),
                       url(r'^register/closed/$',
                           TemplateView.as_view(template_name='registration/registration_closed.html'),
                           name='registration_disallowed'),

                       # Authentication urls
                       url(r'^login/$',
                           auth_views.login,
                           {'template_name': 'registration/login.html'},
                           name='login'),
                       url(r'^logout/$',
                           views.LogoutView.as_view(),
                           name='logout'),
                       url(r'^password/change/$',
                           views.PasswordChangeView.as_view(),
                           name='password_change'),

                       url(r'^password/reset/$',
                           views.PasswordResetView.as_view(),
                           name='password_reset'),
                       url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$',
                           views.password_reset_confirm,
                           {'post_reset_redirect': reverse_lazy('accounts:login')},
                           name='password_reset_confirm'),
)
