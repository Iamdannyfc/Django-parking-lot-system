
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
        return Response({'error': 'An error occured, unable to vreate a parking lot'}, status=status.HTTP_400_BAD_REQUEST)     
    
    
    

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
            return Response({'message': f'Vehicle parked successfully with TicketID:{available_slot.floor.parking_lot.parking_lot_id}_{available_slot.floor.number}_{available_slot.number}'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'An error occured'}, status=status.HTTP_400_BAD_REQUEST)




class UnparkVehicleView(APIView):
    def post(self, request):
        ticket_id = request.data.get('ticket_id')
        
        if not ticket_id:
            return Response({'error': 'Ticket ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Split the ticket ID
        try:
            parking_lot_id, floor_number, slot_number = ticket_id.split('_')
        except:
            return Response({'error': 'Invalid ticket ID format'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            parking_lot = ParkingLot.objects.get(parking_lot_id=parking_lot_id)
        except:
            return Response({'error': 'Parking lot not found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            floor = Floor.objects.get(parking_lot=parking_lot, number=floor_number)
        except:
            return Response({'error': 'Floor not found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            slot = ParkingSlot.objects.get(floor=floor, number=slot_number)
        except:
            return Response({'error': 'Parking slot not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if slot.vehicle is None:
            return Response({'error': 'No vehicle parked in this slot'}, status=status.HTTP_400_BAD_REQUEST)

        # Unpark the vehicle
        slot.vehicle = None
        slot.vehicle.delete()  
        slot.is_available = True
        slot.save()
        
        return Response({'message': 'Vehicle unparked successfully'}, status=status.HTTP_200_OK)


                            
