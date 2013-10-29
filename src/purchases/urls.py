# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url


urlpatterns = patterns(
    'purchases.views',

    url(r'^purchase/new/$', 'new_purchase'))
