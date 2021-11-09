from django.db import models
from chat.models.user import User


class Room(models.Model):
    room = models.CharField(max_length=20, unique=True)
    created_time = models.DateTimeField(auto_now_add=True, blank=True)
    online = models.ManyToManyField(User, default=None, blank=True, related_name='online')
    typing = models.ManyToManyField(User, default=None, blank=True, related_name='typing')

    def __str__(self):
        return f'No.{self.id}( {self.room} )'
