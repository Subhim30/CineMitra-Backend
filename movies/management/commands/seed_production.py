from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from movies.models import (
    UserProfile,
    Vendor,
    Branch,
    Hall,
    Seat,
    Movie,
    Show,
    ShowSeat,
)


class Command(BaseCommand):
    help = "Seed CineMitra production database with initial data"

    def handle(self, *args, **options):
        self.stdout.write("Starting CineMitra production seed...")

        # -------------------------------------------------
        # USERS
        # -------------------------------------------------

        users = [
            {
                "username": "subhim",
                "email": "subhimchhetri30@gmail.com",
                "password": "ChangeMe_Admin_2026!",
                "is_staff": True,
                "is_superuser": True,
                "role": "ADMIN",
            },
            {
                "username": "qfx_test",
                "email": "",
                "password": "ChangeMe_QFX_2026!",
                "role": "VENDOR",
            },
            {
                "username": "testcustomer",
                "email": "customer@example.com",
                "password": "ChangeMe_Customer_2026!",
                "role": "CUSTOMER",
            },
            {
                "username": "test",
                "email": "test@gmail.com",
                "password": "ChangeMe_Test_2026!",
                "role": "CUSTOMER",
            },
            {
                "username": "vendor_test",
                "email": "",
                "password": "ChangeMe_Vendor_2026!",
                "role": "VENDOR",
            },
        ]

        created_users = {}

        for data in users:
            user, created = User.objects.get_or_create(
                username=data["username"],
                defaults={
                    "email": data["email"],
                    "is_staff": data.get("is_staff", False),
                    "is_superuser": data.get("is_superuser", False),
                },
            )

            if created:
                user.set_password(data["password"])
                user.save()

            UserProfile.objects.update_or_create(
                user=user,
                defaults={"role": data["role"]},
            )

            created_users[data["username"]] = user

            self.stdout.write(
                f"User {'created' if created else 'exists'}: {user.username}"
            )

        # -------------------------------------------------
        # VENDORS
        # -------------------------------------------------

        vendor1, _ = Vendor.objects.update_or_create(
            user=created_users["qfx_test"],
            defaults={
                "business_name": "QFX_Cinema",
                "phone": "9856568956",
                "approval_status": "APPROVED",
            },
        )

        vendor2, _ = Vendor.objects.update_or_create(
            user=created_users["vendor_test"],
            defaults={
                "business_name": "vendor_test",
                "phone": "9800000000",
                "approval_status": "APPROVED",
            },
        )

        # -------------------------------------------------
        # BRANCHES
        # -------------------------------------------------

        branch1, _ = Branch.objects.update_or_create(
            vendor=vendor1,
            name="QFX Civil Mall",
            defaults={
                "city": "Kathmandu",
                "address": "Civil Mall, Sundhara, Kathmandu",
            },
        )

        branch2, _ = Branch.objects.update_or_create(
            vendor=vendor2,
            name="QFX Trademall",
            defaults={
                "city": "Pokhara",
                "address": "Chipledhunga, Pokhara",
            },
        )

        # -------------------------------------------------
        # HALLS
        # -------------------------------------------------

        hall1, _ = Hall.objects.update_or_create(
            branch=branch1,
            name="Hall 2",
            defaults={"capacity": 50},
        )

        hall2, _ = Hall.objects.update_or_create(
            branch=branch2,
            name="East Hall",
            defaults={"capacity": 80},
        )

        # -------------------------------------------------
        # SEATS
        # -------------------------------------------------

        seats = [
            (hall1, "A", 1, "STANDARD"),
            (hall1, "A", 2, "STANDARD"),
            (hall1, "A", 3, "PREMIUM"),
            (hall2, "A", 1, "STANDARD"),
        ]

        for hall, row, number, seat_type in seats:
            Seat.objects.update_or_create(
                hall=hall,
                row=row,
                number=number,
                defaults={"seat_type": seat_type},
            )

        # -------------------------------------------------
        # MOVIE
        # -------------------------------------------------

        movie, _ = Movie.objects.update_or_create(
            title="Avatar",
            defaults={
                "description": "A science fiction adventure movie.",
                "genre": "Science Fiction",
                "duration": 162,
                "release_date": "2026-09-01",
                "rating": "8.5",
                "poster": "cinemitra/movies/avatar-poster.jpg",
            },
        )

        # -------------------------------------------------
        # SHOW
        # -------------------------------------------------

        existing_shows = Show.objects.filter(
            movie=movie,
            hall=hall1,
            show_date="2026-09-27",
            start_time="17:00:00",
        )

        if existing_shows.exists():
            show = existing_shows.first()

            existing_shows.exclude(pk=show.pk).delete()

            show.ticket_price = "350.00"
            show.is_active = True
            show.save()

            self.stdout.write(
                f"Using existing show: {show.id}"
            )
        else:
            show = Show.objects.create(
                movie=movie,
                hall=hall1,
                show_date="2026-09-27",
                start_time="17:00:00",
                ticket_price="350.00",
                is_active=True,
            )

            self.stdout.write(
                f"Created show: {show.id}"
            )

        # -------------------------------------------------
        # SHOW SEATS
        # -------------------------------------------------

        hall1_seats = Seat.objects.filter(hall=hall1)

        for seat in hall1_seats:
            ShowSeat.objects.get_or_create(
                show=show,
                seat=seat,
                defaults={
                    "status": "AVAILABLE",
                    "price": "350.00",
                },
            )

        self.stdout.write(
            self.style.SUCCESS(
                "CineMitra production seed completed successfully!"
            )
        )