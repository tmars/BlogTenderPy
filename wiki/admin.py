#coding=utf8

from django.contrib import admin
from django import forms
from wiki.models import Brand, Product, Shop, ShopHasProduct, Substance, Category, CategoryGroup
from lib.parser import ProductParser, parseCSV
from lib.django_object_actions import DjangoObjectActions
from lib.mptt.admin import MPTTModelAdmin
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
			if len(data):
				for d in ProductParser.pack(data):
					v = ShopHasProduct()
					v.shop = instance
					v.url = d['url']
					v.name = d['name']
					v.price = d['price']
					v.image = d['image']
					v.available = d['available']
					v.additional_data = d['additional']
					
					p, f = Product.objects.get_or_create(name=v.name)
					
					if f:
						bn = v.get_addit('brand')
						if len(bn):
							b, f = Brand.objects.get_or_create(name=bn)
							p.brand = b
						
						cn = v.get_addit('category')
						if len(cn):
							c, f = Category.objects.get_or_create(name=cn)
							p.category = c
						
						p.image = v.image
						p.save()
					
					v.product = p
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

class ShopHasProductForm(forms.ModelForm):
	product_name = forms.CharField(label=u'Название продукта', required=False)
	product_brand_s = forms.ChoiceField(label=u'Бренд', required=False)
	product_brand = forms.CharField(label=u'Новый бренд', required=False)
	
	product_category_s = forms.ChoiceField(label=u'Категория', required=False)
	product_category = forms.CharField(label=u'Новая категория', required=False)
	
	class Meta:
		model = ShopHasProduct
		fields = ['name','product', 'product_name', 'product_brand_s', 'product_brand', 'product_category_s', 'product_category',\
			'url', 'image','price','available','additional_data']

	def __init__(self, *args, **kwargs):
		super(ShopHasProductForm, self).__init__(*args, **kwargs)
		
		if 'instance' in kwargs:
			obj = kwargs['instance']

			# выводим возможные значения продукта
			if obj.product:
				keys = ('product_name','product_brand_s','product_brand','product_category_s','product_category')
				help_text = '<style>'
				for k in keys:
					help_text += '.field-'+k+'{display:none}'
				help_text += '</style>'
				
				self.fields['product_name'].help_text = help_text
			else:
				#ps = Product.objects.search('name', obj.name)
				#self.fields['product'].help_text = ''.join(
				#	['<a href="javascript:django.jQuery(\'#id_product\').val(%s).change();">%s</a><br>' % (p.id, unicode(p)) for p in ps]
				#)
				
				self.fields['product_name'].initial = obj.name
				
				help_text = '<style>'
				brands, f = Brand.objects.order_by_search('name', obj.get_addit('brand'))
				self.fields['product_brand_s'].choices = [(-1,'-- создать --')] + [(p.id, p.name) for p in brands]
				self.fields['product_brand_s'].initial = brands[0].id if f else -1
				self.fields['product_brand'].initial = obj.get_addit('brand')
				if f and obj.get_addit('brand').lower() == brands[0].name.lower(): help_text += '.field-product_brand {display:none}'
				
				categories, f = Category.objects.order_by_search('name', obj.get_addit('category'))
				self.fields['product_category_s'].choices = [(-1,'-- создать --')] + [(p.id, p.name) for p in categories]
				self.fields['product_category_s'].initial = categories[0].id if f else -1
				self.fields['product_category'].initial = obj.get_addit('category')
				if f and obj.get_addit('category').lower() == categories[0].name.lower(): help_text += '.field-product_category {display:none}'
				
				help_text += '</style>'
				
				help_text += '<script>\
					django.jQuery("#id_product_brand_s,#id_product_category_s").change(function(){\
						var n = django.jQuery(this).attr("name");\
						n = n.substring(0, n.length-2);\
						var obj = django.jQuery(".field-"+n);\
						if (django.jQuery(this).val() == -1) {\
							obj.show();\
						} else {\
							obj.hide();\
						}\
					});\
					django.jQuery("#id_product").change(function(){\
						if (django.jQuery(this).val() == "") {\
							django.jQuery(".field-product_name").show();\
							django.jQuery(".field-product_brand_s,.field-product_category_s").show().change()\
						} else {\
							django.jQuery(".field-product_name").hide();\
							django.jQuery(".field-product_brand_s,.field-product_brand,.field-product_category_s,.field-product_category").hide()\
						}\
					});\
				</script>';
		
				self.fields['product_category_s'].help_text = help_text

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
			p.description = instance.get_addit('description')
			
			if self.cleaned_data['product_category_s'] == '-1':
				c = Category()
				c.name = self.cleaned_data['product_category']
				c.save()
				p.category = c
			else:
				p.category_id = self.cleaned_data['product_category_s']
				
			if self.cleaned_data['product_brand_s'] == '-1':
				b = Brand()
				b.name = self.cleaned_data['product_brand']
				b.save()
				p.brand = b
			else:
				p.brand_id = self.cleaned_data['product_brand_s']
			
			p.save()
			instance.product = p
			
		if commit:
			instance.save()
		
		return instance
	

class ShopHasProductAdmin(admin.ModelAdmin, DjangoObjectActions):

	form = ShopHasProductForm
	ordering = ['verified', 'name']
	list_filter = ['product__category']
	list_display = ['name', 'verified', 'product', 'shop']
	
	def get_object_actions(self, request, context, **kwargs):
		#print dir(admin.ModelAdmin)
		return self.objectactions

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
	
			
class BrandAdmin(admin.ModelAdmin, DjangoObjectActions):
	ordering = ['verified', 'name']
	list_display = ['name', 'verified']
	form = BrandForm
	
admin.site.register(Brand, BrandAdmin)

####################
## Product object
####################
class ProductForm(forms.ModelForm):
	class Meta:
		model = Product
		fields = ['name','image','brand','category','substance','description']
		
	def __init__(self, *args, **kwargs):
		super(ProductForm, self).__init__(*args, **kwargs)
		
		if 'instance' in kwargs:
			obj = kwargs['instance']
			
			self.fields['image'].help_text = '<a target="_blank" href="%s"><img src="%s" style="max-width:200px; max-height: 200px;"></a>' % \
				(obj.image, obj.image)
			self.fields['name'].help_text = '<a href="javascript:window.open(\'../../shophasproduct/?_popup=1&product__id__exact='+\
				str(obj.id)+'\', \'Продукты\', \'height=500,width=800,resizable=yes,scrollbars=yes\')" target="_blank">В магазинах</a>'
			
	def save(self, commit=True):
		instance = super(ProductForm, self).save(commit=False)
		instance.verified = True
			
		if commit:
			instance.save()
		
		return instance
	
			
class ProductAdmin(admin.ModelAdmin, DjangoObjectActions):
	ordering = ['verified', 'name']
	list_filter = ['category', 'brand']
	list_display = ['name', 'verified']
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
	
			
class CategoryAdmin(admin.ModelAdmin, DjangoObjectActions):
	ordering = ['verified', 'name']
	list_display = ['name', 'verified']
	form = CategoryForm
	
admin.site.register(Category, CategoryAdmin)

####################
## CategoryGroup object
####################

class CategoryGroupAdmin(MPTTModelAdmin):
    # speficfy pixel amount for this ModelAdmin only:
    mptt_level_indent = 20

admin.site.register(CategoryGroup, CategoryGroupAdmin)