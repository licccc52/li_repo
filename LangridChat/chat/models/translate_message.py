from django.db import models

from chat.models import Message


class TranslateMessage(models.Model):
    source = models.ForeignKey(Message, on_delete=models.CASCADE)
    language = models.CharField(max_length=10)
    message = models.CharField(max_length=1024)
    created_time = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.message
