from django.db.models import Q
from rest_framework import serializers, routers, viewsets

from .models import *

class LeaseRoomSerializer(serializers.ModelSerializer):

    class Meta:
        model = Room
        fields = ('num_users', 'rent', 'squarefeet', 'name', 'hasbathroom', 'hasawkwardlayout', 'hascloset')

class LeaseUserSerializer(serializers.ModelSerializer):
    is_self = serializers.SerializerMethodField()

    def get_is_self(self, obj):
        return obj.username == self.context['user']

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'is_self')

class LeaseSerializer(serializers.ModelSerializer):
    house_name = serializers.SerializerMethodField()
    landlord = serializers.SerializerMethodField()
    is_current = serializers.SerializerMethodField()

    def get_house_name(self, obj):
        return obj.house.house_name

    def get_landlord(self, obj):
        return obj.house.landlord

    def get_is_current(self, obj):
        tenant = Tenant.objects.get(user__username=self.context['user'])
        return Lease.objects.filter(Q(id=tenant.current_lease.id) & Q(id=obj.id)).exists()

    class Meta:
        model = Lease
        fields = ('id', 'house_name', 'start_date', 'end_date', 'landlord', 'is_current')

class ChatMessageSerializer(serializers.ModelSerializer):
    likes = serializers.SerializerMethodField()
    poster = serializers.SerializerMethodField()

    def get_poster(self, obj):
        return obj.poster.username

    def get_likes(self, obj):
        return obj.likes.count()

    class Meta:
        model = ChatMessage
        fields = ('lease', 'message', 'time', 'poster', 'likes')

class CardSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()
    house = serializers.SerializerMethodField()
    # user = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()

    def get_date(self, obj):
        return obj.time

    def get_house(self, obj):
        # print (obj.title)
        return House.objects.get(id=obj.lease.house.id).house_name

    # def get_user(self, obj):
    #     return self.context['user']

    def get_content(self, obj):
        # print (obj.id)
        # print (self.context['user'])
        if HouseCard.objects.filter(basecard__id=obj.id):
            hc = HouseCard.objects.get(basecard__id=obj.id)
            if Announcement.objects.filter(card__id=hc.id):
                return AnnouncementSerializer(Announcement.objects.get(card__id=hc.id)).data
            if Task.objects.filter(card__id=hc.id):
                return TaskSerializer(Task.objects.get(card__id=hc.id)).data
            if Vote.objects.filter(card__id=hc.id):
                return VoteSerializer(Vote.objects.get(card__id=hc.id)).data
            if Event.objects.filter(card__id=hc.id):
                return EventSerializer(Event.objects.get(card__id=hc.id)).data
        elif UserCard.objects.filter(basecard__id=obj.id):
            uc = UserCard.objects.get(basecard__id=obj.id)
            if PaymentRequest.objects.filter(card__id=uc.id):
                return PaymentRequestSerializer(PaymentRequest.objects.get(card__id=uc.id)).data
            if SubleaseRequest.objects.filter(card__id=uc.id):
                return SubleaseRequestSerializer(SubleaseRequest.objects.get(card__id=uc.id)).data
            if Setup.objects.filter(card__id=uc.id):
                return SetupSerializer(Setup.objects.get(card__id=uc.id)).data
        return None

    class Meta:
        model = Card
        fields = ('id', 'date', 'title', 'house', 'content')

    def create(self, valudated_data):
        # print (valudated_data)
        card = Card.objects.create(**valudated_data)
        return card

    # def update(self, instance, validated_data):
    #     if HouseCard.objects.filter(basecard__id=instance.id):
    #         hc = HouseCard.objects.get(basecard__id=instance.id)
    #         if Announcement.objects.filter(card__id=hc.id):
                # return AnnouncementSerializer(Announcement.objects.get(card__id=hc.id)).data
            # if Task.objects.filter(card__id=hc.id):
            #     return TaskSerializer(Task.objects.get(card__id=hc.id)).data
            # if Vote.objects.filter(card__id=hc.id):
            #     return VoteSerializer(Vote.objects.get(card__id=hc.id)).data
            # if Event.objects.filter(card__id=hc.id):
            #     return EventSerializer(Event.objects.get(card__id=hc.id)).data

class SubleaseRequestSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()

    def get_type(self, obj):
        return 'sublease request'

    def get_owner(self, obj):
        return UserCard.objects.get(id=obj.card.id).poster.username

    class Meta:
        model = SubleaseRequest
        fields =  ('type', 'owner', 'message')

    def create(self, valudated_data):
        return SubleaseRequest.objects.create(**valudated_data)

class SetupSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()

    def get_type(self, obj):
        return 'setup'

    def get_owner(self, obj):
        return UserCard.objects.get(id=obj.card.id).poster.username

    class Meta:
        model = Setup
        fields =  ('type', 'owner', 'link')

    def create(self, valudated_data):
        return Setup.objects.create(**valudated_data)

class VoteSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()

    def get_type(self, obj):
        return 'vote'

    def get_owner(self, obj):
        return HouseCard.objects.get(id=obj.card.id).poster.username

    class Meta:
        model = Vote
        fields = ('type', 'owner', 'yes', 'no')

    def create(self, valudated_data):
        return Vote.objects.create(**valudated_data)

class EventSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()

    def get_type(self, obj):
        return 'event'

    def get_owner(self, obj):
        return HouseCard.objects.get(id=obj.card.id).poster.username

    class Meta:
        model = Event
        fields = ('type', 'owner', 'eventdate', 'eventtime')

    def create(self, valudated_data):
        return Event.objects.create(**valudated_data)

class TaskSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    assignee = serializers.SerializerMethodField()

    def get_type(self, obj):
        return 'task'

    def get_owner(self, obj):
        return HouseCard.objects.get(id=obj.card.id).poster.username

    def get_assignee(self, obj):
        return obj.assignee.username

    class Meta:
        model = Task
        fields = ('type', 'owner', 'assignee', 'completed')

    def create(self, valudated_data):
        return Task.objects.create(**valudated_data)

class PaymentRequestSerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField(read_only=True)
    type = serializers.SerializerMethodField()
    # title = serializers.SerializerMethodField()
    # date = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    is_payed = serializers.SerializerMethodField()

    def get_type(self, obj):
        return 'payment'

    # def get_title(self, obj):
    #     return UserCard.objects.get(id=obj.card.id).basecard.title

    # def get_date(self, obj):
    #     return UserCard.objects.get(id=obj.card.id).basecard.time

    def get_owner(self, obj):
        return UserCard.objects.get(id=obj.card.id).poster.username

    def get_is_payed(self, obj):
        return False

    class Meta:
        model = PaymentRequest
        fields =  ('type', 'owner', 'is_payed', 'amount')

    def create(self, valudated_data):
        return PaymentRequest.objects.create(**valudated_data)

    def update(self, instance, validated_data):
        instance.id = validated_data.get('id')
        instance.save()
        # instance.title = validated_data('card__basecard__title')

        return instance

class AnnouncementSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    # title = serializers.SerializerMethodField()
    # date = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()

    def get_type(self, obj):
        return 'announcement'

    # def get_title(self, obj):
    #     return HouseCard.objects.get(id=obj.card.id).basecard.title

    # def get_date(self, obj):
    #     return HouseCard.objects.get(id=obj.card.id).basecard.time

    def get_owner(self, obj):
        return HouseCard.objects.get(id=obj.card.id).poster.username

    def get_likes(self, obj):
        # print (HouseCard.objects.get(id=obj.card.id).likes)
        # likes = []
        # like_names = HouseCard.objects.get(id=obj.card.id).likes
        # for i in like_names:
        #     if 
        #     likes.append(i.username)
        return []

    def get_comments(self, obj):
        return []

    class Meta:
        model = Announcement
        fields =  ('type', 'owner', 'likes', 'comments')

    def create(self, valudated_data):
        return Announcement.objects.create(**valudated_data)

    def update(self, instance, validated_data):
        # instance.id = validated_data.get('id')
        # instance.owner = validated_data('')
        instance.save()
        # instance.title = validated_data('card__basecard__title')

        return instance

# class AnnouncementSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = Announcement
#         fields = '__all__'
