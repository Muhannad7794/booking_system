import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rooms.models import Room, Reservation
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from unittest.mock import patch, Mock
import datetime


@pytest.fixture(autouse=True)
def mock_datetime_now(monkeypatch):
    fixed_date = datetime.datetime(2024, 5, 21)

    class MockDateTime(datetime.datetime):
        @classmethod
        def now(cls, tz=None):
            return fixed_date

    monkeypatch.setattr(datetime, "datetime", MockDateTime)


@pytest.fixture
def room(db):
    return Room.objects.create(name="Test Room", number_of_people=10)


@pytest.fixture
def reservation_dates():
    tomorrow = timezone.now().date() + timedelta(days=1)
    return {
        "tomorrow": tomorrow,
        "over_100_days": tomorrow + timedelta(days=101),
        "past_date": timezone.now().date() - timedelta(days=1),
    }


@pytest.mark.django_db
class TestReservationViewSet:
    client = APIClient()

    @patch("django.core.mail.send_mail")
    def test_create_reservation(self, mock_send_mail, room, reservation_dates):
        reservation_data = {
            "room": room.id,
            "date_from": reservation_dates["tomorrow"].strftime("%Y-%m-%d"),
            "date_to": (reservation_dates["tomorrow"] + timedelta(days=2)).strftime(
                "%Y-%m-%d"
            ),
            "reserved_people": 2,
        }
        response = self.client.post(reverse("reservation-list"), reservation_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Reservation.objects.filter(room=room).exists()
        mock_send_mail.assert_called_once()

    def test_reservation_date_not_numerical(self, room, reservation_dates):
        reservation_data = {
            "room": room.id,
            "date_from": "two thousand twenty-two",
            "date_to": "two thousand twenty-two",
            "reserved_people": 2,
        }
        response = self.client.post(reverse("reservation-list"), reservation_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_reservation_date_in_past(self, room, reservation_dates):
        reservation_data = {
            "room": room.id,
            "date_from": reservation_dates["past_date"].strftime("%Y-%m-%d"),
            "date_to": reservation_dates["tomorrow"].strftime("%Y-%m-%d"),
            "reserved_people": 2,
        }
        response = self.client.post(reverse("reservation-list"), reservation_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_reservation_period_above_99_days(self, room, reservation_dates):
        reservation_data = {
            "room": room.id,
            "date_from": reservation_dates["tomorrow"].strftime("%Y-%m-%d"),
            "date_to": reservation_dates["over_100_days"].strftime("%Y-%m-%d"),
            "reserved_people": 2,
        }
        response = self.client.post(reverse("reservation-list"), reservation_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_reservation_period_zero_days(self, room, reservation_dates):
        reservation_data = {
            "room": room.id,
            "date_from": reservation_dates["tomorrow"].strftime("%Y-%m-%d"),
            "date_to": reservation_dates["tomorrow"].strftime("%Y-%m-%d"),
            "reserved_people": 2,
        }
        response = self.client.post(reverse("reservation-list"), reservation_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch("django.core.mail.send_mail")
    def test_create_reservation(self, mock_send_mail, room, reservation_dates):
        reservation_data = {
            "room": room.id,
            "date_from": reservation_dates["tomorrow"].strftime("%Y-%m-%d"),
            "date_to": (reservation_dates["tomorrow"] + timedelta(days=2)).strftime(
                "%Y-%m-%d"
            ),
            "reserved_people": 2,
        }
        response = self.client.post(reverse("reservation-list"), reservation_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Reservation.objects.filter(room=room).exists()
        mock_send_mail.assert_called_once()
