from django.urls import include, path
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from rest_framework import routers, serializers, viewsets, permissions

from . import views
from .models import *

# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff')

# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer

# API routes
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'announcements', views.AnnouncementViewSet)
router.register(r'payments', views.PaymentRequestViewSet)
router.register(r'cards', views.CardViewSet)
router.register(r'chats', views.ChatMessageViewSet)
router.register(r'leases', views.LeaseViewSet)
router.register(r'lease/users', views.LeaseUserViewSet)
router.register(r'rooms', views.LeaseRoomViewSet)
# router.register(r'cardslike', view)
# router.register(r'card/<int:card_id>/like', views.CardViewSet)

urlpatterns = [
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('signup/', views.signup, name='signup'),
    path('account-settings/', views.accountSettings, name='account-settings'),
    path('house-settings/', views.houseSettings, name='house-settings'),
    path('house-settings/<int:house_id>/', views.houseIdSettings),
    path('add-house/', views.addHouse, name='add-house'),
    path('feed/', views.feed, name='feed'),
    path('rent/', views.rentCalculation, name='rent'),
    path('tasks/', views.tasks, name='tasks'),
    path('calendar/', views.calendar, name='calendar'),
    # path('api/card/<int:card_id>/like', views.postLike, name='post-like'),
    path('cardlist/<int:card_id>/', views.card_list_view),
    path('api/card/create/', views.createCard),
    path('api/chat/create/', views.createChatMessage),
    path('api/lease/change/', views.changeUserCurrentLease),
    path('api/rent/', views.calculateRent),
    path('api/room/add/', views.addhousefrompost),
    # path('api/card/new/', views.card_list_view),
    # path('cards/', views.cards, name='cards'),
    # path('post_announcement/', views.post_announcement, name='post_announcement'),
    # path('maketestdata/', views.testdata, name='maketestdata'),
    path('', views.index, name='index'),
]