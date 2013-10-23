# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url


urlpatterns = patterns(
    'products.views',
    url(r'^shop/$', 'list_shops'),
    url(r'^shop/add/$', 'add_shop'),
    url(r'^shop/show/(\d+)/$', 'show_shop'))


