from django.core.mail import send_mail
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Room, Reservation
from .serializers import RoomSerializer, ReservationSerializer
from datetime import datetime


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

    def create(self, request, *args, **kwargs):
        room_id = request.data.get("room")
        date_from = request.data.get("date_from")
        date_to = request.data.get("date_to")
        reserved_people = int(request.data.get("reserved_people"))

        # Validate room availability and capacity
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

        # Check for date conflicts
        if Reservation.objects.filter(
            room=room, date_to__gte=date_from, date_from__lte=date_to
        ).exists():
            return Response(
                {"error": "Room is not available for the selected dates."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create reservation
        reservation = Reservation.objects.create(
            room=room,
            date_from=date_from,
            date_to=date_to,
            reserved_people=reserved_people,
            resource_id=request.data.get(
                "resource_id", 0
            ),  # Defaulting resource_id if not provided
        )

        # Sending email upon successful reservation
        send_mail(
            subject="Reservation Confirmation",
            message=f"Your reservation for {room.name} from {date_from} to {date_to} has been confirmed.",
            from_email=None,  # Use default from settings
            recipient_list=["stockanalyser.adduser@gmail.com"],
            fail_silently=False,
        )

        return Response(
            self.get_serializer(reservation).data, status=status.HTTP_201_CREATED
        )
