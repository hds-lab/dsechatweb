from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView
from django.contrib.auth import views as auth_views
from django.core.urlresolvers import reverse_lazy
from views import UserRegistrationView, UserProfileView, PasswordChangeView

urlpatterns = patterns('',

                       # User profile
                       url(r'^profile/$',
                           UserProfileView.as_view(),
                           name='profile'),

                       # Registration urls
                       url(r'^register/$',
                           UserRegistrationView.as_view(),
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
                           auth_views.logout,
                           {'template_name': 'registration/logout.html'},
                           name='logout'),
                       url(r'^password/change/$',
                           PasswordChangeView.as_view(),
                           name='password_change'),

                       url(r'^password/reset/$',
                           auth_views.password_reset,
                           {'post_reset_redirect': reverse_lazy('password_reset_done')},
                           name='password_reset'),
                       url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$',
                           auth_views.password_reset_confirm,
                           {'post_reset_redirect': reverse_lazy('password_reset_complete')},
                           name='password_reset_confirm'),
                       url(r'^password/reset/complete/$',
                           auth_views.password_reset_complete,
                           name='password_reset_complete'),
                       url(r'^password/reset/done/$',
                           auth_views.password_reset_done,
                           name='password_reset_done'),
)
