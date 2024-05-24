from django.urls import path
from .views import (
    ParkingLotCreateView,
    ParkVehicleView,
    UnparkVehicleView,
    DisplayFreeCountView,
    DisplayOccupiedSlotsView,
    DisplayFreeSlotsView,
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
    path(
        "free-slots/<str:vehicle_type>/",
        DisplayFreeSlotsView.as_view(),
        name="display-free-slots",
    ),
    path(
        "occupied-slots/<str:vehicle_type>/",
        DisplayOccupiedSlotsView.as_view(),
        name="display-occupied-slots",
    ),
]
