from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import ParkingSlot, Vehicle, Floor, ParkingLot
from .serializers import VehicleSerializer, ParkingLotSerializer


# You have to create parking
class ParkingLotCreateView(APIView):
    def post(self, request):
        serializer = ParkingLotSerializer(data=request.data)
        print(serializer.is_valid(), request.data)
        if serializer.is_valid():
            parking_lot = serializer.save()

            # Create Floors and Parking Slots based on max_floors and max_slots
            max_floors = parking_lot.max_floors
            max_slots = parking_lot.max_slots

            for floor_number in range(1, max_floors + 1):
                floor = Floor.objects.create(
                    number=floor_number, parking_lot=parking_lot
                )
                for slot_number in range(1, max_slots + 1):
                    ParkingSlot.objects.create(
                        number=slot_number, is_available=True, floor=floor
                    )

            return Response(
                {"message": serializer.data}, status=status.HTTP_201_CREATED
            )
        return Response(
            {"error": "An error occured, unable to create a parking lot"},
            status=status.HTTP_400_BAD_REQUEST,
        )


# wait, lemme work on parking
class ParkVehicleView(APIView):
    def post(self, request):
        vehicle_data = request.data
        vehicle_type = vehicle_data.get("_type")
        print(vehicle_type)
        slot_free_number = None

        if vehicle_type.title() == "Truck":
            slot_free_number = [1]
        elif vehicle_type.title() == "Bike":
            slot_free_number = [2, 3]

        if not vehicle_data:
            return Response(
                {"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Find an available slot
        if slot_free_number:
            available_slot = ParkingSlot.objects.filter(
                is_available=True, number__in=slot_free_number
            ).first()
        else:
            available_slot = (
                ParkingSlot.objects.filter(is_available=True)
                .exclude(number__in=[1, 2, 3])
                .first()
            )
        print(available_slot)

        if not available_slot:
            return Response(
                {"error": "No available parking slots"},
                status=status.HTTP_404_NOT_FOUND,
            )

        vehicle_serializer = VehicleSerializer(data=vehicle_data)

        if vehicle_serializer.is_valid():
            vehicle = vehicle_serializer.save()
            available_slot.vehicle = vehicle
            available_slot.is_available = False
            available_slot.save()
            return Response(
                {
                    "message": f"Vehicle parked successfully with TicketID:    {available_slot.floor.parking_lot.parking_lot_id}_{available_slot.floor.number}_{available_slot.number}"
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "An error occured"}, status=status.HTTP_400_BAD_REQUEST
            )


class UnparkVehicleView(APIView):
    def post(self, request):
        ticket_id = request.data.get("ticket_id")

        if not ticket_id:
            return Response(
                {"error": "Ticket ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Split the ticket ID
        try:
            parking_lot_id, floor_number, slot_number = ticket_id.split("_")
        except:
            return Response(
                {"error": "Invalid ticket ID format"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            parking_lot = ParkingLot.objects.get(parking_lot_id=parking_lot_id)
        except:
            return Response(
                {"error": "Parking lot not found"}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            floor = Floor.objects.get(parking_lot=parking_lot, number=floor_number)
        except:
            return Response(
                {"error": "Floor not found"}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            slot = ParkingSlot.objects.get(floor=floor, number=slot_number)
        except:
            return Response(
                {"error": "Parking slot not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if slot.vehicle is None:
            return Response(
                {"error": "No vehicle parked in this slot"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Unpark the vehicle
        slot.vehicle.delete()
        slot.vehicle = None

        slot.is_available = True
        slot.save()

        return Response(
            {"message": "Vehicle unparked successfully"}, status=status.HTTP_200_OK
        )


class DisplayFreeCountView(APIView):
    def get(self, request, vehicle_type):
        slot_free_number = None
        if vehicle_type.title() == "Truck":
            slot_free_number = [1]
        elif vehicle_type.title() == "Bike":
            slot_free_number = [2, 3]

        # Find free slots for the given vehicle type
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

        return Response(
            {"free_slots_count": free_slots_count}, status=status.HTTP_200_OK
        )


class DisplayFreeSlotsView(APIView):
    def get(self, request, vehicle_type):
        slot_free_number = None
        if vehicle_type.title() == "Truck":
            slot_free_number = [1]
        elif vehicle_type.title() == "Bike":
            slot_free_number = [2, 3]

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

            response_data.append(
                {
                    "floor": floor.number,
                    "free_slots": free_slots_str,
                    "parking_lot_id": floor.parking_lot.parking_lot_id,
                }
            )

        # response_message = "\n".join(
        #    [f"Free slots for {vehicle_type.title()} on Floor {data['floor']}: {data['free_slots']}" for data in response_data]
        # )

        return Response({"message": response_data}, status=status.HTTP_200_OK)


class DisplayOccupiedSlotsView(APIView):
    def get(self, request, vehicle_type):

        slot_free_number = None
        if vehicle_type.title() == "Truck":
            slot_free_number = [1]
        elif vehicle_type.title() == "Bike":
            slot_free_number = [2, 3]

        response_data = []
        # find occupied vehicle ids
        list_vehicles = Vehicle.objects.filter(_type=vehicle_type.title())
        list_vehicle_ids = [vehicle for vehicle in list_vehicles]
        # print(list_vehicle_ids, list_vehicles)

        # Iterate over all floors
        floors = Floor.objects.all()

        for floor in floors:

            # Find occupied slots for the given vehicle type on the current floor
            if slot_free_number:
                occupied_slots = ParkingSlot.objects.filter(
                    is_available=False,
                    number__in=slot_free_number,
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

            response_data.append(
                {"floor": floor.number, "occupied_slots": occupied_slots_str}
            )

        # response_message = "\n".join(
        #  [f"Occupied slots for {vehicle_type.title()} on Floor {data['floor']}: {data['occupied_slots']}" for data in response_data]
        # )

        return Response({"message": response_data}, status=status.HTTP_200_OK)
