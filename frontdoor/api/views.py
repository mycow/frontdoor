from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from datetime import date
from rest_framework import viewsets, permissions

from .serializers import *
from .models import *
from .util import *
from .forms import *

def index(request):
    return render(request, 'index.html', context={})

class AnnouncementViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer

class PaymentRequestViewSet(viewsets.ModelViewSet):
    queryset = PaymentRequest.objects.all()
    serializer_class = PaymentRequestSerializer

class CardViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Card.objects.all()
    serializer_class = CardSerializer

    def get_serializer_context(self):
        return {'user': self.request.user.username}

@login_required
def accountSettings(request):
    print (request.method)
    if request.method == 'POST':
        # print ("here?")
        form = AccountSettingsForm(request.user, request.POST)
        if form.is_valid():
            print ("here")
            # form.save()
            account_type = form.cleaned_data.get('account_type')
            # raw_password = form.cleaned_data.get('password1')
            # user = authenticate(username=username, password=raw_password)

            # login(request, user)
            # TODO: extend the form to cover the rest of this lol
            if Account.objects.filter(user__id=request.user.id).exists():
                account = Account.objects.get(user__id=request.user.id)
                account.account_type = account_type
            else:
                account = Account(user=request.user, account_type=account_type)
            account.save()
            # evl = Tenant.objects.get(user__username='eric')
            # lease = evl.current_lease
            # account.leases.add(lease)
            if account_type == 'T':
                tenant = Tenant(user=request.user)
                tenant.save()
            elif account_type == 'L':
                landlord = Landlord(user=request.user)
                landlord.save()
            return redirect('/house-settings/')
    # else:
    #     form = AccountSettingsForm(request.user)
    print("no here")
    form = AccountSettingsForm(request.user)
    return render(request, 'settings.html', context={'form':form})

@login_required
def houseIdSettings(request, house_id):
    house = Lease.objects.get(id=house_id)
    tenant = Tenant.objects.get(user__id=request.user.id)
    tenants = Account.objects.filter(leases=house)
    invite_code = str(house.house.house_name)+'-'+str(house.id)

    if request.method == 'POST':
        form = SetToCurrentLease(request.user, request.POST)
        if form.is_valid():
            tenant.current_lease = house
            tenant.save()

    is_current_lease = (tenant.current_lease == house)
    form = SetToCurrentLease(request.user)
    return render(request, 'house_id_settings.html', context={
        'house':house,
        'tenant':tenant,
        'tenants':tenants,
        'is_current_lease':is_current_lease,
        'invite_code':invite_code,
        'form':form
    })

@login_required
def houseSettings(request):
    # if request.method == 'POST':
    #     form = HouseSettingsForm(request.user, request.POST)
    #     if form.is_valid():
    #         return redirect('/house-settings/')
    # else:
    #     form = HouseSettingsForm(request.user)
    houses = get_houses(request)
    # if houses:
    #     print("shet")
    return render(request, 'house_settings.html', context={'houses':houses})

@login_required
def addHouse(request):
    if request.method == 'POST':
        if 'new_house_btn' in request.POST:
            new_house_form = AddHouseForm(request.user, request.POST)
            if new_house_form.is_valid():
                house_address = Address(
                    street=new_house_form.cleaned_data.get('street'),
                    city=new_house_form.cleaned_data.get('city'),
                    state=new_house_form.cleaned_data.get('state'),
                    code=new_house_form.cleaned_data.get('code')
                )
                house_address.save()
                house = House(
                    house_name=new_house_form.cleaned_data.get('house_name'),
                    house_address=house_address
                )
                house.save()
                lease = Lease(
                    house=house,
                    start_date=new_house_form.cleaned_data.get('lease_start'),
                    end_date=new_house_form.cleaned_data.get('lease_end')
                )
                lease.save()
                account = Account.objects.get(user__id=request.user.id)
                account.leases.add(lease)
                account.save()
                tenant = Tenant.objects.get(user__id=request.user.id)
                tenant.current_lease = lease
                tenant.save()
                return redirect('house-settings')
        if 'invite_btn' in request.POST:
            invite_form = InviteForm(request.user, request.POST)
            if invite_form.is_valid():
                lease_id = int(invite_form.cleaned_data.get('invite_code').rpartition('-')[-1])
                # print (lease_id)
                lease = Lease.objects.get(id=lease_id)
                account = Account.objects.get(user__id=request.user.id)
                account.leases.add(lease)
                account.save()
                tenant = Tenant.objects.get(user__id=request.user.id)
                tenant.current_lease = lease
                tenant.save()
                return redirect('house-settings')                
    
    new_house_form = AddHouseForm(request.user)
    invite_form = InviteForm(request.user)
    return render(request, 'add_house.html', context={'new_house_form':new_house_form, 'invite_form':invite_form})

@login_required
def rentCalculation(request):
    form = RentCalculator(request.user)
    return render(request, 'rentcalculator.html', context={'form':form})

@login_required
def feed(request):
    if request.method == 'POST':
        if 'ann_btn' in request.POST:
            ann_form = PostAnnouncement(request.user, request.POST)
            if ann_form.is_valid():
                card = Card(title=ann_form.cleaned_data['title'], lease=ann_form.cleaned_data['lease'])
                card.save()
                hcard = HouseCard(basecard=card, poster=request.user)
                hcard.save()
                announcement = Announcement(card=hcard)
                announcement.save()
        if 'prq_btn' in request.POST:
            prq_form = PostPaymentRequest(request.user, request.POST)
            if prq_form.is_valid():
                card = Card(title=prq_form.cleaned_data['title'], lease=prq_form.cleaned_data['lease'])
                card.save()
                ucard = UserCard(basecard=card, poster=request.user, recipient=prq_form.cleaned_data['recipient'])
                ucard.save()
                payment_request = PaymentRequest(card=ucard, amount=prq_form.cleaned_data['amount'])
                payment_request.save()
        if 'tsk_btn' in request.POST:
            tsk_form = PostTask(request.user, request.POST)
            if tsk_form.is_valid():
                card = Card(title=tsk_form.cleaned_data['title'], lease=tsk_form.cleaned_data['lease'])
                card.save()
                hcard = HouseCard(basecard=card, poster=request.user)
                hcard.save()
                task = Task(card=hcard, assignee=tsk_form.cleaned_data['assignee'])
                task.save()
        if 'evt_btn' in request.POST:
            evt_form = PostEvent(request.user, request.POST)
            if evt_form.is_valid():
                card = Card(title=evt_form.cleaned_data['title'], lease=evt_form.cleaned_data['lease'])
                card.save()
                hcard = HouseCard(basecard=card, poster=request.user)
                hcard.save()
                event = Event(card=hcard, eventdate=evt_form.cleaned_data['date'], eventtime=evt_form.cleaned_data['time'])
                event.save()
        if 'vte_btn' in request.POST:
            vte_form = PostVote(request.user, request.POST)
            if vte_form.is_valid():
                card = Card(title=vte_form.cleaned_data['title'], lease=vte_form.cleaned_data['lease'])
                card.save()
                hcard = HouseCard(basecard=card, poster=request.user)
                hcard.save()
                vote = Vote(card=hcard)
                vote.save()

    cards = get_cards(request)
    ann_form = PostAnnouncement(request.user)
    prq_form = PostPaymentRequest(request.user)
    tsk_form = PostTask(request.user)
    evt_form = PostEvent(request.user)
    vte_form = PostVote(request.user)

    return render(request, 'feed.html', context={
        'cards':cards,
        'ann_form':ann_form,
        'prq_form':prq_form,
        'tsk_form':tsk_form,
        'evt_form':evt_form,
        'vte_form':vte_form})

# def post_announcement(request):
#     if request.method == 'POST':
#         form = PostAnnouncement(request.POST)
#         if form.is_valid():
#             lease = get_lease(request.user)
#             card1 = Card(title=form.cleaned_data['title'], lease=lease)
#             card1.save()
#             hcard = HouseCard(basecard=card1, poster=request.user)
#             hcard.save()
#             announcement = Announcement(card=hcard)
#             announcement.save()
#     else:
#         form = PostAnnouncement()
#     cards = get_cards(request)
#     form = PostAnnouncement()
#     return render(request, 'feed.html', context={'cards':cards, 'form':form})

def signup(request):
    # if request.user.is_authenticated:
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)

            login(request, user)
            # TODO: extend the form to cover the rest of this lol
            # account = Account(user=user, account_type='T')
            # account.save()
            # evl = Tenant.objects.get(user__username='eric')
            # lease = evl.current_lease
            # account.leases.add(lease)
            # tenant = Tenant(user=request.user, current_lease=lease)
            # tenant.save()
            return redirect('/account-settings/')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})
    # else:
    #     return feed(request)

def testdata(request):
    # # DO NOT RUN MORE THAN ONCE YET
    # # create house and account for current user
    # account1 = Account(user=request.user, account_type='T')
    # account1.save()
    # addy = Address(street='860 Washington St', city='Santa Clara', state='CA', code='95050')
    # addy.save()
    # house = House(house_address=addy, house_name='Courtside')
    # house.save()
    # lease = Lease(house=house, start_date=date(2017, 7, 5), end_date=date(2018, 7, 5))
    # lease.save()
    # account1.leases.add(lease)
    # account1.save()
    # tenant = Tenant(user=request.user, current_lease=lease)
    # tenant.save()

    # # create an announcement from current user
    # card1 = Card(title='This is an announcement', house=house)
    # card1.save()
    # hcard = HouseCard(basecard=card1, poster=request.user)
    # hcard.save()
    # announcement = Announcement(card=hcard)
    # announcement.save()
    # createleaseandhouseandcreateaccountforuser(request)
    createaccountforuserandaddthemtohouse(request)
    # feed(request)
    cards = get_cards(request)
    return render(request, 'feed.html', context={'cards':cards})

def deletestuff(request):
    announcements = Announcement.objects.all()
    announcements.delete()

    hcards = HouseCard.objects.all()
    hcards.delete()

    cards = Card.objects.all()
    cards.delete()

    # cards = get_cards(request)
    # return render(request, 'feed.html', context={'cards':cards})
