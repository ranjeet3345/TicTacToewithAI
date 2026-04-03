import random
import string

from django.db import models
from django.utils import timezone


def generate_room_code():
    """Generate a unique six-digit room code."""
    return "".join(random.choices(string.digits, k=6))


class GameRoom(models.Model):
    GAME_STATUS_CHOICES = [
        ("waiting", "Waiting for opponent"),
        ("playing", "Game in progress"),
        ("finished", "Game finished"),
    ]

    GAME_MODE_CHOICES = [
        ("multiplayer", "Multiplayer"),
        ("ai_minimax", "AI - Minimax"),
        ("ai_gemini", "AI - Gemini"),
    ]

    room_code = models.CharField(max_length=6, unique=True, default=generate_room_code)
    board = models.JSONField(default=list)
    current_turn = models.CharField(max_length=1, default="X")
    player_x = models.CharField(max_length=100, blank=True, null=True)
    player_o = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=10, choices=GAME_STATUS_CHOICES, default="waiting")
    winner = models.CharField(max_length=1, blank=True, null=True)
    game_mode = models.CharField(max_length=15, choices=GAME_MODE_CHOICES, default="multiplayer")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.board:
            self.board = [""] * 9
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Room {self.room_code} ({self.status})"

    def reset_board(self):
        self.board = [""] * 9
        self.current_turn = "X"
        self.winner = None
        self.status = "playing"
        self.save()

    def check_winner(self):
        """Check if there's a winner or a draw. Returns 'X', 'O', 'draw', or None."""
        b = self.board
        win_combos = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # columns
            [0, 4, 8], [2, 4, 6],              # diagonals
        ]
        for combo in win_combos:
            if b[combo[0]] and b[combo[0]] == b[combo[1]] == b[combo[2]]:
                return b[combo[0]]
        if all(cell != "" for cell in b):
            return "draw"
        return None


class GameEvent(models.Model):
    """Audit trail for all game actions."""
    EVENT_TYPES = [
        ("join", "Player Joined"),
        ("move", "Move Made"),
        ("win", "Game Won"),
        ("draw", "Game Draw"),
        ("disconnect", "Player Disconnected"),
        ("ai_move", "AI Move"),
    ]

    room = models.ForeignKey(GameRoom, on_delete=models.CASCADE, related_name="events")
    event_type = models.CharField(max_length=15, choices=EVENT_TYPES)
    player = models.CharField(max_length=100, blank=True, null=True)
    data = models.JSONField(default=dict)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return f"[{self.timestamp}] {self.event_type} in {self.room.room_code}"
