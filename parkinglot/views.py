
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import ParkingSlot, Vehicle
from .serializers import VehicleSerializer,ParkingLotSerializer

#You have to create parking
class ParkingLotCreateView(APIView):
    def post(self, request):
        serializer = ParkingLotSerializer(data=request.data)
        if serializer.is_valid():
            parking_lot = serializer.save()
            
            # Create Floors and Parking Slots based on max_floors and max_slots
            max_floors = parking_lot.max_floors
            max_slots = parking_lot.max_slots
            
            for floor_number in range(1, max_floors + 1):
                floor = Floor.objects.create(number=floor_number, parking_lot=parking_lot)
                for slot_number in range(1, max_slots + 1):
                    ParkingSlot.objects.create(number=slot_number, is_available=True, floor=floor)
            
            return Response({'message': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)     
    
    
    

#wait, lemme work on parking 
class ParkVehicleView(APIView):
    def post(self, request):
        vehicle_data = request.data
        
        if not vehicle_data:
            return Response({'error': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)

        # Find an available slot
        available_slot = ParkingSlot.objects.filter(is_available=True).first()
        
        if not available_slot:
            return Response({'error': 'No available parking slots'}, status=status.HTTP_404_NOT_FOUND)

        vehicle_serializer = VehicleSerializer(data=vehicle_data)
        if vehicle_serializer.is_valid():
            vehicle = vehicle_serializer.save()
            available_slot.vehicle = vehicle
            available_slot.is_available = False
            available_slot.save()
            return Response({'message': 'Vehicle parked successfully', 'slot_number': available_slot.number, 'floor': available_slot.floor.number}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'An error occured'}, status=status.HTTP_400_BAD_REQUEST)



class UnparkVehicleView(APIView):
    def post(self, request):
        registration_number = request.data.get('registration_number')
        
        if not registration_number:
            return Response({'error': 'Registration number is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            vehicle = Vehicle.objects.get(registration_number=registration_number)
        except:
            return Response({'error': 'Vehicle not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            slot = ParkingSlot.objects.get(vehicle=vehicle)
        except:
            return Response({'error': 'Parking slot for this vehicle not found'}, status=status.HTTP_404_NOT_FOUND)

        # Unpark the vehicle
        slot.vehicle = None
        slot.is_available = True
        slot.save()
        vehicle.delete()

        return Response({'message': 'Vehicle unparked successfully'}, status=status.HTTP_200_OK)


