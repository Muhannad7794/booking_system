import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rooms.models import Room


@pytest.mark.django_db
class TestRoomViewSet:
    client = APIClient()

    def test_list_rooms(self):
        # Setup
        Room.objects.create(name="Room 1", number_of_people=3)
        Room.objects.create(name="Room 2", number_of_people=2)

        # Execute
        response = self.client.get(reverse("room-list"))

        # Verify
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_create_room(self):
        # Setup
        room_data = {"name": "Room 3", "number_of_people": 4}

        # Execute
        response = self.client.post(reverse("room-list"), room_data)

        # Verify
        assert response.status_code == status.HTTP_201_CREATED
        assert Room.objects.count() == 1
        assert Room.objects.get().name == "Room 3"
