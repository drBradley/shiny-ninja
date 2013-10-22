from django.contrib import admin

from products.models import Section, Product, Shop, Currency, Price


admin.site.register(Section)
admin.site.register(Product)
admin.site.register(Shop)
admin.site.register(Currency)
admin.site.register(Price)
