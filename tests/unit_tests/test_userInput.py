import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rooms.models import Room


@pytest.mark.django_db
class TestRoomViewSet:
    client = APIClient()

    def test_list_rooms(self):
        Room.objects.create(name="Room 1", number_of_people=3)
        Room.objects.create(name="Room 2", number_of_people=2)

        response = self.client.get(reverse("room-list"))

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_create_room_valid_capacity(self):
        room_data = {"name": "Room 3", "number_of_people": 4}
        response = self.client.post(reverse("room-list"), room_data)

        assert response.status_code == status.HTTP_201_CREATED
        assert Room.objects.filter(name="Room 3").exists()

    def test_room_capacity_exceeds_limit(self):
        room_data = {"name": "Room Large", "number_of_people": 101}
        response = self.client.post(reverse("room-list"), room_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_room_capacity_is_zero(self):
        room_data = {"name": "Room Zero", "number_of_people": 0}
        response = self.client.post(reverse("room-list"), room_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_room_capacity_is_negative(self):
        room_data = {"name": "Room Negative", "number_of_people": -1}
        response = self.client.post(reverse("room-list"), room_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_room_capacity_is_not_numerical(self):
        room_data = {"name": "Room String", "number_of_people": "five"}
        response = self.client.post(reverse("room-list"), room_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Number of people must be an integer." in response.data["error"]
