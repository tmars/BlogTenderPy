from django.db import models
import json, re, operator
from lib.mptt.models import MPTTModel, TreeForeignKey

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
        return sorted(self.all(), key=lambda p: counts[p.id] if p.id in counts else 0, reverse=True), len(counts.keys()) > 0

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

class ShopHasProduct(models.Model):
    product = models.ForeignKey(Product, blank=True, null=True)
    shop = models.ForeignKey(Shop)
    
    url = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    name = models.CharField(max_length=200)
    image = models.CharField(max_length=200, blank=True, null=True)
    available = models.NullBooleanField()
    additional_data = models.TextField(blank=True, null=True)
    verified = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def get_addit(self, key):
        try:
            data = json.loads(self.additional_data)
            if data and key in data:
                return data[key]
        except:
            pass
        return ''

class Substance(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name
