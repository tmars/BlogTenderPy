from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^shop/$', 'wiki.views.shop_list', name='shop_list'),
    url(r'^category/$', 'wiki.views.category_list', name='category_list'),
    url(r'^category/(?P<id>\d+)/$', 'wiki.views.category', name='category'),
    url(r'^product/(?P<id>\d+)/$', 'wiki.views.product', name='product'),
)
