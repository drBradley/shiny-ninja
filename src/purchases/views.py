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


@login_required
def new_purchase_price(request):

    ctx = csrf(request)

    ctx['product'] = Product.objects.get(
        id=request.POST['product_id'])

    ctx['shop'] = Shop.objects.get(
        id=request.POST['shop_id'])

    ctx['price'] = ctx['product'].current_price(
        ctx['shop'])

    ctx['currencies'] = Currency.objects.all()

    return render_to_response(
        'purchases/new_purchase_price_form.html',
        ctx)
