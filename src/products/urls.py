# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url


urlpatterns = patterns(
    'products.views',
    url(r'^shop/$', 'list_shops'),
    url(r'^shop/add/$', 'add_shop'),
    url(r'^shop/show/(\d+)/$', 'show_shop'),

    url(r'^product/$', 'list_products'),
    url(r'^product/add/(\d+)/$', 'add_product'),
    url(r'^product/show/(\d+)/$', 'show_product'),

    url(r'^change_price/$', 'change_price'))
