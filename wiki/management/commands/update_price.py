#coding=utf8
from django.core.management.base import BaseCommand, CommandError
from wiki.models import Shop, ShopHasProduct, ShopProductLog
from lib.parser import ProductParser
from datetime import datetime

class Command(BaseCommand):
    help = u'Update prices'

    def handle(self, *args, **options):
        shops = Shop.objects.all()
        for shop in shops:
            ps = ShopHasProduct.objects.filter(shop=shop)
            urls = [p['url'] for p in ps.values('url')]
            print urls
            parser = ProductParser(shop.site, shop.get_selectors())
            info_list = parser.update(urls)
            for p in ps:
                if p.url in info_list:
                    t = info_list[p.url]
                    
                    p.price = t['price']
                    p.available = t['available']
                    p.save()

                    l = ShopProductLog()
                    l.shop_has_product = p
                    l.price = t['price']
                    l.available = t['available']
                    l.update = datetime.now()
                    l.save()