from django.db import models


class Room(models.Model):
    name = models.CharField(max_length=255)
    number_of_people = models.IntegerField()

    def __str__(self):
        return self.name


class Reservation(models.Model):
    room = models.ForeignKey(
        Room, on_delete=models.CASCADE, related_name="reservations"
    )
    date_from = models.DateField()
    date_to = models.DateField()
    reserved_people = models.IntegerField()
    resource_id = (
        models.IntegerField()
    )  # Assuming this links to another model not detailed here

    def __str__(self):
        return f"{self.room.name} reservation from {self.date_from} to {self.date_to}"
