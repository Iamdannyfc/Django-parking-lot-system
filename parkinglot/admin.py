from django.contrib import admin
from .models import ParkingLot, Floor, Vehicle, ParkingSlot

admin.site.register(ParkingLot)
admin.site.register(Floor)
admin.site.register(Vehicle)
admin.site.register(ParkingSlot)
