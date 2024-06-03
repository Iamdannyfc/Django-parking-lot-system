from .models import ParkingSlot, Vehicle, Floor, ParkingLot


# This are just my helper funtions
def slot_list_for_vehicle_type(vehicle_type):
    if vehicle_type.title() == "Truck":
        return [1]
    elif vehicle_type.title() == "Bike":
        return [2, 3]
    else:
        return []


def find_available_slot(slot_list_for_vehicle_type):
    print(slot_list_for_vehicle_type, 99)
    print(ParkingSlot.objects.filter(is_available=True).exclude(number__in=[1, 2, 3]))
    if not slot_list_for_vehicle_type == []:
        return ParkingSlot.objects.filter(
            is_available=True, number__in=slot_list_for_vehicle_type
        ).first()
    else:
        print("got here")
        return (
            ParkingSlot.objects.filter(is_available=True)
            .exclude(number__in=[1, 2, 3])
            .first()
        )


def find_available_slot_count(slot_free_number):

    if not slot_free_number == []:
        free_slots_count = ParkingSlot.objects.filter(
            is_available=True, number__in=slot_free_number
        ).count()
    else:
        free_slots_count = (
            ParkingSlot.objects.filter(is_available=True)
            .exclude(number__in=[1, 2, 3])
            .count()
        )
    return free_slots_count


def split_ticket_for_unparking(ticket_id):
    try:
        parking_lot_id, floor_number, slot_number = ticket_id.split("_")
    except:
        return None, {"error": "Invalid ticket ID format"}

    try:
        parking_lot = ParkingLot.objects.get(parking_lot_id=parking_lot_id)
    except:
        return None, {"error": "Parking lot not found"}

    try:
        floor = Floor.objects.get(parking_lot=parking_lot, number=floor_number)
    except:
        return None, {"error": "Floor not found"}

    try:
        slot = ParkingSlot.objects.get(floor=floor, number=slot_number)
    except:
        return None, {"error": "Parking slot not found"}
    if slot.vehicle is None:
        return None, {"error": "No vehicle parked in this slot"}
    return slot, None


# All my services functions
# Are in this place


def create_parking_lot(serializer, parking_lot, max_floors, max_slots):
    for floor_number in range(1, max_floors + 1):

        floor = Floor.objects.create(number=floor_number, parking_lot=parking_lot)
        for slot_number in range(1, max_slots + 1):
            ParkingSlot.objects.create(
                number=slot_number, is_available=True, floor=floor
            )
    return {
        "message": "Parking lot created successfully",
        "data": serializer.data,
    }


def park_vehicle(vehicle_serializer, available_slot):
    vehicle = vehicle_serializer.save()
    available_slot.vehicle = vehicle
    available_slot.is_available = False
    available_slot.save()
    return {
        "message": f"Vehicle parked successfully with TicketID:    {available_slot.floor.parking_lot.parking_lot_id}_{available_slot.floor.number}_{available_slot.number}"
    }


def unpark_vehicle(slot):
    slot.vehicle.delete()
    slot.vehicle = None

    slot.is_available = True
    slot.save()


# This are for the display