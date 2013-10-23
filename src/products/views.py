# -*- coding: utf-8 -*-

from django.core.context_processors import csrf
from django.shortcuts import render_to_response

from products.models import Shop


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
