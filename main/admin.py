from django.shortcuts import render
from django.shortcuts import render_to_response

def parser(request):
	return render_to_response('admin/parser/pasers.html')
