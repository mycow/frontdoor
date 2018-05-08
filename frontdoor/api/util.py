from .models import *
from .serializers import *
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

from itertools import chain
from operator import attrgetter
from datetime import date
from django.db.models import Q

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

def roundbase(x, base=5):
    return int(base * round(float(x)/base))

def calculate_rent_for_room(totalrent, rentscalefactor, sqft, totalsqft, roomcount, personcountroom, personcounthouse, multiplier):
    # print (str(totalrent)+" "+str(rentscalefactor)+" "+str(sqft)+" "+str(totalsqft)+" "+str(roomcount)+" "+str(personcountroom)+" "+str(personcounthouse))
    roomprice = float(totalrent)*float(1-rentscalefactor)*float(sqft)/(totalsqft/roomcount)/roomcount/personcountroom*float(multiplier)
    commonprice = float(totalrent)*float(rentscalefactor)/personcounthouse
    return roomprice + commonprice

def get_rooms(request):
    lease = get_lease(request.user)
    rooms = Room.objects.filter(lease=lease)

    return rooms

def get_houses(request):
    account = Account.objects.get(user__id=request.user.id)
    # print (account.leases.all())
    return account.leases.all()

def get_cards(request):
    # user1 = User.objects.filter(username='evl')
    # print(user1)

    tenant = Tenant.objects.get(user__username=request.user)
    lease = tenant.current_lease
    announcements = Announcement.objects.filter(Q(card__basecard__lease=lease))
    # print(announcements)
    # print(request.user)
    for card in announcements:
        card.type = 'announcement'
        # test serializing
        # serializer = AnnouncementSerializer(card)
        # content = JSONRenderer(serializer.data)
        # print('here is the content')
        # print(content)


    payments = PaymentRequest.objects.filter(Q(card__recipient__username=request.user) | Q(card__poster__username=request.user))
    for card in payments:
        card.type = 'payment'

    tasks = Task.objects.filter(Q(card__basecard__lease=lease))
    for card in tasks:
        card.type = 'task'

    setups = Setup.objects.filter(Q(card__recipient__username=request.user) | Q(card__poster__username=request.user))
    for card in setups:
        card.type = 'setup'

    subleases = SubleaseRequest.objects.filter(Q(card__recipient__username=request.user) | Q(card__poster__username=request.user))
    for card in subleases:
        card.type = 'sublease request'

    events = Event.objects.filter(Q(card__basecard__lease=lease))
    for card in events:
        card.type = 'event'

    votes = Vote.objects.filter(Q(card__basecard__lease=lease))
    for card in votes:
        card.type = 'vote'

    return sorted(
        list(chain(
            announcements,
            payments,
            tasks,
            setups,
            subleases,
            events,
            votes)),
        key=attrgetter('card.basecard.time'), reverse=True)

def get_lease(user):
    tenant = Tenant.objects.get(user__username=user)
    return tenant.current_lease

def createleaseandhouseandcreateaccountforuser(request):
    # # DO NOT RUN MORE THAN ONCE YET
    # # create house and account for current user
    # print(request.user)
    account1 = Account(user=request.user, account_type='T')
    account1.save()
    addy = Address(street='860 Washington St', city='Santa Clara', state='CA', code='95050')
    addy.save()
    house = House(house_address=addy, house_name='Courtside')
    house.save()
    # house = House.objects.filter(house_name='Courtside')
    lease = Lease(house=house, start_date=date(2017, 7, 5), end_date=date(2018, 7, 5))
    lease.save()
    # account1 = Account.objects.filter(user__username="eric")
    account1.leases.add(lease)
    account1.save()
    tenant = Tenant(user=request.user, current_lease=lease)
    tenant.save()

    # # create an announcement from current user
    titlestr = "this is an announcement from "+str(request.user)
    card1 = Card(title=titlestr, lease=lease)
    card1.save()
    hcard = HouseCard(basecard=card1, poster=request.user)
    hcard.save()
    announcement = Announcement(card=hcard)
    announcement.save()

    card2 = Card(title='you owe me money', lease=lease)
    card2.save()
    user2 = User.objects.get(username="test2")
    ucard = UserCard(basecard=card2, poster=request.user, recipient=user2)
    ucard.save()
    pr = PaymentRequest(card=ucard, amount=100)
    pr.save()

def createaccountforuserandaddthemtohouse(request):
    account1 = Account(user=request.user, account_type='T')
    account1.save()
    evl = Tenant.objects.get(user__username='eric')
    lease = evl.current_lease
    tenant = Tenant(user=request.user, current_lease=lease)
    tenant.save()