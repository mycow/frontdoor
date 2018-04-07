from rest_framework import serializers

from .models import *

# class CardSerializer(serializers.Serializer):

class AnnouncementSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    type = serializers.CharField(max_length=100)
    # title = serializers.CharField(max_length=140)

    def create(self, valudated_data):
        return Announcement.objects.create(**valudated_data)

    def update(self, instance, validated_data):
        instance.id = validated_data.get('id')
        instance.type = 'announcement'
        # instance.title = validated_data('card__basecard__title')

        return instance