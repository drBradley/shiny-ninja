from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

import products.urls
import purchases.urls

urlpatterns = patterns(
    '',
    url(r'^products/', include(products.urls)),
    url('^accounts/', include('django.contrib.auth.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^purchases/', include(purchases.urls)))
