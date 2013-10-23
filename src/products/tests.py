# -*- coding: utf-8 -*-

import datetime
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError

from products.models import Shop, Section, Currency, Price, Product


def get_id(obj):

    return obj.id


class OurCase(TestCase):

    def assertPricesetEqual(self, one, two):

        self.assertQuerysetEqual(
            one, map(get_id, two),
            transform=get_id, ordered=False)


class ProductModelPriceAtTest(OurCase):

    def test_is_none_when_no_prices_exist_for_shop(self):

        section = Section.objects.create(
            name="Some section",
            description="")
        shop = Shop.objects.create(
            name="Some shop",
            description="")
        product = Product.objects.create(
            name="Some product",
            description="",
            section=section)

        price = product.price_at(
            shop, timezone.now())

        self.assertEqual(price, None)

    def test_when_one_price_for_shop_and_product_exists(self):

        section = Section.objects.create(
            name="Some section",
            description="")
        shop = Shop.objects.create(
            name="Some shop",
            description="")
        product = Product.objects.create(
            name="Some product",
            description="",
            section=section)
        euro = Currency.objects.create(
            name='Euro',
            code='EUR',
            symbol='€')

        price_value = Decimal("1.0")

        Price.objects.create(
            value=price_value,
            currency=euro,
            shop=shop,
            product=product)

        price = product.price_at(
            shop, timezone.now())

        self.assertEqual(type(price.value), Decimal)

        self.assertEqual(price.value, price_value)

    def test_with_time_varying_price(self):

        section = Section.objects.create(
            name="Some section",
            description="")
        shop = Shop.objects.create(
            name="Some shop",
            description="")
        product = Product.objects.create(
            name="Some product",
            description="",
            section=section)
        euro = Currency.objects.create(
            name='Euro',
            code='EUR',
            symbol='€')

        price_value = Decimal("1.0")
        now = timezone.now()

        past = Price.objects.create(
            value=price_value, currency=euro,
            shop=shop, product=product,
            since=now - datetime.timedelta(days=2))

        current = Price.objects.create(
            value=price_value, currency=euro,
            shop=shop, product=product,
            since=now - datetime.timedelta(days=1))

        future = Price.objects.create(
            value=price_value, currency=euro,
            shop=shop, product=product,
            since=now + datetime.timedelta(days=1))

        self.assertEqual(
                past.id,
                product.price_at(
                    shop, now - datetime.timedelta(2)).id)

        self.assertEqual(
                current.id,
                product.price_at(
                    shop, now - datetime.timedelta(1)).id)

        self.assertEqual(
                future.id,
                product.price_at(
                    shop, now + datetime.timedelta(1)).id)

    def test_with_many_products(self):

        section = Section.objects.create(
            name="Some section",
            description="")

        shop = Shop.objects.create(
            name="Some shop",
            description="")

        euro = Currency.objects.create(
            name='Euro',
            code='EUR',
            symbol='€')

        apples = Product.objects.create(
            name="Apples",
            description="",
            section=section)

        oranges = Product.objects.create(
            name="Oranges",
            description="",
            section=section)

        price_value = Decimal("1.0")

        now = timezone.now()

        apples.change_current_price(
            shop, price_value, euro)

        oranges.change_current_price(
            shop, price_value, euro)

        self.assertEqual(
            apples,
            apples.price_at(shop, now).product)

        self.assertEqual(
            oranges,
            oranges.price_at(shop, now).product)


class ProductModelMinPriceAtTest(OurCase):

    def test_for_product_without_price(self):

        section = Section.objects.create(
            name="Some section",
            description="")
        shop = Shop.objects.create(
            name="Some shop",
            description="")
        product = Product.objects.create(
            name="Some product",
            description="",
            section=section)

        self.assertPricesetEqual(
            product.min_price_at(
                timezone.now()),
            [])

    def test_for_product_with_one_price(self):

        section = Section.objects.create(
            name="Some section",
            description="")
        shop = Shop.objects.create(
            name="Some shop",
            description="")
        product = Product.objects.create(
            name="Some product",
            description="",
            section=section)
        euro = Currency.objects.create(
            name='Euro',
            code='EUR',
            symbol='€')

        price_value = Decimal("1.0")
        now = timezone.now()

        current = Price.objects.create(
            value=price_value, currency=euro,
            shop=shop, product=product,
            since=now - datetime.timedelta(days=2))

        self.assertPricesetEqual(
            product.min_price_at(now),
            [current])

    def test_for_product_with_time_varying_price(self):

        section = Section.objects.create(
            name="Some section",
            description="")
        shop = Shop.objects.create(
            name="Some shop",
            description="")
        product = Product.objects.create(
            name="Some product",
            description="",
            section=section)
        euro = Currency.objects.create(
            name='Euro',
            code='EUR',
            symbol='€')

        price_value = Decimal("1.0")
        now = timezone.now()

        past = Price.objects.create(
            value=price_value, currency=euro,
            shop=shop, product=product,
            since=now - datetime.timedelta(days=3))

        current = Price.objects.create(
            value=price_value, currency=euro,
            shop=shop, product=product,
            since=now - datetime.timedelta(days=2))

        self.assertPricesetEqual(
                [past],
                product.min_price_at(now - datetime.timedelta(3)))

        self.assertPricesetEqual(
                [current],
                product.min_price_at(now - datetime.timedelta(2)))

    def test_for_product_with_many_shops_having_one_price(self):

        section = Section.objects.create(
            name="Some section",
            description="")
        shop = Shop.objects.create(
            name="Some shop",
            description="")
        other_shop = Shop.objects.create(
            name="Some other shop",
            description="")
        product = Product.objects.create(
            name="Some product",
            description="",
            section=section)
        euro = Currency.objects.create(
            name='Euro',
            code='EUR',
            symbol='€')

        now = timezone.now()

        current = Price.objects.create(
            value=Decimal("1.0"), currency=euro,
            shop=shop, product=product,
            since=now - datetime.timedelta(days=2))

        Price.objects.create(
            value=Decimal("2.0"), currency=euro,
            shop=other_shop, product=product,
            since=now - datetime.timedelta(days=2))

        self.assertPricesetEqual(
            product.min_price_at(now),
            [current])

    def test_for_product_with_equal_prices_in_different_shops(self):

        section = Section.objects.create(
            name="Some section",
            description="")
        shop = Shop.objects.create(
            name="Some shop",
            description="")
        other_shop = Shop.objects.create(
            name="Some other shop",
            description="")
        last_shop = Shop.objects.create(
            name="Some last shop",
            description="")
        product = Product.objects.create(
            name="Some product",
            description="",
            section=section)
        euro = Currency.objects.create(
            name='Euro',
            code='EUR',
            symbol='€')

        now = timezone.now()
        before = now - datetime.timedelta(4)

        past = []

        Price.objects.create(
            value=Decimal("2.0"), currency=euro,
            shop=shop, product=product,
            since=before)

        past.append(
            Price.objects.create(
                value=Decimal("1.0"), currency=euro,
                shop=other_shop, product=product,
                since=before))

        past.append(
            Price.objects.create(
                value=Decimal("1.0"), currency=euro,
                shop=last_shop, product=product,
                since=before))

        self.assertPricesetEqual(
            product.min_price_at(before), past)

        current = []

        current.append(
            Price.objects.create(
                value=Decimal("1.0"), currency=euro,
                shop=shop, product=product,
                since=now - datetime.timedelta(days=2)))

        current.append(
            Price.objects.create(
                value=Decimal("1.0"), currency=euro,
                shop=other_shop, product=product,
                since=now - datetime.timedelta(days=2)))

        Price.objects.create(
            value=Decimal("2.0"), currency=euro,
            shop=last_shop, product=product,
            since=now - datetime.timedelta(days=2))

        self.assertPricesetEqual(
            product.min_price_at(now), current)


class ProductModelCurrentPriceTest(OurCase):

    def test_is_none_when_no_prices_exist_for_shop(self):

        section = Section.objects.create(
            name="Some section",
            description="")
        shop = Shop.objects.create(
            name="Some shop",
            description="")
        product = Product.objects.create(
            name="Some product",
            description="",
            section=section)

        price = product.current_price(shop)

        self.assertEqual(price, None)

    def test_when_one_price_for_shop_and_product_exists(self):

        section = Section.objects.create(
            name="Some section",
            description="")
        shop = Shop.objects.create(
            name="Some shop",
            description="")
        product = Product.objects.create(
            name="Some product",
            description="",
            section=section)
        euro = Currency.objects.create(
            name='Euro',
            code='EUR',
            symbol='€')

        price_value = Decimal("1.0")

        Price.objects.create(
            value=price_value, currency=euro,
            shop=shop, product=product)

        price = product.current_price(shop)

        self.assertEqual(type(price.value), Decimal)

        self.assertEqual(price.value, price_value)

    def test_chooses_newest_price_not_in_future(self):

        section = Section.objects.create(
            name="Some section",
            description="")
        shop = Shop.objects.create(
            name="Some shop",
            description="")
        product = Product.objects.create(
            name="Some product",
            description="",
            section=section)
        euro = Currency.objects.create(
            name='Euro',
            code='EUR',
            symbol='€')

        price_value = Decimal("1.0")
        now = timezone.now()

        Price.objects.create(
            value=price_value, currency=euro,
            shop=shop, product=product,
            since=now - datetime.timedelta(days=2))

        current = Price.objects.create(
            value=price_value, currency=euro,
            shop=shop, product=product,
            since=now - datetime.timedelta(days=1))

        Price.objects.create(
            value=price_value, currency=euro,
            shop=shop, product=product,
            since=now + datetime.timedelta(days=1))

        self.assertEqual(current.id, product.current_price(shop).id)


class ProductModelMinCurrentPriceTest(OurCase):

    def test_for_product_without_price(self):

        section = Section.objects.create(
            name="Some section",
            description="")
        shop = Shop.objects.create(
            name="Some shop",
            description="")
        product = Product.objects.create(
            name="Some product",
            description="",
            section=section)

        self.assertPricesetEqual(product.min_current_price(), [])

    def test_for_product_with_one_price(self):

        section = Section.objects.create(
            name="Some section",
            description="")
        shop = Shop.objects.create(
            name="Some shop",
            description="")
        product = Product.objects.create(
            name="Some product",
            description="",
            section=section)
        euro = Currency.objects.create(
            name='Euro',
            code='EUR',
            symbol='€')

        price_value = Decimal("1.0")
        now = timezone.now()

        current = Price.objects.create(
            value=price_value, currency=euro,
            shop=shop, product=product,
            since=now - datetime.timedelta(days=2))

        self.assertPricesetEqual(product.min_current_price(), [current])

    def test_for_product_with_many_prices_in_one_shop(self):

        section = Section.objects.create(
            name="Some section",
            description="")
        shop = Shop.objects.create(
            name="Some shop",
            description="")
        product = Product.objects.create(
            name="Some product",
            description="",
            section=section)
        euro = Currency.objects.create(
            name='Euro',
            code='EUR',
            symbol='€')

        price_value = Decimal("1.0")
        now = timezone.now()

        Price.objects.create(
            value=price_value, currency=euro,
            shop=shop, product=product,
            since=now - datetime.timedelta(days=3))

        current = Price.objects.create(
            value=price_value, currency=euro,
            shop=shop, product=product,
            since=now - datetime.timedelta(days=2))

        self.assertPricesetEqual(product.min_current_price(), [current])

    def test_for_product_with_many_shops_having_one_price(self):

        section = Section.objects.create(
            name="Some section",
            description="")
        shop = Shop.objects.create(
            name="Some shop",
            description="")
        other_shop = Shop.objects.create(
            name="Some other shop",
            description="")
        product = Product.objects.create(
            name="Some product",
            description="",
            section=section)
        euro = Currency.objects.create(
            name='Euro',
            code='EUR',
            symbol='€')

        now = timezone.now()

        current = Price.objects.create(
            value=Decimal("1.0"), currency=euro,
            shop=shop, product=product,
            since=now - datetime.timedelta(days=2))

        Price.objects.create(
            value=Decimal("2.0"), currency=euro,
            shop=other_shop, product=product,
            since=now - datetime.timedelta(days=2))

        self.assertPricesetEqual(product.min_current_price(), [current])

    def test_for_product_with_equal_prices_in_different_shops(self):

        section = Section.objects.create(
            name="Some section",
            description="")
        shop = Shop.objects.create(
            name="Some shop",
            description="")
        other_shop = Shop.objects.create(
            name="Some other shop",
            description="")
        last_shop = Shop.objects.create(
            name="Some last shop",
            description="")
        product = Product.objects.create(
            name="Some product",
            description="",
            section=section)
        euro = Currency.objects.create(
            name='Euro',
            code='EUR',
            symbol='€')

        now = timezone.now()
        current = []

        current.append(
            Price.objects.create(
                value=Decimal("1.0"), currency=euro,
                shop=shop, product=product,
                since=now - datetime.timedelta(days=2)))

        current.append(
            Price.objects.create(
                value=Decimal("1.0"), currency=euro,
                shop=other_shop, product=product,
                since=now - datetime.timedelta(days=2)))

        Price.objects.create(
            value=Decimal("2.0"), currency=euro,
            shop=last_shop, product=product,
            since=now - datetime.timedelta(days=2))

        self.assertPricesetEqual(
            product.min_current_price(), current)


class ProductModelChangeCurrentPriceTest(OurCase):

    def test_for_the_first_time(self):

        section = Section.objects.create(
            name="Some section",
            description="")
        shop = Shop.objects.create(
            name="Some shop",
            description="")
        product = Product.objects.create(
            name="Some product",
            description="",
            section=section)
        euro = Currency.objects.create(
            name='Euro',
            code='EUR',
            symbol='€')

        old_price = product.current_price(shop)

        self.assertEqual(old_price, None)

        new_price_value = Decimal("1.0")

        product.change_current_price(shop, new_price_value, euro)

        new_price = product.current_price(shop)

        self.assertEqual(new_price.value, new_price_value)

    def test_to_positive_value(self):

        section = Section.objects.create(
            name="Some section",
            description="")
        shop = Shop.objects.create(
            name="Some shop",
            description="")
        product = Product.objects.create(
            name="Some product",
            description="",
            section=section)
        euro = Currency.objects.create(
            name='Euro',
            code='EUR',
            symbol='€')

        old_price_value = Decimal("2.0")
        new_price_value = Decimal("1.0")

        old_price = Price.objects.create(
            value=old_price_value, currency=euro,
            shop=shop, product=product,
            since=timezone.now() - datetime.timedelta(days=2))

        product.change_current_price(shop, new_price_value, euro)

        self.assertEqual(Price.objects.filter(
            product=product,
            shop=shop).count(), 2)

        new_price = product.current_price(shop)

        self.assertEqual(new_price.value, new_price_value)

    def test_to_negative_value(self):

        section = Section.objects.create(
            name="Some section",
            description="")
        shop = Shop.objects.create(
            name="Some shop",
            description="")
        product = Product.objects.create(
            name="Some product",
            description="",
            section=section)
        euro = Currency.objects.create(
            name='Euro',
            code='EUR',
            symbol='€')

        bad_price_value = Decimal("-1.0")

        self.assertRaisesMessage(
            ValidationError, "{'value': [u'The value must be positive']}",
            product.change_current_price, shop, bad_price_value, euro)
