from django.contrib import admin

from .models import GameEvent, GameRoom


@admin.register(GameRoom)
class GameRoomAdmin(admin.ModelAdmin):
    list_display = ("room_code", "status", "game_mode", "current_turn", "winner", "created_at")
    list_filter = ("status", "game_mode")
    search_fields = ("room_code",)


@admin.register(GameEvent)
class GameEventAdmin(admin.ModelAdmin):
    list_display = ("room", "event_type", "player", "timestamp")
    list_filter = ("event_type",)
