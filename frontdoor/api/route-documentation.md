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
all users in a lease
is_self=true

@GET
/api/rooms/
rooms

@POST
rent calc

@POST
sublease req