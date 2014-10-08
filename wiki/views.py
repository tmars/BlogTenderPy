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


def category_list(request):
	categories = CategoryGroup.objects.all()
	
	return render(request, 'wiki/category/list.html', {"list": categories})

def category(request, id):
	c = Category.objects.get(id=id)
	product_list = Product.objects.filter(category=c)
	paginator = Paginator(product_list, 10)

	page = request.GET.get('page')
	try:
		products = paginator.page(page)
	except PageNotAnInteger:
		products = paginator.page(1)
	except EmptyPage:
		products = paginator.page(paginator.num_pages)

	return render(request, 'wiki/category/products.html', {"list": products})

def product(request, id):
	p = Product.objects.get(id=id)

	return render(request, 'wiki/product/info.html', {"p": p})