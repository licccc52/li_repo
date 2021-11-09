from django.contrib import admin
from .models import Room, TranslateMessage, User, Message
from .models.admin import MessageAdmin

# Register your models here.
admin.site.register(Room)
admin.site.register(User)
admin.site.register(Message, MessageAdmin)
admin.site.register(TranslateMessage)
