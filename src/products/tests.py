import datetime
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from products.models import Shop, Section, Price, Product


def get_id(obj):

    return obj.id


class ProductModelTest(TestCase):

    def test_current_price_is_none_when_no_prices_exist_for_shop(self):

        section = Section.objects.create(name="Some section", description="")
        shop = Shop.objects.create(name="Some shop", description="")
        product = Product.objects.create(name="Some product", description="", section=section)

        price = product.current_price(shop)

        self.assertEqual(price, None)

    def test_current_price_when_one_price_for_shop_and_product_exists(self):

        section = Section.objects.create(name="Some section", description="")
        shop = Shop.objects.create(name="Some shop", description="")
        product = Product.objects.create(name="Some product", description="", section=section)
        
        price_value = Decimal("1.0")

        Price.objects.create(value=price_value, shop=shop, product=product)

        price = product.current_price(shop)
        
        self.assertEqual(type(price.value), Decimal)

        self.assertEqual(price.value, price_value)

    def test_current_price_chooses_newest_price_not_in_future(self):

        section = Section.objects.create(name="Some section", description="")
        shop = Shop.objects.create(name="Some shop", description="")
        product = Product.objects.create(name="Some product", description="", section=section)

        price_value = Decimal("1.0")
        now = timezone.now()

        Price.objects.create(
            value=price_value, shop=shop, product=product,
            since=now - datetime.timedelta(days=2))

        current = Price.objects.create(
            value=price_value, shop=shop, product=product,
            since=now - datetime.timedelta(days=1))

        Price.objects.create(
            value=price_value, shop=shop, product=product,
            since=now + datetime.timedelta(days=1))

        self.assertEqual(current.id, product.current_price(shop).id)

    def assertPricesetEqual(self, one, two):

        self.assertQuerysetEqual(one, map(get_id, two), transform=get_id, ordered=False)

    def test_min_current_price_for_product_without_price(self):

        section = Section.objects.create(name="Some section", description="")
        shop = Shop.objects.create(name="Some shop", description="")
        product = Product.objects.create(name="Some product", description="", section=section)

        self.assertPricesetEqual(product.min_current_price(), [])

    def test_min_current_price_for_product_with_one_price(self):

        section = Section.objects.create(name="Some section", description="")
        shop = Shop.objects.create(name="Some shop", description="")
        product = Product.objects.create(name="Some product", description="", section=section)

        price_value = Decimal("1.0")
        now = timezone.now()

        current = Price.objects.create(
            value=price_value, shop=shop, product=product,
            since=now - datetime.timedelta(days=2))
        
        self.assertPricesetEqual(product.min_current_price(), [current])

    def test_min_current_price_for_product_with_many_prices_in_one_shop(self):

        section = Section.objects.create(name="Some section", description="")
        shop = Shop.objects.create(name="Some shop", description="")
        product = Product.objects.create(name="Some product", description="", section=section)

        price_value = Decimal("1.0")
        now = timezone.now()

        Price.objects.create(
            value=price_value, shop=shop, product=product,
            since=now - datetime.timedelta(days=3))

        current = Price.objects.create(
            value=price_value, shop=shop, product=product,
            since=now - datetime.timedelta(days=2))

        self.assertPricesetEqual(product.min_current_price(), [current])

    def test_min_current_price_for_product_with_many_shops_having_one_price(self):

        section = Section.objects.create(name="Some section", description="")
        shop = Shop.objects.create(name="Some shop", description="")
        other_shop = Shop.objects.create(name="Some other shop", description="")
        product = Product.objects.create(name="Some product", description="", section=section)

        now = timezone.now()

        current = Price.objects.create(
            value=Decimal("1.0"), shop=shop, product=product,
            since=now - datetime.timedelta(days=2))

        Price.objects.create(
            value=Decimal("2.0"), shop=other_shop, product=product,
            since=now - datetime.timedelta(days=2))

        self.assertPricesetEqual(product.min_current_price(), [current])

    def test_min_current_price_for_product_with_equal_prices_in_different_shops(self):

        section = Section.objects.create(name="Some section", description="")
        shop = Shop.objects.create(name="Some shop", description="")
        other_shop = Shop.objects.create(name="Some other shop", description="")
        last_shop = Shop.objects.create(name="Some last shop", description="")
        product = Product.objects.create(
            name="Some product", description="", section=section)

        now = timezone.now()
        current = []

        current.append(
            Price.objects.create(
                value=Decimal("1.0"), shop=shop, product=product,
                since=now - datetime.timedelta(days=2)))

        current.append(
            Price.objects.create(
                value=Decimal("1.0"), shop=other_shop, product=product,
                since=now - datetime.timedelta(days=2)))

        Price.objects.create(
            value=Decimal("2.0"), shop=last_shop, product=product,
            since=now - datetime.timedelta(days=2))

        self.assertPricesetEqual(
            product.min_current_price(), current)
