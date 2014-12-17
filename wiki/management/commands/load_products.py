#coding=utf8
from django.core.management.base import BaseCommand, CommandError
from wiki.models import Shop, ShopHasProduct
from lib.parser import readCSV

class Command(BaseCommand):
    help = u'Load products from csv'

    def add_arguments(self, parser):
        parser.add_argument('shop_id', type=int)
        parser.add_argument('filename', type=str)

    def handle(self, *args, **options):
        try:
            shop = Shop.objects.get(id=options['shop_id'])
        except Exception as e:
            self.stdout.write(u'Shop not found: %s' % str(e))
            return

        try:
            products = readCSV(options['filename'])
        except Exception as e:
            self.stdout.write(u'File not found: %s' % str(e))
            return

        print len(products)

        ind = 0
        errors = {}
        for p in products:
            try:
                v = ShopHasProduct()
                v.shop = shop
                v.url = p.get('url', '')
                v.name = p.get('name', '')
                v.price = float(p.get('price', ''))
                v.image = p.get('image', '')
                v.available = True if p.get('available', '') else False
                v.brand_str = p.get('brand', '')
                v.category_str = p.get('category', '')
                v.packing_str = p.get('packing', '')
                v.save()
                print ind, 'ok'
            except Exception as e:
                print ind, 'error'
                errors[ind] = str(e)
            ind += 1

        print '%d errors :' % len(errors)
        for ind,mes in errors.items():
            print ind,mes