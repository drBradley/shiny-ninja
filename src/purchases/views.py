# -*- coding: utf-8 -*-

from decimal import Decimal

from django.core.context_processors import csrf
from django.db.models import Sum
from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from products.models import Product, Shop, Price, Currency

from purchases.models import Purchase, Benefit, Balance


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

    amount = Decimal(
        request.POST['purchased_amount'].replace(
            ',', '.'))

    price = product.current_price(shop)

    if ((not price) or price.currency.id != currency.id or
            price.value != value):

        product.change_current_price(
            shop, value, currency)

        price = product.current_price(shop)

    purchase = Purchase.objects.create(
        product_price=price,
        payer=request.user,
        amount=amount)

    return redirect(show_purchase, purchase.id)


def show_purchase(request, purchase_id):

    ctx = csrf(request)

    purchase = ctx['purchase'] = Purchase.objects.get(
        id=purchase_id)

    ctx['users'] = User.objects.all()

    ctx['benefits'] = ctx['purchase'].benefits()

    share_sum = Benefit.objects.filter(
        purchase=purchase).aggregate(Sum('share'))['share__sum']

    for benefit in ctx['benefits']:

        benefit.__dict__['template_share'] = (
            benefit.share * purchase.amount / share_sum)

    return render_to_response(
        'purchases/show_purchase.html',
        ctx)


def add_beneficiary(request, purchase_id):

    purchase = Purchase.objects.get(
        id=purchase_id)

    if not request.user.id == purchase.payer.id:

        response = render_to_response(
            'purchases/not_payer.html',
            {'purchase_id': purchase_id})

        response.status_code = 401

        return response

    user = User.objects.get(
        id=request.POST['beneficiary_id'])

    share = request.POST['share']

    purchase.add_benefit(user, share)

    return redirect(show_purchase, purchase_id)


@login_required
def show_balances(request):

    ctx = {}

    user = ctx['me'] = request.user

    own_balances = ctx['own_balances'] = (Balance.objects.
        filter(first_user=user, second_user=user))

    balances_me_first = ctx['balances_me_first'] = (Balance.objects.
        filter(first_user=user).
        exclude(second_user=user).
        order_by('second_user'))

    balances_me_second = ctx['balances_me_second'] = (Balance.objects.
        filter(second_user=user).
        exclude(first_user=user).
        order_by('first_user'))

    return render_to_response(
        'purchases/my_balance.html',
        ctx)

@login_required
def debts(request, obligor_id):

    if request.method == 'GET':

        return show_debts(request, obligor_id)

    elif request.method == 'POST':

        return settle_debts(request, obligor_id)


def show_debts(request, obligor_id):

    ctx = csrf(request)

    obligor = ctx["obligor"] = User.objects.get(id=obligor_id)

    benefits = ctx["benefits"] = Benefit.objects.filter(
        purchase__payer=request.user,
        beneficiary=obligor,
        paid_off=False)

    return render_to_response(
        "purchases/debts.html",
        ctx)


def settle_debts(request, obligor_id):

    obligor = User.objects.get(id=obligor_id)

    settled_debts = Benefit.objects.filter(
        id__in=request.POST.getlist('settled'))

    for benefit in settled_debts:

        benefit.purchase.settle_debt(benefit)

    return redirect(debts, obligor_id)

@login_required
def list_purchases(request):

    user = request.user

    purchases = Purchase.objects.filter(payer=user).order_by('date')

    return render_to_response(
        'purchases/list_purchases.html',
        {'purchases': purchases})
