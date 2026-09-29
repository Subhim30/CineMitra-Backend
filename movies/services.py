from .models import ShowSeat


def create_show_seats(show):
    seats = show.hall.seats.all()

    show_seats = []

    for seat in seats:
        show_seats.append(
            ShowSeat(
                show=show,
                seat=seat,
                status="AVAILABLE",
                price=show.ticket_price,
            )
        )

    ShowSeat.objects.bulk_create(show_seats)

    return show_seats