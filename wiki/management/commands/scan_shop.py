#coding=utf8
from django.core.management.base import BaseCommand, CommandError
from wiki.models import Shop, ShopHasProduct
from lib.parser import ProductParser

class Command(BaseCommand):
    help = u'Scan products in shop'

    def add_arguments(self, parser):
        parser.add_argument('shop_id', type=int)

    def handle(self, *args, **options):
        try:
            shop = Shop.objects.get(id=options['shop_id'])
            parser = ProductParser(shop.site, shop.get_selectors())

        except Exception as e:
            self.stdout.write(u'Shop not found: %s' % str(e))
            return

        shop.scanning = True
        shop.save()

        products, keys, urls = parser.scan(shop.get_excludes())
        self.stdout.write('Finded %d products' % len(products))
        for p in products:
            print p 
            v = ShopHasProduct()
            v.shop = shop
            v.url = p['url']
            v.name = p['name']
            v.price = p['price']
            v.image = p['image']
            v.available = p['available']
            v.brand_str = p['brand']
            v.category_str = p['category']
            v.save()

        shop.scanning = False
        shop.save()
        