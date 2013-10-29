# -*- coding: utf-8 -*-

from decimal import Decimal

from django.core.context_processors import csrf
from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import login_required

from products.models import Product, Shop, Price, Currency

from purchases.models import Purchase


@login_required
def new_purchase(request):

    ctx = csrf(request)

    ctx['products'] = Product.objects.all()

    ctx['shops'] = Shop.objects.all()

    return render_to_response(
        'purchases/new_purchase_form.html',
        ctx)
