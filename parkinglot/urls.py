from django.views.decorators.cache import cache_page
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT


from django.urls import path
from .views import (
    ParkingLotCreateView,
    ParkVehicleView,
    UnparkVehicleView,
    DisplayFreeCountView,
    DisplayOccupiedSlotsView,
    DisplayFreeSlotsView,
)

CACHE_TTL = getattr(settings, "CACHE_TTL", DEFAULT_TIMEOUT)

urlpatterns = [
    path(
        "create-parking-lot/", ParkingLotCreateView.as_view(), name="create-parking-lot"
    ),
    path("park-vehicle/", ParkVehicleView.as_view(), name="park-vehicle"),
    path("unpark-vehicle/", UnparkVehicleView.as_view(), name="unpark-vehicle"),
    path(
        "free-count/<str:vehicle_type>/",
        cache_page(CACHE_TTL)(DisplayFreeCountView.as_view()),
        name="display-free-count",
    ),
    path(
        "free-slots/<str:vehicle_type>/",
        cache_page(CACHE_TTL)(DisplayFreeSlotsView.as_view()),
        name="display-free-slots",
    ),
    path(
        "occupied-slots/<str:vehicle_type>/",
        cache_page(CACHE_TTL)(DisplayOccupiedSlotsView.as_view()),
        name="display-occupied-slots",
    ),
]
