from django.test import TestCase
from .models import ParkingLot, Floor, ParkingSlot, Vehicle


class ParkingLotModelTests(TestCase):
    def setUp(self):
        self.parking_lot = ParkingLot.objects.create(
            max_floors=2, max_slots=3, parking_lot_id="PR1234"
        )
        self.vehicle = Vehicle.objects.create(
            _type="Car", registration_number="ABC123", color="Red"
        )

    def test_parking_lot_creation(self):
        self.assertEqual(self.parking_lot.max_floors, 2)
        self.assertEqual(self.parking_lot.max_slots, 3)
        self.assertEqual(self.parking_lot.parking_lot_id, "PR1234")

    def test_floor_creation(self):
        floor = Floor.objects.create(number=1, parking_lot=self.parking_lot)
        self.assertEqual(floor.number, 1)
        self.assertEqual(floor.parking_lot, self.parking_lot)

    def test_parking_slot_creation(self):
        floor = Floor.objects.create(number=1, parking_lot=self.parking_lot)
        parking_slot = ParkingSlot.objects.create(
            number=1, is_available=True, floor=floor
        )
        self.assertEqual(parking_slot.number, 1)
        self.assertTrue(parking_slot.is_available)
        self.assertEqual(parking_slot.floor, floor)

    def test_vehicle_creation(self):
        self.assertEqual(self.vehicle._type, "Car")
        self.assertEqual(self.vehicle.registration_number, "ABC123")
        self.assertEqual(self.vehicle.color, "Red")

    def test_parking_slot_assigned_to_vehicle(self):
        floor = Floor.objects.create(number=1, parking_lot=self.parking_lot)
        parking_slot = ParkingSlot.objects.create(
            number=1, is_available=False, floor=floor, vehicle=self.vehicle
        )
        self.assertEqual(parking_slot.vehicle, self.vehicle)
        self.assertFalse(parking_slot.is_available)
