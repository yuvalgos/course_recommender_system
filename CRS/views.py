import requests
from django.shortcuts import render
from bs4 import BeautifulSoup

# Create your views here.
def home(request):
    return render(request, template_name='base.html')

def new_search(request):
    search = request.POST.get('search')
    print(search)
    data_to_show = {
        'search': search,
    }
    return render(request, 'CRS/new_search.html', data_to_show)