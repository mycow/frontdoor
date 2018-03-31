from django.db import models

class House(models.Model):
    house_name = models.CharField(max_length=100)

class Account(models.Model):
    ACCOUNT_TYPES = (
        ('T','Tenant'),
        ('L','Landlord'),
    )
    name = models.CharField(max_length = 100)
    username = models.CharField(max_length = 20)
    account_type = models.CharField(max_length = 1, choices=ACCOUNT_TYPES)