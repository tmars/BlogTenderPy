#coding=utf8

from django.contrib import admin
from django import forms
from wiki.models import Brand, Product, Shop, ShopHasProduct, Substance, Category
from lib.parser import ProductParser, parseCSV
from lib.django_object_actions import DjangoObjectActions
from django.http import HttpResponse
import re

####################
## Shop object
####################
class ShopForm(forms.ModelForm):
	csv_import = forms.FileField(label=u'Файл импорта', required=False)
	
	class Meta:
		model = Shop

	def save(self, commit=True):
		instance = super(ShopForm, self).save(commit=False)
		if commit:
		    instance.save()
		if self.cleaned_data['csv_import']:
			data = parseCSV(self.cleaned_data['csv_import'].read())
			for data in ProductParser.pack(data):
				v = ShopHasProduct()
				v.shop = instance
				v.url = data['url']
				v.name = data['name']
				v.price = data['price']
				v.image = data['image']
				v.available = data['available']
				v.additional_data = data['additional']
				v.save()
		return instance
        
class ShopAdmin(admin.ModelAdmin):
	form = ShopForm

	#def add_view(self, request, *args, **kwargs):
	#	print request.GET.keys()
	#	return super(ShopAdmin, self).add_view(request, *args, **kwargs)

admin.site.register(Shop, ShopAdmin)

####################
## ShopHasProduct object
####################
from lib.admin import NullFilterSpec

class ProductNullFilterSpec(NullFilterSpec):
    title = u'Продукт'
    parameter_name = u'product'

class ShopHasProductForm(forms.ModelForm):
	product_brand_s = forms.ChoiceField(label=u'Бренд', required=False)
	product_brand = forms.CharField(label=u'Новый бренд', required=False)
	
	product_category_s = forms.ChoiceField(label=u'Категория', required=False)
	product_category = forms.CharField(label=u'Новая категория', required=False)
	
	class Meta:
		model = ShopHasProduct
		fields = ['name','product', 'product_brand_s', 'product_brand', 'product_category_s', 'product_category',\
			'price','available','additional_data']

	def __init__(self, *args, **kwargs):
		super(ShopHasProductForm, self).__init__(*args, **kwargs)
		
		if 'instance' in kwargs:
			obj = kwargs['instance']

			# выводим возможные значения продукта
			if obj.product:
				del self.fields['product_brand_s'],self.fields['product_brand']
				del self.fields['product_category_s'],self.fields['product_category']
			else:
				ps = Product.objects.search('name', obj.name)
				self.fields['product'].help_text = ''.join(
					['<a href="javascript:django.jQuery(\'#id_product\').val(%s);">%s [%s]</a><br>' % (p.id, p.name, p.id) for p in ps]
				)

				brands, f = Brand.objects.order_by_search('name', obj.get_addit('producer'))
				self.fields['product_brand_s'].choices = [(-1,'-- создать --')] + [(p.id, p.name) for p in brands]
				self.fields['product_brand_s'].initial = brands[0].id if f else -1
				self.fields['product_brand'].initial = obj.get_addit('producer')
				
				categories, f = Category.objects.order_by_search('name', obj.get_addit('category'))
				self.fields['product_category_s'].choices = [(-1,'-- создать --')] + [(p.id, p.name) for p in categories]
				self.fields['product_category_s'].initial = categories[0].id if f else -1
				self.fields['product_category'].initial = obj.get_addit('category')
				
				help_text = '<script>\
					django.jQuery("#id_product_brand_s,#id_product_category_s").change(function(){\
						var n = django.jQuery(this).attr("name");\
						n = n.substring(0, n.length-2);\
						var obj = django.jQuery(".field-"+n);\
						if (django.jQuery(this).val() == -1) {\
							obj.show();\
						} else {\
							obj.hide();\
						}\
					})\
				</script>';

				self.fields['product_category_s'].help_text = help_text

			# выводим картинку
			#self.fields['image'].help_text = '<a target="_blank" href="%s"><img src="%s" style="max-width:200px; max-height: 200px;"></a>' % (obj.image, obj.image)
			#self.fields['url'].help_text = '<a target="_blank" href="%s">Перейти</a>' % obj.url.encode('utf8')

class ShopHasProductAdmin(admin.ModelAdmin, DjangoObjectActions):

	form = ShopHasProductForm

	list_filter = [ProductNullFilterSpec]
	objectactions = ['create_related']
	list_display = ['name', 'product', 'shop']
	
	def get_object_actions(self, request, context, **kwargs):
		#print dir(admin.ModelAdmin)
		return self.objectactions

	# создаем связанные объекты
	def create_related(self, request, obj):
		if obj.product is not None:
			return
		
		p = Product()
		p.name = obj.name
		p.image = obj.image
		p.description = obj.get_addit('description')

		prod = obj.get_addit('producer')
		if prod:
			b = Brand()
			b.name = prod
			b.save()
			p.brand = b

		cat = obj.get_addit('category')
		if cat:
			c = Category.objects.filter(name__contains=cat)
			if not c:
				c = Category()
				c.name = cat
				c.save()
			else:
				c = c[0]
			p.category = c

		p.save()

		obj.product = p
		obj.save()

	create_related.label = "Создать связанные объекты"

admin.site.register(ShopHasProduct, ShopHasProductAdmin)

####################
## Brand object
####################
admin.site.register(Brand)

####################
## Product object
####################
admin.site.register(Product)

####################
## Substance object
####################
admin.site.register(Substance)

####################
## Category object
####################
admin.site.register(Category)
