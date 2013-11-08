# -*- coding: utf-8 -*-

from django.contrib import admin

from purchases.models import Purchase, Benefit, Balance


admin.site.register(Purchase)
admin.site.register(Benefit)
admin.site.register(Balance)
