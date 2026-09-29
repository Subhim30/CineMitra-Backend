from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MovieViewSet, ShowViewSet, ShowSeatViewSet, RegisterView,LoginView, BookingViewSet,VendorBranchViewSet,VendorHallViewSet,VendorSeatViewSet

router = DefaultRouter()

router.register('movies', MovieViewSet)
router.register('shows', ShowViewSet)
router.register('show-seats', ShowSeatViewSet)
router.register('bookings', BookingViewSet, basename="booking")
router.register(
    "vendor/branches",
    VendorBranchViewSet,
    basename="vendor-branch"
)
router.register(
    "vendor/halls",
    VendorHallViewSet,
    basename="vendor-hall"
)
router.register(
    "vendor/seats",
    VendorSeatViewSet,
    basename="vendor-seat"
)

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("login/", LoginView.as_view()),
    path("", include(router.urls)),
]