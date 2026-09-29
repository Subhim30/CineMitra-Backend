from rest_framework import viewsets
from .models import Movie, Show, ShowSeat, Booking, BookingSeat, Branch , Vendor, Hall,Seat
from .serializers import MovieSerializer, ShowSerializer, ShowSeatSerializer, RegisterSerializer, BookingSerializer, BranchSerializer, HallSerializer,SeatSerializer
from .services import create_show_seats
from .permissions import IsVendor

from django.db import transaction
from django.utils.crypto import get_random_string
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import BasePermission
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.exceptions import ValidationError

class RegisterView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            token, created = Token.objects.get_or_create(
                user=user
            )

            return Response(
                {
                    "message": "Registration successful",
                    "token": token.key,
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "role": "CUSTOMER",
                    },
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class LoginView(APIView):
    permission_classes = []

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(
            username=username,
            password=password
        )

        if user is None:
            return Response(
                {"error": "Invalid username or password"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        token, created = Token.objects.get_or_create(
            user=user
        )

        role = "CUSTOMER"

        if hasattr(user, "userprofile"):
            role = user.userprofile.role

        return Response(
            {
                "message": "Login successful",
                "token": token.key,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": role,
                },
            }
        )

class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    parser_classes ={
        MultiPartParser,
        FormParser,
        JSONParser,
    }

class ShowViewSet(viewsets.ModelViewSet):
    queryset = Show.objects.all()
    serializer_class = ShowSerializer

    def perform_create(self, serializer):
        show = serializer.save()
        create_show_seats(show)

class ShowSeatViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ShowSeat.objects.all()
    serializer_class = ShowSeatSerializer

    def get_queryset(self):
        queryset = ShowSeat.objects.all()

        show_id = self.request.query_params.get("show")

        if show_id:
            queryset = self.queryset.filter(show_id=show_id)

        return queryset


class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Booking.objects
            .filter(customer=self.request.user)
            .prefetch_related(
                "booking_seats__show_seat__seat"
            )
            .select_related(
                "show__movie",
                "show__hall"
            )
        )

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        show_id = request.data.get("show")
        show_seat_ids = request.data.get("show_seats", [])

        if not show_id:
            return Response(
                {"error": "Show is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not show_seat_ids:
            return Response(
                {"error": "At least one seat is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            show = Show.objects.get(
                id=show_id,
                is_active=True
            )
        except Show.DoesNotExist:
            return Response(
                {"error": "Show not found or inactive."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Lock selected seats while creating the booking.
        show_seats = list(
            ShowSeat.objects
            .select_for_update()
            .select_related("seat")
            .filter(
                id__in=show_seat_ids,
                show=show
            )
        )

        # Make sure every submitted ID belongs to this show.
        if len(show_seats) != len(set(show_seat_ids)):
            return Response(
                {"error": "One or more selected seats are invalid."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check availability.
        unavailable_seats = [
            f"{seat.seat.row}{seat.seat.number}"
            for seat in show_seats
            if seat.status != "AVAILABLE"
        ]

        if unavailable_seats:
            return Response(
                {
                    "error": "Some seats are no longer available.",
                    "unavailable_seats": unavailable_seats,
                },
                status=status.HTTP_409_CONFLICT
            )

        # Calculate total using the actual ShowSeat prices.
        total_amount = sum(
            seat.price for seat in show_seats
        )

        # Generate booking code.
        booking_code = (
            "CM-"
            + get_random_string(
                10,
                allowed_chars="ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
            )
        )

        booking = Booking.objects.create(
            customer=request.user,
            show=show,
            booking_code=booking_code,
            total_amount=total_amount,
            status="PENDING",
            payment_status="PENDING",
        )

        # Create booking seats and mark seats as booked.
        for show_seat in show_seats:
            BookingSeat.objects.create(
                booking=booking,
                show_seat=show_seat,
                price=show_seat.price,
            )

            show_seat.status = "BOOKED"
            show_seat.save(
                update_fields=["status"]
            )

        serializer = self.get_serializer(booking)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

class IsVendor(BasePermission):
    """
    Allows access only to authenticated users
    whose UserProfile role is VENDOR.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        try:
            return request.user.userprofile.role == "VENDOR"
        except Exception:
            return False

class VendorBranchViewSet(viewsets.ModelViewSet):
    serializer_class = BranchSerializer
    permission_classes = [
        IsAuthenticated,
        IsVendor,
    ]

    def get_queryset(self):
        return Branch.objects.filter(
            vendor__user=self.request.user
        ).select_related("vendor")

    def perform_create(self, serializer):
        vendor = Vendor.objects.get(
            user=self.request.user
        )

        serializer.save(vendor=vendor)

class VendorHallViewSet(viewsets.ModelViewSet):
    serializer_class = HallSerializer
    permission_classes = [
        IsAuthenticated,
        IsVendor,
    ]

    def get_queryset(self):
        return Hall.objects.filter(
            branch__vendor__user=self.request.user
        ).select_related(
            "branch",
            "branch__vendor"
        )

    def perform_create(self, serializer):
        branch_id = self.request.data.get("branch")

        try:
            branch = Branch.objects.get(
                id=branch_id,
                vendor__user=self.request.user
            )
        except Branch.DoesNotExist:
            from rest_framework.exceptions import ValidationError

            raise ValidationError({
                "branch": "Invalid branch or branch does not belong to you."
            })

        serializer.save(branch=branch)

class VendorSeatViewSet(viewsets.ModelViewSet):
    serializer_class = SeatSerializer
    permission_classes = [
        IsAuthenticated,
        IsVendor,
    ]

    def get_queryset(self):
        return Seat.objects.filter(
            hall__branch__vendor__user=self.request.user
        ).select_related(
            "hall",
            "hall__branch",
            "hall__branch__vendor",
        )

    def perform_create(self, serializer):
        hall_id = self.request.data.get("hall")

        try:
            hall = Hall.objects.get(
                id=hall_id,
                branch__vendor__user=self.request.user
            )
        except Hall.DoesNotExist:
            raise ValidationError({
                "hall": "Invalid hall or hall does not belong to you."
            })

        serializer.save(hall=hall)