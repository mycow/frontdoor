@GET
/api/cards/
Get all cards for user's current lease


@POST
/api/card/create/
POST a new card. POST body depends on type of card:

    Type            Fields
    announcement => (type, title)
    payment      => (type, title, recipient, amount)
    task         => (type, title, assignee)
    event        => (type, title, eventdate, eventtime)
    vote         => (type, title)


@GET
/api/chats/
Get chat for current lease


@POST
/api/chat/create/
POST a new messave e.g.

    "message":"example message"


@GET
/api/leases/
Get all leases for current user


@POST
/api/lease/change/
POST A change to user's current lease e.g.

    "lease_id":3


@GET
/api/lease/users/
all users in current lease
is_self=true


@GET
/api/lease/<lease_id>/users/
all users in a lease
is_self=true


@GET
/api/rooms/
rooms in current lease


@GET
/api/lease/<lease_id>/rooms/
rooms in a lese


@POST
/api/room/add/
add a room

Fields:
    room_name
    square_footage
    number_of_residents
    has_bathroom
    has_awkward_layout
    has_closet


@POST
/api/rent/
rent calc

Fields:
    total_rent
    include_common_space
    common_space_importance

@POST
sublease req