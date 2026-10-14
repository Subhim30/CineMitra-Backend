from decimal import Decimal
from .models import ShowSeat


def create_show_seats(show):
    seats = show.hall.seats.all()

    existing_seat_ids = set(
        ShowSeat.objects.filter(show=show).values_list(
            "seat_id",
            flat=True
        )
    )

    show_seats = []

    for seat in seats:
        if seat.id in existing_seat_ids:
            continue

        base_price = Decimal(show.ticket_price)

        if seat.seat_type == "PREMIUM":
            price = base_price * Decimal("1.20")

        elif seat.seat_type == "VIP":
            price = base_price * Decimal("1.50")

        else:
            price = base_price

        show_seats.append(
            ShowSeat(
                show=show,
                seat=seat,
                status="AVAILABLE",
                price=price,
            )
        )

    if show_seats:
        ShowSeat.objects.bulk_create(show_seats)

    return show_seats