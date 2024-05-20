from rest_framework import serializers
from .models import Room, Reservation


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ["id", "name", "number_of_people"]


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = [
            "id",
            "room",
            "date_from",
            "date_to",
            "reserved_people",
            "resource_id",
        ]
