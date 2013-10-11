from django.contrib import admin

from products.models import Section, Product, Shop, Price


admin.site.register(Section)
admin.site.register(Product)
admin.site.register(Shop)
admin.site.register(Price)
