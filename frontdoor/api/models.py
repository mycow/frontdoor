import uuid
from django.db import models
from django.contrib.auth.models import User
from .choices import *

class Landlord(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class Address(models.Model):
    street = models.TextField()
    city = models.TextField()
    state = models.TextField()
    code = models.TextField()

class House(models.Model):
    # uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)        
    house_name = models.CharField(max_length=100, null=True)
    house_address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True)
    landlord = models.ForeignKey(Landlord, on_delete=models.SET_NULL, null=True)

class Lease(models.Model):
    # uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)        
    house = models.ForeignKey(House, on_delete=models.CASCADE, null=True)
    start_date = models.DateField()
    end_date = models.DateField()

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ACCOUNT_TYPES = (
        ('T','Tenant'),
        ('L','Landlord'),
    )
    account_type = models.CharField(max_length = 1, choices=ACCOUNT_TYPES)
    # uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)    
    leases = models.ManyToManyField(Lease)

class Tenant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    current_lease = models.ForeignKey(Lease, on_delete=models.SET_NULL, null=True)

class Comment(models.Model):
    poster = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)

class Card(models.Model):
    # uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    time = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=140)
    lease = models.ForeignKey(Lease, on_delete=models.CASCADE, null=True)

class HouseCard(models.Model):
    basecard = models.OneToOneField(Card, on_delete=models.CASCADE)
    poster = models.ForeignKey(User, on_delete=models.CASCADE)
    comments = models.ManyToManyField(Comment)
    likes = models.ManyToManyField(User, related_name='likes')

class UserCard(models.Model):
    basecard = models.OneToOneField(Card, on_delete=models.CASCADE)
    poster = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='poster')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipient')

class Announcement(models.Model):
    card = models.ForeignKey(HouseCard, on_delete=models.CASCADE)

class PaymentRequest(models.Model):
    card = models.ForeignKey(UserCard, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=6, decimal_places=2)

class Task(models.Model):
    card = models.ForeignKey(HouseCard, on_delete=models.CASCADE)
    assignee = models.ForeignKey(User, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)

class Setup(models.Model):
    card = models.ForeignKey(UserCard, on_delete=models.CASCADE)
    link = models.TextField()

class SubleaseRequest(models.Model):
    card = models.ForeignKey(UserCard, on_delete=models.CASCADE)
    message = models.CharField(max_length=280)

class Event(models.Model):
    card = models.ForeignKey(HouseCard, on_delete=models.CASCADE)
    eventdate = models.DateField()
    eventtime = models.TimeField(null=True)

class Vote(models.Model):
    card = models.ForeignKey(HouseCard, on_delete=models.CASCADE)
    yes = models.ManyToManyField(User, related_name='yes')
    no = models.ManyToManyField(User, related_name='no')

class Profile(models.Model):
    TENANT = 'T'
    LANDLORD = 'L'
    USER_TYPE_CHOICES = (
        ('T','Tenant'),
        ('L','Landlord'),
    )

    type = models.CharField(max_length=5, choices=USER_TYPE_CHOICES, default='T')

tenants = Profile.objects.filter(type=Profile.TENANT)
landlords = Profile.objects.filter(type=Profile.LANDLORD)