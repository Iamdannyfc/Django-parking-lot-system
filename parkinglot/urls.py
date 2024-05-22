from django.urls import path
from .views import ParkingLotCreateView, park_vehicle

urlpatterns = [
    path('create-parking-lot/', ParkingLotCreateView.as_view(), name='create-parking-lot'),
    path('park-vehicle/', ParkVehicleView.as_view(), name='park-vehicle'),
]
