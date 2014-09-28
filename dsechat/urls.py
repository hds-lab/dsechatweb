from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'dsechat.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^', include('dsechat.apps.web.urls', namespace='web')),
    url(r'^accounts/', include('dsechat.apps.accounts.urls', namespace='accounts')),

)
