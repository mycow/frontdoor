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
    # uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)        
    house_name = models.CharField(max_length=100, null=True)
    house_address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True)
    landlord = models.ForeignKey(Landlord, on_delete=models.SET_NULL, null=True)

class Lease(models.Model):
    # uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)        
    house = models.ForeignKey(House, on_delete=models.CASCADE, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    includecommonarea = models.BooleanField(default=True)
    rentscalefactor = models.FloatField(null=True)
    rent = models.DecimalField(max_digits=8, decimal_places=2, null=True)

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
    message = models.TextField(null=True)

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

class ChatMessage(models.Model):
    lease = models.ForeignKey(Lease, on_delete=models.CASCADE, null=True)
    message = models.TextField()
    time = models.DateTimeField(auto_now_add=True)
    poster = models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, related_name='chatlikes')  

class Room(models.Model):
    lease = models.ForeignKey(Lease, on_delete=models.CASCADE, null=True)
    users = models.ManyToManyField(User, related_name='roomtenants')
    num_users = models.IntegerField(null=True)
    rent = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    squarefeet = models.IntegerField(null=True)
    name = models.TextField()
    hasbathroom = models.BooleanField(default=False)
    hasawkwardlayout = models.BooleanField(default=False)
    hascloset = models.BooleanField(default=False)

# class Sublease(models.Model):

