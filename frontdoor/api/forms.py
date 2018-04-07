from django.contrib.auth.models import User
from django import forms

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
import datetime

from .models import *
from .fields import *
from .util import *

class PostAnnouncement(forms.Form):
    title = forms.CharField(label='Announcement', max_length=140)
    lease = HouseModelChoiceField(label='House', empty_label=None, queryset=Lease.objects.none())

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
    lease = HouseModelChoiceField(label='House', empty_label=None, queryset=Lease.objects.none())
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
    lease = HouseModelChoiceField(label='House', empty_label=None, queryset=Lease.objects.none())
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
    lease = HouseModelChoiceField(label='House', empty_label=None, queryset=Lease.objects.none())
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
    lease = HouseModelChoiceField(label='House', empty_label=None, queryset=Lease.objects.none())

    def __init__(self, user, *args, **kwargs):
        super(PostVote, self).__init__(*args, **kwargs)
        account = Account.objects.get(user__username=user)
        leases = account.leases
        self.fields['lease'].queryset = leases

        current_lease = get_lease(user)
        self.fields['lease'].initial = current_lease
