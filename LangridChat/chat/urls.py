from django.urls import path

from . import views

app_name = 'chat'
urlpatterns = [
    path('', views.index, name='index'),
    path('support-language', views.support_languages, name='support languages'),
    path('room/', views.room, name='check_room'),
    path('room/<str:room_name>/', views.room, name='set_room'),
    path('csv', views.csv_download, name='csv_info'),
    path('csv/<str:room_name>', views.csv_download, name='download_csv'),
]
