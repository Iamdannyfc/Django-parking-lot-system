from .models import ParkingSlot, Vehicle, Floor, ParkingLot


# This are just my helper funtions
#
#
def slot_list_for_vehicle_type(vehicle_type):
    if vehicle_type.title() == "Truck":
        return [1]
    elif vehicle_type.title() == "Bike":
        return [2, 3]
    else:
        return []


def find_available_slot(slot_list_for_vehicle_type):
    # print(slot_list_for_vehicle_type)
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
#


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


# This are for the displays
# All display functions are here
#


def display_free_slots(slot_free_number):
    response_data = []

    # Iterate over all floors
    floors = Floor.objects.all()
    for floor in floors:
        # Find free slots for the given vehicle type on the current floor
        if slot_free_number:
            free_slots = ParkingSlot.objects.filter(
                is_available=True, number__in=slot_free_number, floor=floor
            )
        else:
            free_slots = ParkingSlot.objects.filter(
                is_available=True, floor=floor
            ).exclude(number__in=[1, 2, 3])

        # Convert slot numbers to a comma-separated string
        free_slots_list = [slot.number for slot in free_slots]
        free_slots_str_list = [str(slot) for slot in free_slots_list]
        free_slots_str = ", ".join(free_slots_str_list)

        if free_slots_str:
            response_data.append(
                {
                    "floor": floor.number,
                    "free_slots": free_slots_str,
                    "parking_lot_id": floor.parking_lot.parking_lot_id,
                }
            )
        else:
            continue
    return response_data


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


def display_occupied_slots(slot_lists_for_vehicle_type, list_vehicle_ids):
    response_data = []
    # find occupied vehicle ids

    # Iterate over all floors
    floors = Floor.objects.all()

    for floor in floors:

        # Find occupied slots for the given vehicle type on the current floor
        if slot_lists_for_vehicle_type:
            occupied_slots = ParkingSlot.objects.filter(
                is_available=False,
                number__in=slot_lists_for_vehicle_type,
                floor=floor,
                vehicle__in=list_vehicle_ids,
            )
        else:

            occupied_slots = ParkingSlot.objects.filter(
                is_available=False, floor=floor, vehicle__in=list_vehicle_ids
            ).exclude(number__in=[1, 2, 3])

        # Convert slot numbers to a comma-separated string
        # print(occupied_slots)

        occupied_slots_list = [slot.number for slot in occupied_slots]

        occupied_slots_str_list = [str(slot) for slot in occupied_slots_list]
        occupied_slots_str = ", ".join(occupied_slots_str_list)

        if occupied_slots_str:

            response_data.append(
                {
                    "occupied_slots": occupied_slots_str,
                    "floor": floor.number,
                    "parking_lot_id": floor.parking_lot.parking_lot_id,
                }
            )
        else:
            continue
    return response_data
