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

    def benefits(self):

        return Benefit.objects.filter(
            purchase=self)

    def add_benefit(self, who):

        Benefit.objects.create(
            purchase=self,
            beneficiary=who)

    
class Benefit(models.Model):

    purchase = models.ForeignKey(Purchase)
    beneficiary = models.ForeignKey(User)
    paid_off = models.BooleanField(default=False)

    def __unicode__(self):

        return (('*unpaid* ' if not self.paid_off else '') +
                "%s uses %s bought by %s on %s" % (
                    self.beneficiary,
                    self.purchase.product_price.product.name,
                    self.purchase.payer,
                    self.purchase.date))


class Balance(models.Model):

    first_user = models.ForeignKey(User)
    second_user = models.ForeignKey(User)

    first_owes_second = models.DecimalField(
        default=0, max_digits=5, decimal_places=2)

    second_owes_first = models.DecimalField(
        default=0, max_digits=5, decimal_places=2)

    @classmethod
    def balances_of(cls, user):

        return (cls.objects.filter(
            first_user=user) +
                cls.objetcs.filter(
                    second_user=user.exclude(first_user=user)))

    @classmethod
    def balance_between(cls, one, another):

        if one.id > another.id:

            one, another = another, one

        if cls.objects.filter(
                first_user=one,
                second_user=another).count() == 1:

            return cls.objects.get(
                first_user=one,
                second_user=another)

        return cls.objects.create(
            first_user=one,
            second_user=another)
