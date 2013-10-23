from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

import products.urls

urlpatterns = patterns(
    '',
    url(r'^products/', include(products.urls)),
    url(r'^admin/', include(admin.site.urls)))
