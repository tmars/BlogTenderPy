from django.shortcuts import render
from django.shortcuts import render_to_response

def home(request):
	return render_to_response('main/home.html')

def parser(request):
	return render_to_response('admin/parser/pasers.html')