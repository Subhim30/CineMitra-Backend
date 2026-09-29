from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ("CUSTOMER", "Customer"),
        ("VENDOR", "Vendor"),
        ("ADMIN", "Admin"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="CUSTOMER")

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class Vendor(models.Model):
    APPROVAL_CHOICES = [
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_CHOICES,
        default="PENDING"
    )

    def __str__(self):
        return self.business_name


class Branch(models.Model):
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name="branches"
    )
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=300)

    def __str__(self):
        return f"{self.name} - {self.city}"


class Hall(models.Model):
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name="halls"
    )
    name = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.branch.name} - {self.name}"


class Seat(models.Model):
    SEAT_TYPE_CHOICES = [
        ("STANDARD", "Standard"),
        ("PREMIUM", "Premium"),
        ("VIP", "VIP"),
    ]

    hall = models.ForeignKey(
        Hall,
        on_delete=models.CASCADE,
        related_name="seats"
    )
    row = models.CharField(max_length=5)
    number = models.PositiveIntegerField()
    seat_type = models.CharField(
        max_length=20,
        choices=SEAT_TYPE_CHOICES,
        default="STANDARD"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["hall", "row", "number"],
                name="unique_seat_in_hall"
            )
        ]

    def __str__(self):
        return f"{self.row}{self.number} - {self.hall.name}"


class Movie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    genre = models.CharField(max_length=100)
    duration = models.IntegerField()
    release_date = models.DateField()
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    poster = models.ImageField(
        upload_to="movies/",
        blank=True,
        null=True
    )

    def __str__(self):
        return self.title
class Show(models.Model):
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name="shows"
    )
    hall = models.ForeignKey(
        Hall,
        on_delete=models.CASCADE,
        related_name="shows"
    )
    show_date = models.DateField()
    start_time = models.TimeField()
    ticket_price = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.movie.title} - {self.hall.name} - {self.show_date} {self.start_time}"

class ShowSeat(models.Model):
    STATUS_CHOICES = [
        ("AVAILABLE", "Available"),
        ("HELD", "Held"),
        ("BOOKED", "Booked"),
    ]

    show = models.ForeignKey(
        Show,
        on_delete=models.CASCADE,
        related_name="show_seats"
    )
    seat = models.ForeignKey(
        Seat,
        on_delete=models.CASCADE,
        related_name="show_seats"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="AVAILABLE"
    )
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["show", "seat"],
                name="unique_seat_per_show"
            )
        ]

    def __str__(self):
        return f"{self.show.movie.title} - {self.seat.row}{self.seat.number} - {self.status}"
    
class Booking(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("CONFIRMED", "Confirmed"),
        ("CANCELLED", "Cancelled"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PAID", "Paid"),
        ("FAILED", "Failed"),
    ]

    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bookings"
    )
    show = models.ForeignKey(
        Show,
        on_delete=models.CASCADE,
        related_name="bookings"
    )
    booking_code = models.CharField(
        max_length=20,
        unique=True
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="PENDING"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.booking_code

class BookingSeat(models.Model):
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name="booking_seats"
    )
    show_seat = models.ForeignKey(
        ShowSeat,
        on_delete=models.CASCADE,
        related_name="booking_seats"
    )
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["booking", "show_seat"],
                name="unique_booking_show_seat"
            )
        ]

    def __str__(self):
        return f"{self.booking.booking_code} - {self.show_seat.seat.row}{self.show_seat.seat.number}"