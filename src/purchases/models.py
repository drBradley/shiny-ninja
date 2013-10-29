# -*- coding: utf-8 -*-

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

from products.models import Price


class Purchase(models.Model):

    amount = models.DecimalField(
        decimal_places=2,
        max_digits=5,
        default=1)
    product_price = models.ForeignKey(Price)
    payer = models.ForeignKey(User)
    date = models.DateField(
        default=timezone.now)

    def __unicode__(self):

        return "%s bought %d %s for %s on %s" % (
            self.payer,
            self.amount,
            self.product_price.product.name,
            self.product_price.value,
            self.date)


class Benefit(models.Model):

    purchase = models.ForeignKey(Purchase)
    beneficiary = models.ForeignKey(User)

    def __unicode__(self):

        return "%s uses %s bought by %s on %s" % (
            self.beneficiary,
            self.purchase.product_price.product.name,
            self.purchase.payer,
            self.purchase.date)
