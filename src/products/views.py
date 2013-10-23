# -*- coding: utf-8 -*-

from decimal import Decimal

from django.core.context_processors import csrf
from django.shortcuts import render_to_response

from products.models import Shop, Currency, Product, Section


def add_shop(request):

    if request.method == 'GET':

        return display_add_shop_form(request)

    elif request.method == 'POST':

        return handle_add_shop_form(request)


def display_add_shop_form(request):

    return render_to_response(
        'products/add_shop_form.html',
        csrf(request))


def handle_add_shop_form(request):

    shop = Shop(
        name=request.POST['shop_name'],
        description=request.POST['shop_description'])

    shop.full_clean()
    shop.save()

    return render_to_response(
        'products/shop_added.html',
        {'new_shop': shop})


def list_shops(request):

    return render_to_response(
        'products/list_shops.html',
        {'shops': Shop.objects.order_by('name')})


def show_shop(request, shop_id):

    return render_to_response(
        'products/show_shop.html',
        {'shop': Shop.objects.get(id=shop_id)})


def add_product(request, shop_id):

    if request.method == 'GET':

        return display_add_product_form(request, shop_id)

    elif request.method == 'POST':

        return handle_add_product_form(request, shop_id)


def display_add_product_form(request, shop_id):

    ctx = csrf(request)
    ctx["shop_id"] = shop_id
    ctx["currencies"] = Currency.objects.order_by("code")
    ctx['sections'] = Section.objects.order_by("name")

    return render_to_response(
        'products/add_product_form.html',
        ctx)

def handle_add_product_form(request, shop_id):

    section = Section.objects.get(
        id=request.POST['product_section'])

    product = Product(
        name=request.POST['product_name'],
        section=section,
        description=request.POST['product_description'])

    product.full_clean()
    product.save()

    currency = Currency.objects.get(
        id=request.POST['product_price_currency'])

    value = Decimal(request.POST['product_price'])

    shop = Shop.objects.get(id=shop_id)

    product.change_current_price(shop, value, currency)

    return render_to_response(
        'products/product_added.html',
        {'product': product,
         'shop': shop_id})


def show_product(request, product_id):

    return render_to_response(
        'products/show_product.html',
        {'product': Product.objects.get(
            id=product_id)})


def list_products(request):

    return render_to_response(
        'products/list_products.html',
        {'products': Product.objects.order_by('name')})
