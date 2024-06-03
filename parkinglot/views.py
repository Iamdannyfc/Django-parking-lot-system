from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import ParkingSlot, Vehicle, Floor, ParkingLot
from .serializers import VehicleSerializer, ParkingLotSerializer, ParkingSlotSerializer
from .services import *


# You have to create parking
class ParkingLotCreateView(APIView):
    def post(self, request):
        serializer = ParkingLotSerializer(data=request.data)

        if serializer.is_valid():
            parking_lot = serializer.save()

            # What is the max_floors and max_slots you want
            max_floors = parking_lot.max_floors
            max_slots = parking_lot.max_slots

            # Create the parking lot based on max_floors and max_slots
            parking_lot_creation_response = create_parking_lot(
                serializer, parking_lot, max_floors, max_slots
            )

            return Response(
                parking_lot_creation_response,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {"error": "An error occurred, unable to create a parking lot"},
            status=status.HTTP_400_BAD_REQUEST,
        )


# wait, lemme work on parking
class ParkVehicleView(APIView):
    def post(self, request):
        vehicle_data = request.data
        vehicle_type = vehicle_data.get("_type")
        # print(vehicle_type)
        slot_free_number = slot_list_for_vehicle_type(vehicle_type)

        if not vehicle_data:
            return Response(
                {"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Find an available slot
        available_slot = find_available_slot(slot_free_number)
        # print(available_slot)

        if not available_slot:
            return Response(
                {"error": "No available parking slots"},
                status=status.HTTP_404_NOT_FOUND,
            )

        vehicle_serializer = VehicleSerializer(data=vehicle_data)

        if vehicle_serializer.is_valid():
            # Park the damn vehicle
            park_vehicle_response = park_vehicle(vehicle_serializer, available_slot)

            return Response(
                park_vehicle_response,
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
        slot, err = split_ticket_for_unparking(ticket_id)

        if err:
            return Response(err, status=status.HTTP_400_BAD_REQUEST)

        # Unpark the vehicle in the slot
        unpark_vehicle(slot)

        return Response(
            {"message": "Vehicle unparked successfully"}, status=status.HTTP_200_OK
        )


class DisplayFreeCountView(APIView):
    def get(self, request, vehicle_type):
        slot_free_number = slot_list_for_vehicle_type(vehicle_type)

        # How many are they?
        free_slots_count = find_available_slot_count(slot_free_number)

        return Response(
            {"free_slots_count": free_slots_count}, status=status.HTTP_200_OK
        )


class DisplayFreeSlotsView(APIView):
    def get(self, request, vehicle_type):

        slot_free_number = slot_list_for_vehicle_type(vehicle_type)

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
                {
                    "floor": floor.number,
                    "occupied_slots": occupied_slots_str,
                    "parking_lot_id": floor.parking_lot.parking_lot_id,
                }
            )

        # response_message = "\n".join(
        #  [f"Occupied slots for {vehicle_type.title()} on Floor {data['floor']}: {data['occupied_slots']}" for data in response_data]
        # )

        return Response({"message": response_data}, status=status.HTTP_200_OK)
