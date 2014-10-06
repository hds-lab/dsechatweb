from django.conf.urls import patterns, include, url
import views

urlpatterns = patterns('',
                       # Examples:
                       # url(r'^$', 'dsechat.views.home', name='home'),
                       # url(r'^blog/', include('blog.urls')),

                       url(r'^$', views.HomeView.as_view(), name="home"),
                       url(r'^setup/$', views.SetupView.as_view(), name="setup"),
                       url(r'^chat/$', views.ChatView.as_view(), name="chat"),
                       url(r'^research/$', views.ResearchView.as_view(), name="research"),
                       url(r'^contact/$', views.ContactView.as_view(), name='contact'),
                       url(r'^study/info/$', views.ConsentInfoView.as_view(), name='consent_info'),
                       url(r'^setup/pidgin/$',
                           views.SetupView.as_view(template_name="web/setup/pidgin.html"),
                           name="setup_pidgin"),
                       url(r'^setup/adium/$',
                           views.SetupView.as_view(template_name="web/setup/adium.html"),
                           name="setup_adium"),
)
