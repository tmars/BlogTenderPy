#coding=utf8
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from wiki.models import Product

class Command(BaseCommand):
    help = u'Освежает макс/мин/сред цены у товаров'

    def handle(self, *args, **options):
        products = Product.objects.all()
        ind = 0;
        for product in products:
            cursor = connection.cursor()
            cursor.execute(
                'SELECT COUNT(*) count, AVG(price) avgp, MIN(price) minp,MAX(price) maxp\
                FROM wiki_shophasproduct h\
                WHERE h.product_id=%s \
                    AND h.available=1',
                [product.id]
            )
            count, avgp, minp, maxp = cursor.fetchone()
            if count > 0:
                product.avg_price = avgp
                product.min_price = minp
                product.max_price = maxp
                product.save()
            ind += 1
            
            self.stdout.write("%d/%d" % (ind, len(products)))