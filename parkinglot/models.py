from django.db import models

# Create your models here.


class ParkingLot(models.Model):
    parking_lot_id = models.CharField(max_length=50, unique=True)
    max_floors = models.IntegerField()
    max_slots = models.IntegerField()

    def __str__(self):
        return self.parking_lot_id


class Floor(models.Model):
    number = models.IntegerField()
    parking_lot = models.ForeignKey(
        ParkingLot, on_delete=models.CASCADE, related_name="floors"
    )

    def __str__(self):
        return f"Floor {self.number} "


class Vehicle(models.Model):
    _type = models.CharField(max_length=50)
    registration_number = models.CharField(max_length=50)
    color = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.type_} - {self.registration_number}"


class ParkingSlot(models.Model):
    number = models.IntegerField()
    is_available = models.BooleanField(default=True)
    vehicle = models.ForeignKey(
        Vehicle, null=True, blank=True, on_delete=models.SET_NULL
    )
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE, related_name="slots")

    def __str__(self):
        return f"Slot {self.number} "
