# -*- coding: utf-8 -*-

from decimal import Decimal

from django.core.context_processors import csrf
from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

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


@login_required
def handle_new_purchase(request):

    product = Product.objects.get(
        id=request.POST['product_id'])

    shop = Shop.objects.get(
        id=request.POST['shop_id'])

    currency = Currency.objects.get(
        id=request.POST['price_currency'])

    # Qucik and dirty fix to accept commas in place of periods.
    value = Decimal(
        request.POST['price_value'].replace(
            ',', '.'))

    price = product.current_price(shop)

    if ((not price) or price.currency.id != currency.id or
            price.value != value):

        product.change_current_price(
            shop, value, currency)

        price = product.current_price(shop)

    purchase = Purchase.objects.create(
        product_price=price,
        payer=request.user)

    return redirect(show_purchase, purchase.id)


def show_purchase(request, purchase_id):

    purchase = Purchase.objects.get(
        id=purchase_id)

    users = User.objects.all()

    return render_to_response(
        'purchases/show_purchase.html',
        {'purchase': purchase,
         'users': users})
