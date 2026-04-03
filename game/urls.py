from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.create_room, name="create_room"),
    path("join/", views.join_room, name="join_room"),
    path("room/<str:room_code>/", views.game_room, name="game_room"),
    path("api/room/<str:room_code>/", views.room_status, name="room_status"),
]
