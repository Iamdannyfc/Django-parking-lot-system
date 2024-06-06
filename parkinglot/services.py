from .models import ParkingSlot, Vehicle, Floor, ParkingLot


# Helper functions
# These functions assist with operations related to parking slots and vehicles


def slot_list_for_vehicle_type(vehicle_type):
    """
    Return a list of slot numbers suitable for the given vehicle type.
    """
    if vehicle_type.title() == "Truck":
        return [1]
    elif vehicle_type.title() == "Bike":
        return [2, 3]
    else:
        return []


def find_available_slot(slot_list_for_vehicle_type):
    """
    Find the first available slot for the given slot list suitable for the vehicle type.
    """
    try:
        # If slot list is not empty, filter available slots for the given slot numbers
        if slot_list_for_vehicle_type:
            return (
                ParkingSlot.objects.filter(
                    is_available=True, number__in=slot_list_for_vehicle_type
                ).first(),
                None,
            )
        else:
            # If slot list is empty, find available slots excluding specific numbers
            return (
                ParkingSlot.objects.filter(is_available=True)
                .exclude(number__in=[1, 2, 3])
                .first()
            ), None
    except:

        return None, {"error": f"Error finding available slot"}


def split_ticket_for_unparking(ticket_id):
    """
    Split the ticket ID to find the parking lot, floor, and slot.
    Validate and return the slot or an error message if not found.
    """
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


# Service functions
# These functions handle the core logic of creating, parking, and unparking operations


def create_parking_lot(serializer, parking_lot, max_floors, max_slots):
    """
    Create floors and parking slots for the given parking lot.
    """
    try:
        for floor_number in range(1, max_floors + 1):
            floor = Floor.objects.create(number=floor_number, parking_lot=parking_lot)
            for slot_number in range(1, max_slots + 1):
                ParkingSlot.objects.create(
                    number=slot_number, is_available=True, floor=floor
                )
        return {
            "message": "Parking lot created successfully",
            "data": serializer.data,
        }, None
    except:
        print(f"Error creating parking lot")
        return None, {"error": "An error occurred while creating the parking lot"}


def park_vehicle(vehicle_serializer, available_slot):
    """
    Park a vehicle in the given available slot.
    """
    try:
        vehicle = vehicle_serializer.save()
        available_slot.vehicle = vehicle
        available_slot.is_available = False
        available_slot.save()
        return {
            "message": f"Vehicle parked successfully with TicketID: {available_slot.floor.parking_lot.parking_lot_id}_{available_slot.floor.number}_{available_slot.number}"
        }, None
    except:
        print(f"Error parking vehicle")
        return None, {"error": "An error occurred while parking the vehicle"}


def unpark_vehicle(slot):
    """
    Unpark a vehicle from the given slot.
    """
    try:
        slot.vehicle.delete()
        slot.vehicle = None
        slot.is_available = True
        slot.save()
        return {"message": "Vehicle unparked successfully"}, None
    except:
        print(f"Error unparking vehicle")
        return None, {"error": "An error occurred while unparking the vehicle"}


# Display functions
# These functions handle the logic for displaying information about free and occupied slots


def display_free_slots(slot_free_number):
    """
    Display free slots for the given slot numbers on each floor.
    """
    response_data = []

    try:
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
            free_slots_str = ", ".join(str(slot) for slot in free_slots_list)

            if free_slots_str:
                response_data.append(
                    {
                        "floor": floor.number,
                        "free_slots": free_slots_str,
                        "parking_lot_id": floor.parking_lot.parking_lot_id,
                    }
                )
    except:
        print(f"Error displaying free slots")
        return None, {"error": "An error occurred while displaying free slots"}

    return response_data, None


def find_available_slot_count(slot_free_number):
    """
    Find the count of available slots for the given slot numbers.
    """
    try:
        if slot_free_number:
            free_slots_count = ParkingSlot.objects.filter(
                is_available=True, number__in=slot_free_number
            ).count()
        else:
            free_slots_count = (
                ParkingSlot.objects.filter(is_available=True)
                .exclude(number__in=[1, 2, 3])
                .count()
            )
        return free_slots_count, None
    except:
        print(f"Error finding available slot count")
        return None, {"error": "An error occurred while finding available slot count"}


def display_occupied_slots(slot_lists_for_vehicle_type, list_vehicle_ids):
    """
    Display occupied slots for the given slot numbers and vehicle IDs on each floor.
    """
    response_data = []

    try:
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
            occupied_slots_list = [slot.number for slot in occupied_slots]
            occupied_slots_str = ", ".join(str(slot) for slot in occupied_slots_list)

            if occupied_slots_str:
                response_data.append(
                    {
                        "occupied_slots": occupied_slots_str,
                        "floor": floor.number,
                        "parking_lot_id": floor.parking_lot.parking_lot_id,
                    }
                )
    except:
        print(f"Error displaying occupied slots")
        return None, {"error": "An error occurred while displaying occupied slots"}

    return response_data, None
