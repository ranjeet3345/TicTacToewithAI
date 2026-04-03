import json
import logging

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .ai import get_gemini_move, get_minimax_move
from .models import GameEvent, GameRoom

logger = logging.getLogger(__name__)


class GameConsumer(AsyncWebsocketConsumer):
    """
    Async WebSocket consumer that manages a Tic-Tac-Toe game room.
    Handles connections, moves, turn management, win/draw detection,
    and AI opponent integration.
    """

    async def connect(self):
        self.room_code = self.scope["url_route"]["kwargs"]["room_code"]
        self.room_group_name = f"game_{self.room_code}"
        self.player_symbol = None

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        room = await self._get_room()
        if room is None:
            await self.send(text_data=json.dumps({"type": "error", "message": "Room not found"}))
            await self.close()
            return

        # Handle AI games - start immediately when first player joins
        if room.game_mode in ("ai_minimax", "ai_gemini"):
            if room.player_x is None:
                self.player_symbol = "X"
                room.player_x = self.channel_name
                room.player_o = "AI"
                room.status = "playing"
                room.current_turn = "X"
                await sync_to_async(room.save)()
            else:
                await self.send(text_data=json.dumps({"type": "error", "message": "Room is full"}))
                await self.close()
                return
        # Handle multiplayer games
        elif room.player_x is None:
            self.player_symbol = "X"
            room.player_x = self.channel_name
            await sync_to_async(room.save)()
        elif room.player_o is None:
            self.player_symbol = "O"
            room.player_o = self.channel_name
            room.status = "playing"
            await sync_to_async(room.save)()
        else:
            await self.send(text_data=json.dumps({"type": "error", "message": "Room is full"}))
            await self.close()
            return

        await self._log_event("join", self.channel_name, {"symbol": self.player_symbol})

        await self.send(text_data=json.dumps({
            "type": "player_assigned",
            "symbol": self.player_symbol,
            "room_code": self.room_code,
        }))

        await self._broadcast_game_state()

    async def disconnect(self, close_code):
        await self._log_event("disconnect", self.channel_name, {"code": close_code})
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")

        if action == "make_move":
            await self._handle_move(data.get("position"))
        elif action == "reset":
            await self._handle_reset()

    async def _handle_move(self, position):
        if position is None:
            return

        room = await self._get_room()
        if room is None or room.status != "playing":
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "Game is not in progress",
            }))
            return

        if room.current_turn != self.player_symbol:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "Not your turn",
            }))
            return

        position = int(position)
        if position < 0 or position > 8 or room.board[position] != "":
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "Invalid move",
            }))
            return

        # Atomic update: apply move, check result, save
        room.board[position] = self.player_symbol
        room.current_turn = "O" if self.player_symbol == "X" else "X"
        await sync_to_async(room.save)()
        await self._log_event("move", self.channel_name, {
            "symbol": self.player_symbol,
            "position": position,
        })

        result = await sync_to_async(room.check_winner)()
        if result:
            room.status = "finished"
            room.winner = None if result == "draw" else result
            await sync_to_async(room.save)()
            event_type = "draw" if result == "draw" else "win"
            await self._log_event(event_type, self.channel_name, {"result": result})

        await self._broadcast_game_state()

        # If it's AI's turn and game is still playing, make AI move
        if room.status == "playing" and room.game_mode in ("ai_minimax", "ai_gemini"):
            await self._handle_ai_move(room)

    async def _handle_ai_move(self, room):
        room = await self._get_room()
        if room.status != "playing":
            return

        ai_symbol = "O"
        if room.game_mode == "ai_minimax":
            move = await sync_to_async(get_minimax_move)(list(room.board), ai_symbol)
        else:
            move = await sync_to_async(get_gemini_move)(list(room.board), ai_symbol)

        if move is None:
            return

        room.board[move] = ai_symbol
        room.current_turn = "X"
        await sync_to_async(room.save)()
        await self._log_event("ai_move", "AI", {"symbol": ai_symbol, "position": move})

        result = await sync_to_async(room.check_winner)()
        if result:
            room.status = "finished"
            room.winner = None if result == "draw" else result
            await sync_to_async(room.save)()
            event_type = "draw" if result == "draw" else "win"
            await self._log_event(event_type, "AI", {"result": result})

        await self._broadcast_game_state()

    async def _handle_reset(self):
        room = await self._get_room()
        if room:
            await sync_to_async(room.reset_board)()
            await self._broadcast_game_state()

    async def _broadcast_game_state(self):
        room = await self._get_room()
        if room is None:
            return

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "game_state",
                "board": room.board,
                "current_turn": room.current_turn,
                "status": room.status,
                "winner": room.winner,
                "game_mode": room.game_mode,
                "player_x_connected": room.player_x is not None,
                "player_o_connected": room.player_o is not None,
            },
        )

    async def game_state(self, event):
        """Handler for game_state group messages."""
        await self.send(text_data=json.dumps({
            "type": "game_state",
            "board": event["board"],
            "current_turn": event["current_turn"],
            "status": event["status"],
            "winner": event["winner"],
            "game_mode": event["game_mode"],
            "player_x_connected": event["player_x_connected"],
            "player_o_connected": event["player_o_connected"],
        }))

    async def _get_room(self):
        try:
            return await sync_to_async(GameRoom.objects.select_for_update().get)(
                room_code=self.room_code
            )
        except GameRoom.DoesNotExist:
            return None

    async def _log_event(self, event_type, player, data):
        try:
            room = await sync_to_async(GameRoom.objects.get)(room_code=self.room_code)
            await sync_to_async(GameEvent.objects.create)(
                room=room,
                event_type=event_type,
                player=player,
                data=data,
            )
        except Exception as e:
            logger.error("Failed to log event: %s", e)
