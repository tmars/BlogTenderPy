#coding=utf8

import re
import sys, os

from django.contrib import admin
from django.shortcuts import render, render_to_response
from django import forms
from django.http import HttpResponse
from django.conf import settings

from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION 
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_unicode

from wiki.models import Brand, Product, Shop, ShopHasProduct, Substance, Category, CategoryGroup

from lib.django_object_actions import DjangoObjectActions
from lib.cuser.middleware import CuserMiddleware	

def log_entry_add(obj):
	log_entry_fix(obj, ADDITION)

def log_entry_change(obj):
	log_entry_fix(obj, CHANGE)
	
def log_entry_del(obj):
	log_entry_fix(obj, DELETION)

def log_entry_fix(obj, type):
	user = CuserMiddleware.get_user()
	if user:
		LogEntry.objects.log_action(
			user_id			= user.id, 
			content_type_id	= ContentType.objects.get_for_model(obj).pk,
			object_id		= obj.pk,
			object_repr		= force_unicode(obj), 
			action_flag		= type
		)

####################
## Shop object
####################
class ShopForm(forms.ModelForm):
	products_csv = forms.FileField(label=u'Товары', required=False)
	
	class Meta:
		model = Shop
		fields = ['name','site','image','description']

	def save(self, commit=True):
		instance = super(ShopForm, self).save(commit=commit)
	
		if commit:
			instance.save()

		if self.cleaned_data['products_csv'] and instance.id:
			from lib.parser import parseCSV
			products = parseCSV(self.cleaned_data['products_csv'].read())
			
			errors = {}
			ind = 0
			from django.db import IntegrityError, transaction
			for p in products:
				try:
					with transaction.atomic():
						v = ShopHasProduct()
						v.shop = instance
						v.url = p.get('url', '')
						v.name = p.get('name', '')
						v.price = float(p.get('price', ''))
						v.image = p.get('image', '')
						v.available = True if p.get('available', '') else False
						v.brand_str = p.get('brand', '')
						v.category_str = p.get('category', '')
						v.packing_str = p.get('packing', '')
						v.save()
				except Exception as e:
					errors[ind] = str(e)
				ind += 1

			import logging
			logger = logging.getLogger('MYAPP')
			
			logger.debug('shop %d' % instance.id)
			logger.debug('success: %d' % (ind-len(errors)))
			logger.debug('errors: %d' % len(errors))
			for ind,mes in errors.items():
				logger.debug("%d: %s" % (ind,products[ind]))
				logger.debug("%d: %s" % (ind,mes))
				logger.debug("---")

		return instance
	

class ShopAdmin(admin.ModelAdmin):
	form = ShopForm
	list_display = ['name']


admin.site.register(Shop, ShopAdmin)

class SimilarsField(forms.MultipleChoiceField):
	def __init__(self, *args, **kwargs):
		kwargs['required'] = False
		kwargs['widget'] = forms.CheckboxSelectMultiple
		super(SimilarsField, self).__init__(args, kwargs)
	
	def validate(self, value):
		pass

	def set_objects(self, obj, similars):
		from django.template.loader import render_to_string
		choices = [(-1, 'no')]
		items = [obj.get_data()]
		for shp in similars:
			items.append(shp.get_data())
			choices.append((shp.id, shp.name))
		self.help_text = render_to_string('admin/wiki/similars.html', {'items': items})
		self.choices = choices


####################
## ShopHasProduct object
####################
class ShopHasProductForm(forms.ModelForm):
	product_name = forms.CharField(label=u'Название продукта', required=False)
	product_brand_s = forms.ChoiceField(label=u'Бренд', required=False)
	product_brand = forms.CharField(label=u'Новый бренд', required=False)
	
	product_category_s = forms.ChoiceField(label=u'Категория', required=False)
	product_category = forms.CharField(label=u'Новая категория', required=False)
	similars = SimilarsField(label=u'Схожие товары')
	
	class Meta:
		model = ShopHasProduct
		fields = ['name','product', 'product_name', 'product_brand_s', 'product_brand', 'product_category_s', 'product_category',\
			'url', 'image','price','available', 'packing_str', 'similars']

	def __init__(self, *args, **kwargs):
		super(ShopHasProductForm, self).__init__(*args, **kwargs)
		
		if 'instance' in kwargs:
			obj = kwargs['instance']

			# выводим возможные значения продукта
			if obj.product:
				keys = ('product_name','product_brand_s','product_brand','product_category_s','product_category', 'similars')
				help_text = '<style>'
				for k in keys:
					help_text += '.field-'+k+'{display:none}'
				help_text += '</style>'
				
				self.fields['product_name'].help_text = help_text
			else:
				self.fields['product_name'].initial = obj.name

				# Выводим сходные товары
				# qset = ShopHasProduct.objects.filter(product__isnull=False)
				# similars = ShopHasProduct.objects.similars_by_one(obj, qset)
				
				# products = {}
				# prods = {}
				# for shp in similars:
				# 	if shp.product.id not in products:
				# 		products[shp.product.id] = 0
				# 		prods[shp.product.id] = shp.product
				# 	products[shp.product.id] += 1

				# import operator
				# products = sorted(products.items(), key=operator.itemgetter(1), reverse=True)

				# help_text = ''
				# for p,v in products:
				# 	help_text += unicode(prods[p]) + '<br>'
				# self.fields['product'].help_text = help_text

				# Выводим сходные товары
				qset = ShopHasProduct.objects.filter(product__isnull=True)
				similars = ShopHasProduct.objects.similars_by_one(obj, qset)
				
				self.fields['similars'].set_objects(obj, similars)
				self.fields['similars'].widget.attrs.update({'class': 'if_not_product'})

				# Выводим возможные бренды
				brands = Brand.objects.order_by_search('name', obj.brand_str)
				
				self.fields['product_brand_s'].choices = [(-1,'-- создать --')] + [(p.id, p.name) for p in brands]
				self.fields['product_brand_s'].widget.attrs.update({'class': 'select_list if_not_product'})
				
				self.fields['product_brand'].initial = obj.brand_str
				self.fields['product_brand'].widget.attrs.update({'class': 'if_not_product'})
				if len(brands) > 0 and obj.brand_str.lower() == brands[0].name.lower(): 
					self.fields['product_brand'].widget.attrs.update({'styles': 'display:none;'})
					
				# Выводим возможные категории
				categories = Category.objects.order_by_search('name', obj.category_str)
				
				self.fields['product_category_s'].choices = [(-1,'-- создать --')] + [(p.id, p.name) for p in categories]
				self.fields['product_category_s'].widget.attrs.update({'class': 'select_list if_not_product'})
				self.fields['product_category'].widget.attrs.update({'class': 'if_not_product'})

				self.fields['product_category'].initial = obj.category_str
				if len(categories) > 0 and obj.category_str.lower() == categories[0].name.lower(): 
					self.fields['product_category'].widget.attrs.update({'styles': 'display:none;'})

			# выводим картинку
			self.fields['image'].help_text = '<a target="_blank" href="%s"><img src="%s" style="max-width:200px; max-height: 200px;"></a>' % (obj.image, obj.image)
			self.fields['url'].help_text = '<a target="_blank" href="%s">Перейти</a>' % obj.url.encode('utf8')
			
	def save(self, commit=True):
		instance = super(ShopHasProductForm, self).save(commit=False)
		instance.verified = True
		if not self.cleaned_data['product']:
			p = Product()
			p.name = self.cleaned_data['product_name']
			p.image = instance.image
			#p.description = instance.get_addit('description')
			
			if self.cleaned_data['product_category_s'] == '-1':
				c = Category()
				c.name = self.cleaned_data['product_category']
				c.save()
				p.category = c
				log_entry_add(c)
				
			else:
				p.category_id = self.cleaned_data['product_category_s']
				
			if self.cleaned_data['product_brand_s'] == '-1':
				b = Brand()
				b.name = self.cleaned_data['product_brand']
				b.save()
				p.brand = b
				log_entry_add(b)
			else:
				p.brand_id = self.cleaned_data['product_brand_s']
			
			p.packing = self.cleaned_data['packing_str']

			p.save()
			instance.product = p
			log_entry_add(p)

			if len(self.cleaned_data['similars']):
				for id in self.cleaned_data['similars']:
					shp = ShopHasProduct.objects.get(id=id)
					shp.verified = True
					shp.product = p
					shp.save()
					log_entry_change(shp)

		if commit:
			instance.save()
		
		return instance
	

class ShopHasProductAdmin(admin.ModelAdmin):

	form = ShopHasProductForm
	ordering = ['verified', 'name']
	list_filter = ['product__category', 'shop']
	list_display = ['name', 'verified', 'product', 'shop']
	raw_id_fields = ('product',)
	related_lookup_fields = {
		'fk': ['product'],
	}
admin.site.register(ShopHasProduct, ShopHasProductAdmin)

####################
## Brand object
####################
class BrandForm(forms.ModelForm):
	class Meta:
		model = Brand
		fields = ['name', 'site', 'image', 'description']
		
		
	def __init__(self, *args, **kwargs):
		super(BrandForm, self).__init__(*args, **kwargs)
		
		if 'instance' in kwargs:
			obj = kwargs['instance']
			if len(obj.site):
				self.fields['site'].help_text = '<a href="%">Ссылка</a>' % (obj.site)
			self.fields['image'].help_text = '<a target="_blank" href="%s"><img src="%s" style="max-width:200px; max-height: 200px;"></a>' % \
				(obj.image, obj.image)
			self.fields['name'].help_text = '<a href="javascript:window.open(\'../../shophasproduct/?_popup=1&product__brand__id__exact='+\
				str(obj.id)+'\', \'Продукты\', \'height=500,width=800,resizable=yes,scrollbars=yes\')" target="_blank">В магазинах</a>'
			
			
	def save(self, commit=True):
		instance = super(BrandForm, self).save(commit=False)
		instance.verified = True
			
		if commit:
			instance.save()
		
		return instance
	
			
class BrandAdmin(admin.ModelAdmin):
	ordering = ['verified', 'name']
	list_display = ['name', 'verified']
	form = BrandForm
	
admin.site.register(Brand, BrandAdmin)

####################
## Product object
####################
class ProductForm(forms.ModelForm):
	similars = SimilarsField(label=u'Схожие товары')

	class Meta:
		model = Product
		fields = ['name','image','brand','category','substance','description','packing']
		
	def __init__(self, *args, **kwargs):
		super(ProductForm, self).__init__(*args, **kwargs)
		
		if 'instance' in kwargs:
			obj = kwargs['instance']
			
			self.fields['image'].help_text = '<a target="_blank" href="%s"><img src="%s" style="max-width:200px; max-height: 200px;"></a>' % \
				(obj.image, obj.image)
			self.fields['name'].help_text = '<a href="javascript:window.open(\'../../shophasproduct/?_popup=1&product__id__exact='+\
				str(obj.id)+'\', \'Продукты\', \'height=500,width=800,resizable=yes,scrollbars=yes\')" target="_blank">В магазинах</a>'
			

			# Выводим сходные товары
			from django.template.loader import render_to_string
			
			shps = ShopHasProduct.objects.filter(product=obj)
			
			ss = ShopHasProduct.objects.filter(product__isnull=True)
			similars = ShopHasProduct.objects.similars_by_set(shps, ss)

			self.fields['similars'].set_objects(obj, similars)


			
	def save(self, commit=True):
		instance = super(ProductForm, self).save(commit=False)
		instance.verified = True
			
		if len(self.cleaned_data['similars']):
			for id in self.cleaned_data['similars']:
				shp = ShopHasProduct.objects.get(id=id)
				shp.verified = True
				shp.product = instance
				shp.save()
				log_entry_change(shp)
			
			instance.clear_prices()

		if commit:
			instance.save()
		
		return instance
	
			
class ProductAdmin(admin.ModelAdmin):
	ordering = ['verified', 'name']
	list_filter = ['category', 'brand']
	list_display = ['name', 'packing', 'verified']
	form = ProductForm

admin.site.register(Product, ProductAdmin)

####################
## Substance object
####################
admin.site.register(Substance)

####################
## Category object
####################
class CategoryForm(forms.ModelForm):
	class Meta:
		model = Category
		fields = ['name']
		
	def save(self, commit=True):
		instance = super(CategoryForm, self).save(commit=False)
		instance.verified = True
			
		if commit:
			instance.save()
		
		return instance
	
	def __init__(self, *args, **kwargs):
		super(CategoryForm, self).__init__(*args, **kwargs)
		
		if 'instance' in kwargs:
			obj = kwargs['instance']
			self.fields['name'].help_text = '<a href="javascript:window.open(\'../../shophasproduct/?_popup=1&product__category__id__exact='+\
				str(obj.id)+'\', \'Продукты\', \'height=500,width=800,resizable=yes,scrollbars=yes\')" target="_blank">В магазинах</a>'
	
			
class CategoryAdmin(admin.ModelAdmin):
	ordering = ['verified', 'name']
	list_display = ['name', 'verified']
	form = CategoryForm
	
admin.site.register(Category, CategoryAdmin)

####################
## CategoryGroup object
####################
from lib.mptt.admin import MPTTModelAdmin

class CategoryGroupAdmin(MPTTModelAdmin):
	# speficfy pixel amount for this ModelAdmin only:
	mptt_level_indent = 20

admin.site.register(CategoryGroup, CategoryGroupAdmin)