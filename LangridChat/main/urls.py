from django.conf.urls import include
from django.urls import path
from django.contrib import admin

urlpatterns = [
    path('', include('chat.urls')),
    path('langridchat/admin/', admin.site.urls),
]
