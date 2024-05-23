from django.urls import path
from .views import (
    ParkingLotCreateView,
    ParkVehicleView,
    UnparkVehicleView,
    DisplayFreeCountView,
)

urlpatterns = [
    path(
        "create-parking-lot/", ParkingLotCreateView.as_view(), name="create-parking-lot"
    ),
    path("park-vehicle/", ParkVehicleView.as_view(), name="park-vehicle"),
    path("unpark-vehicle/", UnparkVehicleView.as_view(), name="unpark-vehicle"),
    path(
        "free-slots/<str:vehicle_type>/",
        DisplayFreeCountView.as_view(),
        name="display-free-count",
    ),
]
