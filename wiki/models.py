from django.db import models
import json, re, operator
from lib.djangosphinx.models import SphinxSearch

class MyManager(models.Manager):
	def split_words(self, string):
		if string == '':
			return []
		return re.sub(r'([a-z])([A-Z])', r'\1 \2', string).lower().split(' ')

	def search(self, field, string):
		words = self.split_words(string)
		filt = field+'__icontains'
		return self.filter(
			reduce(operator.or_, (models.Q(**{filt: w}) for w in words)) 
		)

	def order_by_search(self, field, string):
		words = self.split_words(string)
		filt = field+'__icontains'
		counts = {}
		for w in words:
			for p in self.filter(**{filt: w}):
				if p.id not in counts:
					counts[p.id] = 0
				counts[p.id] += 1
		return sorted(self.all(), key=lambda p: counts[p.id] if p.id in counts else 0, reverse=True)

class Brand(models.Model):
	objects = MyManager()

	name = models.CharField(max_length=200)
	site = models.CharField(max_length=200, blank=True)
	image = models.CharField(max_length=200, blank=True)
	description = models.TextField(blank=True)
	verified = models.BooleanField(default=False)
	
	def __str__(self):
		return unicode(self)

	def __unicode__(self):
		return '#%d %s' % (self.id, self.name)

class Category(models.Model):
	objects = MyManager()
	verified = models.BooleanField(default=False)
	
	name = models.CharField(max_length=200)

	def __str__(self):
		return unicode(self)

	def __unicode__(self):
		return '#%d %s' % (self.id, self.name)

from lib.mptt.models import MPTTModel, TreeForeignKey
class CategoryGroup(MPTTModel):
	name = models.CharField(max_length=200, unique=True)
	parent = TreeForeignKey('self', null=True, blank=True, related_name='children')
	categories = models.ManyToManyField(Category)

	def __str__(self):
		return unicode(self)

	def __unicode__(self):
		return '#%d %s' % (self.id, self.name)
		

class Product(models.Model):
	objects = MyManager()

	name = models.CharField(max_length=200)
	image = models.CharField(max_length=200, blank=True)
	brand = models.ForeignKey(Brand, null=True)
	category = models.ForeignKey(Category, null=True)
	substance = models.ForeignKey('Substance', blank=True, null=True)
	description = models.TextField(blank=True, null=True)
	verified = models.BooleanField(default=False)
	packing = models.CharField(max_length=200, blank=True, null=True)

	_avg_price = models.DecimalField(db_column='avg_price',max_digits=10, 
		decimal_places=0, null=True)
	_min_price = models.DecimalField(db_column='min_price',max_digits=10, 
		decimal_places=0, null=True)
	_max_price = models.DecimalField(db_column='max_price',max_digits=10, 
		decimal_places=0, null=True)
	
	def clear_prices(self):
		self._max_price = None
		self._min_price = None
		self._avg_price = None

	def recalc_prices(self):
		shps = ShopHasProduct.objects.filter(product=self)
		prices = [shp.price for shp in shps]
		self._max_price = max(prices)
		self._min_price = min(prices)
		self._avg_price = int(round(sum(prices) / len(prices)))
		self.save()

	@property
	def min_price(self):
	    if self._min_price == None:
	    	self.recalc_prices()
	    return self._min_price

	@property
	def avg_price(self):
	    if self._avg_price == None:
	    	self.recalc_prices()
	    return self._avg_price

	@property
	def max_price(self):
	    if self._max_price == None:
	    	self.recalc_prices()
	    return self._max_price
	
	def get_data(self):
		return {
			'image': self.image,
			'name': self.name, 
			'brand': self.brand.name, 
			'category': self.category.name, 
			'packing': self.packing
		}

	def __str__(self):
		return unicode(self)
	
	def __unicode__(self):
		try:
			b = unicode(self.brand)
		except:
			b = '-'
		try:
			c = unicode(self.category)
		except:
			c = '-'	
		return "#%d %s (%s) [%s]" % (self.id, self.name, b, c)

class Shop(models.Model):
	name = models.CharField(max_length=200)
	site = models.CharField(max_length=200)
	image = models.CharField(max_length=200, blank=True)
	description = models.TextField(blank=True)
	
	def __str__(self):
		return self.name

	def __unicode__(self):
		return self.name
	
import logging

class ShopHasProductManager(MyManager):
	
	def _similars(self, data, ids, qset):
		#qset = super(ShopHasProductManager, self).get_queryset()
		logger = logging.getLogger('MYAPP')

		from lib.prodmatch import ProductMatcher
		import operator

		matcher = ProductMatcher()
		signs = matcher.get_signs(data)

		import operator
		from django.db.models import Q

		qset = qset.filter(~Q(id__in=ids))
		
		mylist = []
		for w in signs['words']:
			mylist.append(Q(name__icontains=w))
			mylist.append(Q(brand_str__icontains=w))
			mylist.append(Q(category_str__icontains=w))

		if len(mylist):
			qset = qset.filter(reduce(operator.or_, mylist))

		items = {r.id:r for r in qset}
		datas = {r.id:r.get_data() for r in qset}

		selected = matcher.matching(data, datas)
		
		return [items[i] for i in selected]

	def similars_by_set(self, shps, qset):
		keys = ['name', 'brand', 'category', 'packing']
		data = {k:'' for k in keys}
		ids = []
		for shp in shps:
			ids.append(shp.id)
			d = shp.get_data()
			for k in keys:
				data[k] += ' ' + d[k]  
		
		return self._similars(data, ids, qset)
		
	def similars_by_one(self, shp, qset):
		return self._similars(shp.get_data(), [shp.id], qset)


class ShopHasProduct(models.Model):
	objects = ShopHasProductManager()
	search = SphinxSearch(
		index='shps',
		weights={
			'title_en': 100,
			'title_ru': 100,
		}
	)

	product = models.ForeignKey(Product, blank=True, null=True)
	shop = models.ForeignKey(Shop)
	
	url = models.CharField(max_length=200)
	price = models.DecimalField(max_digits=10, decimal_places=0)
	name = models.CharField(max_length=200)
	image = models.CharField(max_length=200, blank=True, null=True)
	available = models.NullBooleanField()
	verified = models.BooleanField(default=False)
	
	brand_str = models.CharField(max_length=200, blank=True, null=True)
	category_str = models.CharField(max_length=200, blank=True, null=True)
	packing_str = models.CharField(max_length=200, blank=True, null=True)

	def __str__(self):
		return self.name

	def __unicode__(self):
		return self.name

	def get_data(self):
		return {
			'id': self.id, 
			'image': self.image, 
			'name': self.name, 
			'brand': self.brand_str, 
			'category': self.category_str, 
			'packing': self.packing_str, 
			'price': self.price, 
			'url': self.url,
			'shop': self.shop.name
		}

class ShopProductLog(models.Model):
	shop_has_product = models.ForeignKey(ShopHasProduct)
	price = models.DecimalField(max_digits=10, decimal_places=0)
	available = models.NullBooleanField()
	update = models.DateTimeField()

class Substance(models.Model):
	name = models.CharField(max_length=200)
	description = models.TextField(blank=True)

	def __str__(self):
		return self.name

	def __unicode__(self):
		return self.name
