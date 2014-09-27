from django.conf.urls import patterns, include, url
from views import HomeView, SetupView

urlpatterns = patterns('',
                       # Examples:
                       # url(r'^$', 'dsechat.views.home', name='home'),
                       # url(r'^blog/', include('blog.urls')),

                       url(r'^$', HomeView.as_view(), name="home"),
                       url(r'^setup', SetupView.as_view(), name="setup"),
)
