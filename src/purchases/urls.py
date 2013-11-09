# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url


urlpatterns = patterns(
    'purchases.views',

    url(r'^summary/$', 'show_balances'),
    url(r'^purchase/(\d+)/$', 'show_purchase'),
    url(r'^purchase/new/$', 'new_purchase'),
    url(r'^purchase/new/price/$', 'new_purchase_price'),
    url(r'^purchase/(\d+)/add_beneficiary/$', 'add_beneficiary'),
    url(r'^purchase/new/handle/$', 'handle_new_purchase'))
