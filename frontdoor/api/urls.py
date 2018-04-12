from django.urls import include, path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path('signup/', views.signup, name='signup'),
    path('feed/', views.feed, name='feed'),
    # path('post_announcement/', views.post_announcement, name='post_announcement'),
    path('maketestdata/', views.testdata, name='maketestdata'),
    path('', views.index, name='index'),
]