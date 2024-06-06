from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import ParkingSlot, Vehicle, Floor, ParkingLot
from .serializers import VehicleSerializer, ParkingLotSerializer, ParkingSlotSerializer
from .services import *

# This are vehicles you can park here
ALLOWED_VEHICLES = ["Car", "Truck", "Bike"]

# REQUEST codes
BAD_REQUEST = status.HTTP_400_BAD_REQUEST
CREATED_REQUEST = status.HTTP_201_CREATED
NOT_FOUND_REQUEST = status.HTTP_404_NOT_FOUND
OK_REQUEST = status.HTTP_200_OK


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
            parking_lot_creation_response, err = create_parking_lot(
                serializer, parking_lot, max_floors, max_slots
            )

            if err:
                return Response(
                    err,
                    status=BAD_REQUEST,
                )

            return Response(
                parking_lot_creation_response,
                status=CREATED_REQUEST,
            )

        return Response(
            {"error": "An error occurred, unable to create a parking lot"},
            status=BAD_REQUEST,
        )


# wait, lemme work on parking
class ParkVehicleView(APIView):
    def post(self, request):
        vehicle_data = request.data
        vehicle_type = vehicle_data.get("_type")
        # print(vehicle_type)
        slot_lists_for_vehicle_type = slot_list_for_vehicle_type(vehicle_type)

        if (not vehicle_data) or (not (vehicle_type.title() in ALLOWED_VEHICLES)):
            return Response({"error": "Invalid data"}, status=BAD_REQUEST)

        # Find an available slot
        available_slot, err = find_available_slot(slot_lists_for_vehicle_type)
        # print(available_slot)

        if err:
            return Response(
                err,
                status=NOT_FOUND_REQUEST,
            )

        if not available_slot:
            return Response(
                {"error": "No available parking slots"},
                status=NOT_FOUND_REQUEST,
            )

        vehicle_serializer = VehicleSerializer(data=vehicle_data)

        if vehicle_serializer.is_valid():
            # Park the vehicle
            park_vehicle_response, err = park_vehicle(
                vehicle_serializer, available_slot
            )

            if err:
                return Response(
                    err,
                    status=BAD_REQUEST,
                )

            return Response(
                park_vehicle_response,
                status=OK_REQUEST,
            )
        else:
            return Response({"error": "An error occured"}, status=BAD_REQUEST)


class UnparkVehicleView(APIView):
    def post(self, request):
        ticket_id = request.data.get("ticket_id")

        if not ticket_id:
            return Response({"error": "Ticket ID is required"}, status=BAD_REQUEST)

        # Split the ticket ID
        slot, err = split_ticket_for_unparking(ticket_id)

        if err:
            return Response(err, status=BAD_REQUEST)

        # Unpark the vehicle in the slot
        unpark_response, err = unpark_vehicle(slot)
        if err:
            return Response(
                err,
                status=BAD_REQUEST,
            )

        return Response(unpark_response, status=OK_REQUEST)


class DisplayFreeCountView(APIView):
    def get(self, request, vehicle_type):
        slot_lists_for_vehicle_type = slot_list_for_vehicle_type(vehicle_type)

        # How many are they?
        free_slots_count, err = find_available_slot_count(slot_lists_for_vehicle_type)
        if err:
            return Response(
                err,
                status=BAD_REQUEST,
            )

        return Response({"free_slots_count": free_slots_count}, status=OK_REQUEST)


class DisplayFreeSlotsView(APIView):
    def get(self, request, vehicle_type):

        slot_lists_for_vehicle_type = slot_list_for_vehicle_type(vehicle_type)

        display_free_slots_response, err = display_free_slots(
            slot_lists_for_vehicle_type
        )
        if err:
            return Response(
                err,
                status=BAD_REQUEST,
            )
        return Response({"message": display_free_slots_response}, status=OK_REQUEST)


class DisplayOccupiedSlotsView(APIView):
    def get(self, request, vehicle_type):

        slot_lists_for_vehicle_type = slot_list_for_vehicle_type(vehicle_type)

        list_vehicles = Vehicle.objects.filter(_type=vehicle_type.title())
        list_vehicle_ids = [vehicle for vehicle in list_vehicles]
        # print(list_vehicle_ids, list_vehicles)

        response_data, err = display_occupied_slots(
            slot_lists_for_vehicle_type, list_vehicle_ids
        )
        if err:
            return Response(
                err,
                status=BAD_REQUEST,
            )

        return Response({"message": response_data}, status=OK_REQUEST)
