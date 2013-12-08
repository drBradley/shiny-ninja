# -*- coding: utf-8 -*-
from decimal import Decimal

from django.db import models
from django.db.models.aggregates import Sum
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from products.models import Price, Currency


class Purchase(models.Model):

    amount = models.DecimalField(
        decimal_places=2,
        max_digits=5,
        default=1)
    product_price = models.ForeignKey(Price)
    payer = models.ForeignKey(User)
    date = models.DateField(
        default=timezone.now)
    no_debt_paid_off = models.BooleanField(default=True)

    def __unicode__(self):

        return "%s bought %d %s for %s %s on %s" % (
            self.payer,
            self.amount,
            self.product_price.product.name,
            self.product_price.value,
            self.product_price.currency.code,
            self.date)

    def benefits(self):

        return Benefit.objects.filter(
            purchase=self)

    def add_benefit(self, who, how_much):

        if self.no_debt_paid_off:

            cost = self.amount * self.product_price.value

            for benefit in self.benefit_set.all():

                balance = Balance.balance_between(
                    self.payer, benefit.beneficiary, self.product_price.currency)

                balance.charge(
                    benefit.beneficiary, -benefit.debt)

            Benefit.objects.create(
                beneficiary=who,
                purchase=self,
                share=how_much)

            share_sum = self.benefit_set.aggregate(Sum('share'))['share__sum']
            biggest_share_benefit = self.benefit_set.order_by('-share')[0]

            for benefit in self.benefit_set.order_by('share'):


                benefit.debt = cost * benefit.share / share_sum

                benefit.save()


            debt_sum = Benefit.objects.filter(purchase=self).aggregate(Sum('debt'))['debt__sum']

            rest = cost - debt_sum

            biggest_share_benefit.debt = models.F('debt') + rest
            biggest_share_benefit.save()

            for benefit in self.benefit_set.all():

                balance = Balance.balance_between(
                    self.payer,
                    benefit.beneficiary,
                    self.product_price.currency)

                balance.charge(benefit.beneficiary, benefit.debt)

    def settle_debt(self, benefit):

        if not benefit.paid_off:

            balance = Balance.balance_between(
                self.payer, benefit.beneficiary, benefit.purchase.product_price.currency)

            share_sum = Benefit.objects.filter(
                purchase=self).aggregate(models.Sum('share'))['share__sum']

            balance.charge(benefit.beneficiary, -benefit.debt)

            benefit.paid_off = True
            benefit.save()

            self.no_debt_paid_off = False
            self.save()

@receiver(pre_delete, sender=Purchase)
def fix_balance_on_deletion(instance, **kwargs):

    purchase = instance
    benefits = purchase.benefit_set.all()

    for benefit in benefits:

        balance = Balance.balance_between(purchase.payer,
                                          benefit.beneficiary)
        balance.charge(benefit.beneficiary, -benefit.debt)
        benefit.delete()


class Benefit(models.Model):

    purchase = models.ForeignKey(Purchase)
    beneficiary = models.ForeignKey(User)

    share = models.DecimalField(
        default=1, max_digits=5, decimal_places=2)
    debt = models.DecimalField(
        default=0, max_digits=5, decimal_places=2)

    paid_off = models.BooleanField(default=False)

    def __unicode__(self):

        return (('*unpaid* ' if not self.paid_off else '') +
                "%s uses %s bought by %s for %s %s on %s" % (
                    self.beneficiary,
                    self.purchase.product_price.product.name,
                    self.purchase.payer,
                    self.purchase.product_price.value * self.purchase.amount,
                    self.purchase.product_price.currency.code,
                    self.purchase.date))


class Balance(models.Model):

    currency = models.ForeignKey(Currency)

    first_user = models.ForeignKey(
        User, related_name='balances_where_first')

    second_user = models.ForeignKey(
        User, related_name='balances_where_second')

    first_owes_second = models.DecimalField(
        default=0, max_digits=5, decimal_places=2)

    second_owes_first = models.DecimalField(
        default=0, max_digits=5, decimal_places=2)

    def balance_of_first(self):

        return self.second_owes_first - self.first_owes_second

    def balance_of_second(self):

        return - self.balance_of_first()

    def __unicode__(self):

        if self.first_owes_second > self.second_owes_first:

            return '%s owes %s %.2f %s' % (
                self.first_user.username,
                self.second_user.username,
                self.first_owes_second - self.second_owes_first,
                self.currency)

        elif self.second_owes_first > self.first_owes_second:

            return '%s owes %s %.2f %s' % (
                self.second_user.username,
                self.first_user.username,
                self.second_owes_first - self.first_owes_second,
                self.currency)

        return '%s and %s are even (%s)' % (
            self.first_user.username,
            self.second_user.username,
            self.currency)

    def charge(self, who, how_much):

        if not (self.first_user == who or self.first_user.id == who or
                self.second_user == who or self.second_user.id == who):

            raise ValueError(
                "The user must be one linked to this balance")

        if self.first_user == who or self.first_user.id == who:

            self.first_owes_second += how_much

        elif self.second_user == who or self.second_user.id == who:

            self.second_owes_first += how_much

        self.save()

    @classmethod
    def affected_by(cls, purchase):

        affected = []

        for benefit in Benefit.objects.filter(purchase=purchase):

            affected.append(
                (Balance.balance_between(
                    benefit.beneficiary,
                    purchase.payer,
                    purchase.product_price.currency),
                 benefit))

        return affected


    @classmethod
    def balances_of(cls, user):

        return (cls.objects.filter(
            first_user=user) +
                cls.objetcs.filter(
                    second_user=user.exclude(first_user=user)))

    @classmethod
    def balance_between(cls, one, another, currency):

        if one.id > another.id:

            one, another = another, one

        if cls.objects.filter(
                first_user=one,
                second_user=another,
                currency=currency).count() == 1:

            return cls.objects.get(
                first_user=one,
                second_user=another,
                currency=currency)

        return cls.objects.create(
            first_user=one,
            second_user=another,
            currency=currency)
