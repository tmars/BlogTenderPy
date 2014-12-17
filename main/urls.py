from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'main.views.home', name='home'),
    
    url(r'^', include('wiki.urls')),
	url(r'^admin/', include(admin.site.urls)),
	url(r'^grappelli/', include('grappelli.urls')), # grappelli URLS
)
