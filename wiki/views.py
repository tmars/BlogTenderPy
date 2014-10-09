from django.shortcuts import render, render_to_response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from wiki.models import *

def shop_list(request):
	shop_list = Shop.objects.all()
	paginator = Paginator(shop_list, 10)

	page = request.GET.get('page')
	try:
		shops = paginator.page(page)
	except PageNotAnInteger:
		shops = paginator.page(1)
	except EmptyPage:
		shops = paginator.page(paginator.num_pages)

	return render(request, 'wiki/shop/list.html', {"list": shops})

def shop(request, id):
	s = Shop.objects.get(id=id)
	cs = Category.objects.raw('SELECT DISTINCT c.* FROM wiki_category c \
		INNER JOIN wiki_product p ON p.category_id=c.id\
		INNER JOIN wiki_shophasproduct shp ON shp.product_id=p.id\
		WHERE shp.shop_id='+id)
	
	return render(request, 'wiki/shop/info.html', {'shop': s, 'categories': cs})


def category_list(request):
	categories = CategoryGroup.objects.all()
	
	return render(request, 'wiki/category/list.html', {"list": categories})

def category(request, id):
	c = Category.objects.get(id=id)
	product_list = Product.objects.filter(category=c)
	
	if request.GET.get('brand'):
		product_list = product_list.filter(brand=request.GET.get('brand'))

	paginator = Paginator(product_list, 10)
	page = request.GET.get('page')
	try:
		products = paginator.page(page)
	except PageNotAnInteger:
		products = paginator.page(1)
	except EmptyPage:
		products = paginator.page(paginator.num_pages)

	return render(request, 'wiki/category/products.html', {'list': products, 'category': c})

def product(request, id):
	p = Product.objects.get(id=id)
	shps = ShopHasProduct.objects.filter(product=p,available=True);
	return render(request, 'wiki/product/info.html', {"p": p, "shps": shps})