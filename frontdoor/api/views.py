from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from datetime import date
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.views.decorators.http import require_POST
from django.db.models import Sum

from math import floor, ceil
from decimal import *

from .serializers import *
from .models import *
from .util import *
from .forms import *

def index(request):
    if request.user.is_authenticated:
        return redirect('feed')
    return redirect('/accounts/login/')
    # return render(request, 'index.html', context={})

class LeaseRoomViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = LeaseRoomSerializer

    def get_serializer_context(self):
        return {'user': self.request.user.username}

    def get_queryset(self):
        # leases = Account.objects.get(user=self.request.user).leases
        # return Lease.objects.filter(id__in=leases)
        currentlease = Tenant.objects.get(user=self.request.user).current_lease
        return Room.objects.filter(lease=currentlease)

class LeaseRoomViewSetById(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = LeaseRoomSerializer

    def get_serializer_context(self):
        return {'user': self.request.user.username}

    def get_queryset(self):
        # leases = Account.objects.get(user=self.request.user).leases
        # return Lease.objects.filter(id__in=leases)
        lease = Lease.objects.get(id=self.kwargs['lease_id'])
        return Room.objects.filter(lease=lease)

class LeaseUserViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = LeaseUserSerializer

    def get_serializer_context(self):
        return {'user': self.request.user.username}

    def get_queryset(self):
        # leases = Account.objects.get(user=self.request.user).leases
        # return Lease.objects.filter(id__in=leases)
        currentlease = Tenant.objects.get(user=self.request.user).current_lease
        return User.objects.filter(account__leases__in=[currentlease])

class LeaseUserViewSetById(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = LeaseUserSerializer

    def get_serializer_context(self):
        return {'user': self.request.user.username}

    def get_queryset(self):
        # leases = Account.objects.get(user=self.request.user).leases
        # return Lease.objects.filter(id__in=leases)
        lease = Lease.objects.get(id=self.kwargs['lease_id'])        
        return User.objects.filter(account__leases__in=[lease])

class LeaseViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Lease.objects.all()
    serializer_class = LeaseSerializer

    def get_serializer_context(self):
        return {'user': self.request.user.username}

    def get_queryset(self):
        # leases = Account.objects.get(user=self.request.user).leases
        # return Lease.objects.filter(id__in=leases)
        return Account.objects.get(user=self.request.user).leases.all()

class ChatMessageViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer

    def get_queryset(self):
        return ChatMessage.objects.filter(lease=get_lease(self.request.user))

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

    def get_queryset(self):
        return Card.objects.filter(lease=get_lease(self.request.user)).order_by('-time')

    # @action(methods=['post'], detail=True, permission_classes=[permissions.IsAuthenticated])
    # def like(self, request, card_id=None):
    #     print (id)

@api_view(['POST'])
def addhousefrompost(request):
    l = Lease.objects.get(id=10)
    # l = Lease.objects.get(id=get_lease(request.user).id)
    r = Room(
        name=request.data['room_name'],
        squarefeet=request.data['square_footage'],
        lease=l,
        num_users=request.data['number_of_residents'],
        hasbathroom=request.data['has_bathroom'],
        hasawkwardlayout=request.data['has_awkward_layout'],
        hascloset=request.data['has_closet']
    )
    r.save()
    if l.rent:
        rooms = Room.objects.filter(lease=l)
        totalsqft = rooms.aggregate(Sum('squarefeet'))['squarefeet__sum']
        personcounthouse = rooms.aggregate(Sum('num_users'))['num_users__sum']
        change = 0
        for room in rooms:
            rent = calculate_rent_for_room(
                l.rent,
                l.rentscalefactor,
                room.squarefeet,
                totalsqft,
                rooms.count(),
                room.num_users,
                personcounthouse,
                (1+.05*room.hasbathroom+.05*room.hascloset-.05*room.hasawkwardlayout)
            )
            flooredrent = 5*floor(rent/5)
            change += rent-flooredrent
            room.rent = flooredrent
            room.save()
        roomsum = 0
        for room in Room.objects.filter(lease=l):
            roomsum += room.rent * room.num_users
        change = float(l.rent) - float(roomsum) #5*ceil(change/5)
        sortedrooms = sorted(rooms, key=attrgetter('rent'))
        while change > 5:
            for room in sortedrooms:
                # print (str(change)+" "+str(room.num_users))
                if change >= 5*room.num_users:
                    room.rent = room.rent + 5
                    change -= 5*room.num_users
                    room.save()
        while change:
            for room in sortedrooms:
                if change:
                    room.rent = room.rent + change
                    change = 0
                    room.save()
    return Response(status=status.HTTP_200_OK)

@api_view(['POST'])
def calculateRent(request):
    l = Lease.objects.get(id=get_lease(request.user).id)
    l.rent = request.data['total_rent']
    l.includecommonarea = request.data['include_common_space']
    l.rentscalefactor = float(request.data['common_space_importance'])
    l.save()
    rooms = Room.objects.filter(lease=l)
    # print (rooms.count())
    totalsqft = rooms.aggregate(Sum('squarefeet'))['squarefeet__sum']
    personcounthouse = rooms.aggregate(Sum('num_users'))['num_users__sum']
    # print (totalsqft)
    change = 0
    for room in rooms:
        rent = calculate_rent_for_room(
            l.rent,
            l.rentscalefactor,
            room.squarefeet,
            totalsqft,
            rooms.count(),
            room.num_users,
            personcounthouse,
            (1+.05*room.hasbathroom+.05*room.hascloset-.05*room.hasawkwardlayout)
        )
        flooredrent = 5*floor(rent/5)
        change += rent-flooredrent
        room.rent = flooredrent
        room.save()
    roomsum = 0
    for room in Room.objects.filter(lease=l):
        roomsum += room.rent * room.num_users
    change = float(l.rent) - float(roomsum) #5*ceil(change/5)
    sortedrooms = sorted(rooms, key=attrgetter('rent'))
    while change > 5:
        for room in sortedrooms:
            # print (str(change)+" "+str(room.num_users))
            if change >= 5*room.num_users:
                room.rent = room.rent + 5
                change -= 5*room.num_users
                room.save()
    while change:
        for room in sortedrooms:
            if change:
                room.rent = room.rent + change
                change = 0
                room.save()

    return Response(status=status.HTTP_200_OK)

@api_view(['POST'])
def card_list_view(request, card_id):
    # print(request.data['title'])
    # cards = Card.objects.all()
    # serializer = CardSerializer(cards)
    # return Response(serializer.data)

    # card = Card.objects.get(id=card_id)
    # hc = HouseCard.objects.get(basecard=card)
    # print (request.user)
    # hc.likes.add(request.user)
    # hc.save()

    # print ("hello there")
    return feed(request)

@api_view(['POST'])
def changeUserCurrentLease(request):
    tenant = Tenant.objects.get(user__username=request.user)
    l = Lease.objects.get(id=request.data['lease_id'])
    # print (l)
    tenant.current_lease = l
    tenant.save()
    # print (tenant.user.username)
    return Response(status=status.HTTP_200_OK)

@api_view(['POST'])
def createChatMessage(request):
    # print (request.data)
    # l = Lease.objects.get(id=request.data['lease_id'])
    l = get_lease(request.user)
    chat = ChatMessage(
        lease=l,
        message=request.data['message'],
        poster=request.user
    )
    chat.save()
    return Response(status=status.HTTP_200_OK)

@api_view(['POST'])
def createCard(request):
    l = Lease.objects.get(id=10)
    # l = get_lease(request.user)
    c = Card(title=request.data['title'], lease=l)
    c.save()
    if request.data['type'] == 'announcement':
        hc = HouseCard(basecard=c, poster=request.user)
        hc.save()
        a = Announcement(card=hc)
        a.save()
    elif request.data['type'] == 'payment':
        recipient = User.objects.get(username=request.data['recipient'])
        uc = UserCard(basecard=c, poster=request.user, recipient=recipient)
        uc.save()
        p = PaymentRequest(card=uc, amount=request.data['amount'])
        p.save()
    elif request.data['type'] == 'task':
        hc = HouseCard(basecard=c, poster=request.user)
        hc.save()
        assignee = User.objects.get(username=request.data['assignee'])
        t = Task(card=hc, assignee=assignee)
        t.save()
    elif request.data['type'] == 'event':
        hc = HouseCard(basecard=c, poster=request.user)
        hc.save()
        e = Event(card=hc, eventdate=request.data['eventdate'], eventtime=request.data['eventtime'])
        e.save()
    elif request.data['type'] == 'vote':
        hc = HouseCard(basecard=c, poster=request.user)
        hc.save()
        v = Vote(card=hc)
        v.save()
    # return feed(request)
    return Response(status=status.HTTP_200_OK)

# class AnnouncementViewSet(viewsets.ModelViewSet):
#     permission_classes = [permissions.IsAuthenticated]
#     queryset = Announcement.objects.all()
#     serializer_class = AnnouncementSerializer

#     def get_serializer_context(self):
#         return {'user': self.request.user.username}

    # @action(methods=['post'], detail=True, permission_classes=[permissions.IsAuthenticated])
    # def like(self, request, card_id=None):
    #     print (id)

# class CardIdViewSet(viewsets.ModelViewSet):
#     permission_classes = [permissions.IsAuthenticated]
#     queryset = Card.objects.all()
#     serializer_class = CardSerializer

#     def get_serializer_context(self):
#         return {'user': self.request.user.username}

@login_required
# @require_POST
def postLike(request, card_id):
    # if request.method == 'POST':
    card = Card.objects.get(id=card_id)
    hc = HouseCard.objects.get(basecard=card)
    # print (request.user)
    hc.likes.add(request.user)
    hc.save()
    # print ("hello there")
    return feed(request)

@login_required
def settings(request):
    current_house = get_lease(request.user)
    return render(request, 'settings.html', context={
        'current_house':current_house,
        'houses':get_houses(request)})

@login_required
def accountSettings(request):
    # print (request.method)
    if request.method == 'POST':
        # print ("here?")
        form = AccountSettingsForm(request.user, request.POST)
        if form.is_valid():
            # print ("here")
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
                if not Tenant.objects.filter(user__id=request.user.id).exists():
                    tenant = Tenant(user=request.user)
                    tenant.save()
            elif account_type == 'L':
                if not Landlord.objects.filter(user__id=request.user.id).exists():
                    landlord = Landlord(user=request.user)
                    landlord.save()
            return redirect('/house-settings/')
    # else:
    #     form = AccountSettingsForm(request.user)
    # print("no here")
    form = AccountSettingsForm(request.user)
    return render(request, 'account-settings.html', context={'form':form, 'houses':get_houses(request), 'current_house':get_lease(request.user)})

@login_required
def houseIdSettings(request, house_id):
    current_house = get_lease(request.user)
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
        'form':form,
        'current_house':current_house,
        'houses':get_houses(request)
    })

@login_required
def switchtohouse(request, house_id):
    tenant = Tenant.objects.get(user__id=request.user.id)
    l = Lease.objects.get(id=house_id)
    tenant.current_lease = l
    tenant.save()

    return redirect('/feed/')

@login_required
def houseSettings(request):
    # if request.method == 'POST':
    #     form = HouseSettingsForm(request.user, request.POST)
    #     if form.is_valid():
    #         return redirect('/house-settings/')
    # else:
    #     form = HouseSettingsForm(request.user)
    houses = get_houses(request)
    current_house = get_lease(request.user)
    # if houses:
    #     print("shet")
    return render(request, 'house_settings.html', context={
        'houses':houses,
        'current_house':current_house,
        'houses':get_houses(request)
    })

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
    return render(request, 'add_house.html', context={'new_house_form':new_house_form, 'invite_form':invite_form, 'houses':get_houses(request), 'current_house':get_lease(request.user)})

@login_required
def rentCalculation(request):
    initial = {'include_common_space':True}
    l = Lease.objects.get(id=get_lease(request.user).id)
    if l.rentscalefactor:
        initial['common_space_importance'] = l.rentscalefactor
    if l.rent:
        initial['total_rent'] = l.rent
    if request.method == 'POST':
        if 'cal_btn' in request.POST:
            cal_form = RentCalculator(request.user, request.POST, initial=initial)
            if cal_form.is_valid():
                l.rent = cal_form.cleaned_data['total_rent']
                l.includecommonarea = cal_form.cleaned_data['include_common_space']
                l.rentscalefactor = cal_form.cleaned_data['common_space_importance']
                l.save()
                rooms = Room.objects.filter(lease=l)
                # print (rooms.count())
                totalsqft = rooms.aggregate(Sum('squarefeet'))['squarefeet__sum']
                personcounthouse = rooms.aggregate(Sum('num_users'))['num_users__sum']
                # print (totalsqft)
                change = 0
                for room in rooms:
                    rent = calculate_rent_for_room(
                        l.rent,
                        l.rentscalefactor,
                        room.squarefeet,
                        totalsqft,
                        rooms.count(),
                        room.num_users,
                        personcounthouse,
                        (1+.05*room.hasbathroom+.05*room.hascloset-.05*room.hasawkwardlayout)
                    )
                    flooredrent = 5*floor(rent/5)
                    change += rent-flooredrent
                    room.rent = flooredrent
                    room.save()
                roomsum = 0
                for room in Room.objects.filter(lease=l):
                    roomsum += room.rent * room.num_users
                change = float(l.rent) - float(roomsum) #5*ceil(change/5)
                sortedrooms = sorted(rooms, key=attrgetter('rent'))
                while change > 5:
                    for room in sortedrooms:
                        # print (str(change)+" "+str(room.num_users))
                        if change >= 5*room.num_users:
                            room.rent = room.rent + 5
                            change -= 5*room.num_users
                            room.save()
                while change:
                    for room in sortedrooms:
                        if change:
                            room.rent = room.rent + change
                            change = 0
                            room.save()

        elif 'add_btn' in request.POST:
            add_form = AddRoomForm(request.user, request.POST)
            if add_form.is_valid():
                # l = Lease.objects.get(id=get_lease(request.user).id)
                r = Room(
                    name=add_form.cleaned_data['room_name'],
                    squarefeet=add_form.cleaned_data['square_footage'],
                    lease=l,
                    num_users=add_form.cleaned_data['number_of_residents'],
                    hasbathroom=add_form.cleaned_data['has_bathroom'],
                    hasawkwardlayout=add_form.cleaned_data['has_awkward_layout'],
                    hascloset=add_form.cleaned_data['has_closet']
                )
                r.save()
                if l.rent:
                    rooms = Room.objects.filter(lease=l)
                    totalsqft = rooms.aggregate(Sum('squarefeet'))['squarefeet__sum']
                    personcounthouse = rooms.aggregate(Sum('num_users'))['num_users__sum']
                    change = 0
                    for room in rooms:
                        rent = calculate_rent_for_room(
                            l.rent,
                            l.rentscalefactor,
                            room.squarefeet,
                            totalsqft,
                            rooms.count(),
                            room.num_users,
                            personcounthouse,
                            (1+.05*room.hasbathroom+.05*room.hascloset-.05*room.hasawkwardlayout)
                        )
                        flooredrent = 5*floor(rent/5)
                        change += rent-flooredrent
                        room.rent = flooredrent
                        room.save()
                    roomsum = 0
                    for room in Room.objects.filter(lease=l):
                        roomsum += room.rent * room.num_users
                    change = float(l.rent) - float(roomsum) #5*ceil(change/5)
                    sortedrooms = sorted(rooms, key=attrgetter('rent'))
                    while change > 5:
                        for room in sortedrooms:
                            # print (str(change)+" "+str(room.num_users))
                            if change >= 5*room.num_users:
                                room.rent = room.rent + 5
                                change -= 5*room.num_users
                                room.save()
                    while change:
                        for room in sortedrooms:
                            if change:
                                room.rent = room.rent + change
                                change = 0
                                room.save()

    initial = {'include_common_space':True}
    l = Lease.objects.get(id=get_lease(request.user).id)
    if l.rentscalefactor:
        initial['common_space_importance'] = l.rentscalefactor
    if l.rent:
        initial['total_rent'] = l.rent
    
    rooms = get_rooms(request)
    add_form = AddRoomForm(request.user)
    cal_form = RentCalculator(request.user, initial=initial)
    current_house = get_lease(request.user)
    return render(request, 'rentcalculator.html', context={
        'rooms':rooms,
        'cal_form':cal_form,
        'add_form':add_form,
        'current_house':current_house,
        'houses':get_houses(request)
    })

@login_required
def tasks(request):
    # form = RentCalculator(request.user)
    tenant = Tenant.objects.get(user__username=request.user)
    lease = tenant.current_lease
    tasks = Task.objects.filter(Q(card__basecard__lease=lease))
    return render(request, 'tasks.html', context={'tasks':tasks, 'houses':get_houses(request), 'current_house':get_lease(request.user)})

@login_required
def calendar(request):
    # form = RentCalculator(request.user)
    tenant = Tenant.objects.get(user__username=request.user)
    lease = tenant.current_lease
    events = Event.objects.filter(Q(card__basecard__lease=lease))
    return render(request, 'calendar.html', context={'events':events, 'houses':get_houses(request), 'current_house':get_lease(request.user)})

@login_required
def chat(request):
    if request.method == 'POST':
        form = ChatForm(request.user, request.POST)
        if form.is_valid():
            chat = ChatMessage(
                lease=get_lease(request.user),
                message=form.cleaned_data['message'],
                poster=request.user
            )
            chat.save()
        
    chats = get_chats(request)
    form = ChatForm(request.user)

    tenants = User.objects.filter(account__leases__in=[get_lease(request.user)])

    return render(request, 'chat.html', context={
        'chats':chats,
        'form':form,
        'houses':get_houses(request),
        'current_house':get_lease(request.user),
        'tenants':tenants
    })

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
    current_house = get_lease(request.user)
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
        'vte_form':vte_form,
        'current_house':current_house,
        'houses':get_houses(request)
    })

def signup(request):
    # if request.user.is_authenticated:
    if request.method == 'POST':
        form = SignUpForm(request.POST)
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

            account_type = form.cleaned_data.get('user_type')
            # raw_password = form.cleaned_data.get('password1')
            # user = authenticate(username=username, password=raw_password)

            # login(request, user)
            # TODO: extend the form to cover the rest of this lol
            if Account.objects.filter(user__id=user.id).exists():
                account = Account.objects.get(user__id=user.id)
                account.account_type = account_type
            else:
                account = Account(user=user, account_type=account_type)
            account.save()
            # evl = Tenant.objects.get(user__username='eric')
            # lease = evl.current_lease
            # account.leases.add(lease)
            if account_type == 'T':
                tenant = Tenant(user=user)
                tenant.save()
            elif account_type == 'L':
                landlord = Landlord(user=user)
                landlord.save()
            return redirect('/house-settings/')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})
    # else:
    #     return feed(request)

