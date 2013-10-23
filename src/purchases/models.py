# -*- coding: utf-8 -*-

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

from products.models import Price


class Purchase(models.Model):

    number = models.PositiveIntegerField(default=1)
    product_price = models.ForeignKey(Price)
    payer = models.ForeignKey(User)
    date = models.DateField(
        default=timezone.now)

    def __unicode__(self):

        return "%s bought %d %s for %s on %s" % (
            self.payer,
            self.number,
            self.product_price.product.name,
            self.product_price.value,
            self.date)
