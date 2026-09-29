from rest_framework import serializers
from .models import Movie, Show, ShowSeat
from django.contrib.auth.models import User
from .models import (
    Movie,
    Show,
    ShowSeat,
    Booking,
    BookingSeat,
    Branch,
    Hall,
    Seat,
)


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = "__all__"


class ShowSerializer(serializers.ModelSerializer):
    movie_title = serializers.CharField(
        source="movie.title",
        read_only=True
    )

    hall_name = serializers.CharField(
        source="hall.name",
        read_only=True
    )

    branch_name = serializers.CharField(
        source="hall.branch.name",
        read_only=True
    )

    vendor_name = serializers.CharField(
        source="hall.branch.vendor.business_name",
        read_only=True
    )

    class Meta:
        model = Show
        fields = [
            "id",
            "movie",
            "movie_title",
            "hall",
            "hall_name",
            "branch_name",
            "vendor_name",
            "show_date",
            "start_time",
            "ticket_price",
            "is_active",
        ]
class ShowSeatSerializer(serializers.ModelSerializer):
    seat_label = serializers.SerializerMethodField()
    seat_type = serializers.CharField(
        source="seat.seat_type",
        read_only=True
    )

    class Meta:
        model = ShowSeat
        fields = [
            "id",
            "show",
            "seat",
            "seat_label",
            "seat_type",
            "status",
            "price",
        ]

    def get_seat_label(self, obj):
        return f"{obj.seat.row}{obj.seat.number}"

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
        ]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )

        from .models import UserProfile

        UserProfile.objects.create(
            user=user,
            role="CUSTOMER"
        )

        return user

class BookingSeatSerializer(serializers.ModelSerializer):
    seat_label = serializers.SerializerMethodField()

    class Meta:
        model = BookingSeat
        fields = [
            "id",
            "show_seat",
            "seat_label",
            "price",
        ]

    def get_seat_label(self, obj):
        return f"{obj.show_seat.seat.row}{obj.show_seat.seat.number}"


class BookingSerializer(serializers.ModelSerializer):
    booking_seats = BookingSeatSerializer(
        many=True,
        read_only=True
    )

    movie_title = serializers.CharField(
        source="show.movie.title",
        read_only=True
    )

    show_date = serializers.DateField(
        source="show.show_date",
        read_only=True
    )

    start_time = serializers.TimeField(
        source="show.start_time",
        read_only=True
    )

    hall_name = serializers.CharField(
        source="show.hall.name",
        read_only=True
    )

    class Meta:
        model = Booking
        fields = [
            "id",
            "booking_code",
            "show",
            "movie_title",
            "show_date",
            "start_time",
            "hall_name",
            "total_amount",
            "status",
            "payment_status",
            "created_at",
            "booking_seats",
        ]

        read_only_fields = [
            "booking_code",
            "total_amount",
            "status",
            "payment_status",
            "created_at",
            "booking_seats",
        ]

class BranchSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(
        source="vendor.business_name",
        read_only=True
    )

    class Meta:
        model = Branch
        fields = [
            "id",
            "vendor",
            "vendor_name",
            "name",
            "city",
            "address",
        ]

        read_only_fields = [
            "vendor",
        ]

class HallSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(
        source="branch.name",
        read_only=True
    )

    class Meta:
        model = Hall
        fields = [
            "id",
            "branch",
            "branch_name",
            "name",
            "capacity",
        ]

class SeatSerializer(serializers.ModelSerializer):
    hall_name = serializers.CharField(
        source="hall.name",
        read_only=True
    )

    branch_name = serializers.CharField(
        source="hall.branch.name",
        read_only=True
    )

    class Meta:
        model = Seat
        fields = [
            "id",
            "hall",
            "hall_name",
            "branch_name",
            "row",
            "number",
            "seat_type",
        ]