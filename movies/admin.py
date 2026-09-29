from django.contrib import admin
from .models import (
    UserProfile,
    Vendor,
    Branch,
    Hall,
    Seat,
    Movie,
    Show,
    ShowSeat,
    Booking,
    BookingSeat,
)

admin.site.register(UserProfile)
admin.site.register(Vendor)
admin.site.register(Branch)
admin.site.register(Hall)
admin.site.register(Seat)
admin.site.register(Movie)
admin.site.register(Show)
admin.site.register(ShowSeat)
admin.site.register(Booking)
admin.site.register(BookingSeat)