from django.http import JsonResponse
from django.shortcuts import redirect, render

from .models import GameRoom


def index(request):
    """Home page — create or join a game room."""
    return render(request, "game/index.html")


def create_room(request):
    """Create a new game room and redirect to it."""
    mode = request.POST.get("game_mode", "multiplayer")
    room = GameRoom.objects.create(game_mode=mode)
    return redirect("game_room", room_code=room.room_code)


def join_room(request):
    """Join an existing game room by code."""
    room_code = request.POST.get("room_code", "").strip()
    if not room_code:
        return render(request, "game/index.html", {"error": "Please enter a room code."})

    try:
        room = GameRoom.objects.get(room_code=room_code)
    except GameRoom.DoesNotExist:
        return render(request, "game/index.html", {"error": "Room not found."})

    if room.status == "finished":
        return render(request, "game/index.html", {"error": "This game has already ended."})

    return redirect("game_room", room_code=room.room_code)


def game_room(request, room_code):
    """Render the game room page."""
    try:
        room = GameRoom.objects.get(room_code=room_code)
    except GameRoom.DoesNotExist:
        return redirect("index")

    return render(request, "game/room.html", {"room": room})


def room_status(request, room_code):
    """API endpoint to fetch the current room status as JSON."""
    try:
        room = GameRoom.objects.get(room_code=room_code)
    except GameRoom.DoesNotExist:
        return JsonResponse({"error": "Room not found"}, status=404)

    return JsonResponse({
        "room_code": room.room_code,
        "board": room.board,
        "current_turn": room.current_turn,
        "status": room.status,
        "winner": room.winner,
        "game_mode": room.game_mode,
    })
