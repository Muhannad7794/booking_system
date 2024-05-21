from django.core.mail import send_mail
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Room, Reservation
from .serializers import RoomSerializer, ReservationSerializer
from datetime import datetime


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    def create(self, request, *args, **kwargs):
        number_of_people = int(request.data.get("number_of_people"))
        if number_of_people <= 0 or number_of_people > 100:
            return Response(
                {"error": "Number of people must be between 1 and 100."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().create(request, *args, **kwargs)


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

    def create(self, request, *args, **kwargs):
        room_id = request.data.get("room")
        date_from = request.data.get("date_from")
        date_to = request.data.get("date_to")
        reserved_people = int(request.data.get("reserved_people"))
        today = datetime.now().date()

        try:
            date_from = datetime.strptime(date_from, "%Y-%m-%d").date()
            date_to = datetime.strptime(date_to, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if date_from < today or date_to < today:
            return Response(
                {"error": "Reservation dates cannot be in the past."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (date_to - date_from).days > 99:
            return Response(
                {"error": "Reservation period cannot exceed 99 days."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (date_to - date_from).days < 1:
            return Response(
                {"error": "Reservation period must be at least one day."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            room = Room.objects.get(id=room_id)
            if room.number_of_people < reserved_people:
                return Response(
                    {"error": "Requested quantity exceeds room capacity."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Room.DoesNotExist:
            return Response(
                {"error": "Room does not exist."}, status=status.HTTP_404_NOT_FOUND
            )

        if Reservation.objects.filter(
            room=room, date_to__gte=date_from, date_from__lte=date_to
        ).exists():
            return Response(
                {"error": "Room is not available for the selected dates."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        reservation = Reservation.objects.create(
            room=room,
            date_from=date_from,
            date_to=date_to,
            reserved_people=reserved_people,
            resource_id=request.data.get("resource_id", 0),
        )

        send_mail(
            subject="Reservation Confirmation",
            message=f"Your reservation for {room.name} from {date_from} to {date_to} has been confirmed.",
            from_email=None,
            recipient_list=["stockanalyser.adduser@gmail.com"],
            fail_silently=False,
        )

        return Response(
            self.get_serializer(reservation).data, status=status.HTTP_201_CREATED
        )
