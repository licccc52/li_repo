from django.db import models

from chat.models.room import Room
from chat.models.user import User


class Message(models.Model):
    sender = models.ForeignKey(User, related_name='messages_sent', on_delete=models.CASCADE)
    addressees = models.ManyToManyField(User, default=None, blank=True)
    room = models.ForeignKey(Room, related_name='messages_received', on_delete=models.CASCADE)
    message = models.CharField(max_length=1024)
    language = models.CharField(max_length=10)

    created_time = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.message
