# -*- coding: utf-8 -*-

import os.path
import datetime

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError


class Section(models.Model):

    name = models.CharField(max_length=50)
    description = models.TextField()

    def __unicode__(self):

        return self.name


class Product(models.Model):

    name = models.CharField(max_length=50)
    description = models.TextField()
    section = models.ForeignKey(Section)
    photo = models.ImageField(
        null=True,
        upload_to=os.path.join(
            settings.BASE_DIR,
            "static/images/products"))

    def __unicode__(self):

        return self.name

    def price_at(self, shop, day):

        prices = Price.objects.filter(
            product=self,
            shop=shop,
            since__lte=day).order_by('-since')

        if prices.count() == 0:

            return None

        return prices[0]

    def current_price(self, shop):

        now = timezone.now()

        return self.price_at(shop, now)

    def min_current_price(self):

        shops = Shop.objects.filter(
            price__product=self)

        min_price_value = None

        prices = []
        for shop in shops:

            price = self.current_price(shop)

            if price is not None:

                if min_price_value is None:

                    min_price_value = price.value
                    prices.append(price)

                elif price.value < min_price_value:

                    min_price_value = price.value
                    prices = [price]

                elif price.value == min_price_value:

                    prices.append(price)

        return prices

    def change_current_price(self, shop, value):

        price = Price(shop=shop, product=self, value=value)

        price.full_clean()
        price.save()


class Shop(models.Model):

    name = models.CharField(max_length=50)
    description = models.TextField()

    def __unicode__(self):

        return self.name


def positive(value):

    if not value > 0:

        raise ValidationError(
            "The value must be positive")


class Price(models.Model):

    value = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[positive])
    shop = models.ForeignKey(Shop)
    product = models.ForeignKey(Product)
    since = models.DateField(default=timezone.now)

    def __unicode__(self):

        return "%s for %s at %s since %s" % (
            self.value, self.product,
            self.shop, self.since.strftime("%Y-%m-%d"))
