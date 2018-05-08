from django.contrib.auth.models import User
from django import forms

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
import datetime

from .models import *
from .fields import *
from .util import *

class AccountSettingsForm(forms.Form):
    TYPE_CHOICES = (
        ('T', 'Tenant'),
        ('L', 'Landlord'),
    )
    account_type = forms.ChoiceField(choices=TYPE_CHOICES, label='Account Type')

    def __init__(self, user, *args, **kwargs):
        super(AccountSettingsForm, self).__init__(*args, **kwargs)
        # account = Account.objects.get(user__username=user)

class HouseSettingsForm(forms.Form):

    def __init__(self, user, *args, **kwargs):
        super(HouseSettingsForm, self).__init__(*args, **kwargs)

class InviteForm(forms.Form):
    invite_code = forms.CharField()

    def __init__(self, user, *args, **kwargs):
        super(InviteForm, self).__init__(*args, **kwargs)

class AddHouseForm(forms.Form):
    house_name = forms.CharField(max_length=100, required=False)
    street = forms.CharField()
    city = forms.CharField()
    state = forms.CharField()
    code = forms.CharField()
    lease_start = forms.DateField(initial=datetime.date.today)
    lease_end = forms.DateField(initial=datetime.date.today)

    def __init__(self, user, *args, **kwargs):
        super(AddHouseForm, self).__init__(*args, **kwargs)

class SetToCurrentLease(forms.Form):

    def __init__(self, user, *args, **kwargs):
        super(SetToCurrentLease, self).__init__(*args, **kwargs)

# class UserCreateForm(UserCreationForm):

#     class Meta:

class RentCalculator(forms.Form):
    # num_tenants = forms.IntegerField(label='Number of Tenants')
    total_rent = forms.IntegerField(label='Total Rent')
    include_common_space = forms.BooleanField()
    common_space_importance = forms.FloatField()

    def __init__(self, user, *args, **kwargs):
        super(RentCalculator, self).__init__(*args, **kwargs)

class AddRoomForm(forms.Form):
    room_name = forms.CharField()
    square_footage = forms.IntegerField()
    number_of_residents = forms.IntegerField()
    has_bathroom = forms.BooleanField(required=False)
    has_awkward_layout = forms.BooleanField(required=False)
    has_closet = forms.BooleanField(required=False)

    def __init__(self, user, *args, **kwargs):
        super(AddRoomForm, self).__init__(*args, **kwargs)

class SignUpForm(UserCreationForm):
    TYPE_CHOICES = (
        ('T', 'Tenant'),
        ('L', 'Landlord'),
    )
    first_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Required.')
    email = forms.EmailField(max_length=254, help_text='Required.')
    user_type = forms.ChoiceField(choices=TYPE_CHOICES, help_text='Are you a Tenant or Landlord?')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'user_type', )

    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class PostAnnouncement(forms.Form):
    title = forms.CharField(label='Announcement', max_length=140)
    lease = HouseModelChoiceField(label='House', empty_label='Choose House', queryset=Lease.objects.none())

    def __init__(self, user, *args, **kwargs):
        super(PostAnnouncement, self).__init__(*args, **kwargs)
        account = Account.objects.get(user__username=user)
        leases = account.leases
        self.fields['lease'].queryset = leases

        current_lease = get_lease(user)
        self.fields['lease'].initial = current_lease

class PostPaymentRequest(forms.Form):
    title = forms.CharField(label='Payment Request', max_length=140)
    amount = forms.DecimalField(max_digits=6, decimal_places=2)
    lease = HouseModelChoiceField(label='House', empty_label='Choose House', queryset=Lease.objects.none())
    recipient = UserModelChoiceField(label='Send Request To', empty_label='Choose Tenant', queryset=User.objects.none())

    def __init__(self, user, *args, **kwargs):
        super(PostPaymentRequest, self).__init__(*args, **kwargs)
        account = Account.objects.get(user__username=user)
        leases = account.leases
        self.fields['lease'].queryset = leases

        current_lease = get_lease(user)
        self.fields['lease'].initial = current_lease
        # cleaned_data = super(PostPaymentRequest, self).clean()
        # self.fields['recipient'].queryset = Account.objects.all()
        # self.clean()
        self.fields['recipient'].queryset = User.objects.filter(account__leases__in=[current_lease]).exclude(username=user)

    # TODO: Change recipient queryset when lease is changed
    # def clean(self):
    #     self.fields['recipient'].queryset = Account.objects.all()

class PostTask(forms.Form):
    title = forms.CharField(label='Task', max_length=140)
    lease = HouseModelChoiceField(label='House', empty_label='Choose House', queryset=Lease.objects.none())
    assignee = UserModelChoiceField(label='Assign to', empty_label='Choose Tenant', queryset=User.objects.none())

    def __init__(self, user, *args, **kwargs):
        super(PostTask, self).__init__(*args, **kwargs)
        account = Account.objects.get(user__username=user)
        leases = account.leases
        self.fields['lease'].queryset = leases

        current_lease = get_lease(user)
        self.fields['lease'].initial = current_lease

        self.fields['assignee'].queryset = User.objects.filter(account__leases__in=[current_lease]).exclude(username=user)

class PostEvent(forms.Form):
    title = forms.CharField(label='Event', max_length=140)
    lease = HouseModelChoiceField(label='House', empty_label='Choose House', queryset=Lease.objects.none())
    date = forms.DateField(label='Date', initial=datetime.date.today)
    time = forms.TimeField(label='Time', required=False)

    def __init__(self, user, *args, **kwargs):
        super(PostEvent, self).__init__(*args, **kwargs)
        account = Account.objects.get(user__username=user)
        leases = account.leases
        self.fields['lease'].queryset = leases

        current_lease = get_lease(user)
        self.fields['lease'].initial = current_lease

class PostVote(forms.Form):
    title = forms.CharField(label='Vote', max_length=140)
    lease = HouseModelChoiceField(label='House', empty_label='Choose House', queryset=Lease.objects.none())

    def __init__(self, user, *args, **kwargs):
        super(PostVote, self).__init__(*args, **kwargs)
        account = Account.objects.get(user__username=user)
        leases = account.leases
        self.fields['lease'].queryset = leases

        current_lease = get_lease(user)
        self.fields['lease'].initial = current_lease
