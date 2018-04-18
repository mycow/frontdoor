from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from frontdoor.forms import SignUpForm

def login(request):
	return render(request,'registration/login.html',context={})

def signup(request):
	if request.method == 'POST':
		form = SignUpForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data.get('username')
			raw_password = form.cleaned_data.get('password1')
			user = authenticate(username=username, password=raw_password)
			login(request, user)
			return redirect('/feed/')
	else:
		form = SignUpForm()
	return render(request, 'signup.html', {'form': form})

def index(request):
    return render(request, 'index.html', context={})

@login_required
def feed(request):
    return render(request, 'feed.html', context={})