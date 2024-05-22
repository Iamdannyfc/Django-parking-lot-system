from rest_framework import serializers
from .models import ParkingLot, Floor, ParkingSlot, Vehicle

class ParkingLotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingLot
        fields = ['parking_lot_id', 'max_floors', 'max_slots']

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['_type', 'registration_number', 'color']

class ParkingSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkingSlot
        fields = ['number', 'is_available', 'vehicle', 'floor']
