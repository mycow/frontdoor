from django.urls import include, path
from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path('feed/', views.feed, name='feed'),
    path('', views.index, name='index'),
    path('signup/', views.signup, name="signup"),
]