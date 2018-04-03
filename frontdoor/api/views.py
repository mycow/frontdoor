from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

def index(request):
    return render(request, 'index.html', context={})

@login_required
def feed(request):
    return render(request, 'feed.html', context={})