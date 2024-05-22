from rest_framework import generics
from .models import ParkingLot
from .serializers import ParkingLotSerializer

class ParkingLotCreateView(generics.CreateAPIView):
    queryset = ParkingLot.objects.all()
    serializer_class = ParkingLotSerializer
