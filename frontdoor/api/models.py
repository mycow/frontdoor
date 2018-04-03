import uuid
from django.db import models
from django.contrib.auth.models import User

class Landlord(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class Address(models.Model):
    street = models.TextField()
    city = models.TextField()
    state = models.TextField()
    code = models.TextField()

class House(models.Model):
    house_name = models.CharField(max_length=100)
    house_address = models.ForeignKey(Address, on_delete=models.CASCADE)
    landlord = models.ForeignKey(Landlord, on_delete=models.SET_NULL, null=True)

class Lease(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    leases = models.ManyToManyField(Lease)
    ACCOUNT_TYPES = (
        ('T','Tenant'),
        ('L','Landlord'),
    )
    account_type = models.CharField(max_length = 1, choices=ACCOUNT_TYPES)

class Tenant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    current_house = models.ForeignKey(House, on_delete=models.SET_NULL, null=True)

class Comment(models.Model):
    poster = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)

class Card(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    time = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=140)
    house = models.ForeignKey(House, on_delete=models.CASCADE)

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
