import logging
import math
import random

from django.conf import settings

logger = logging.getLogger(__name__)


def check_winner_board(board):
    """Check winner on a raw board list. Returns 'X', 'O', 'draw', or None."""
    win_combos = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6],
    ]
    for combo in win_combos:
        if board[combo[0]] and board[combo[0]] == board[combo[1]] == board[combo[2]]:
            return board[combo[0]]
    if all(cell != "" for cell in board):
        return "draw"
    return None


# ---------------------------------------------------------------------------
# Minimax AI — unbeatable
# ---------------------------------------------------------------------------

def minimax(board, is_maximizing, ai_symbol, human_symbol):
    """
    Minimax algorithm for optimal Tic-Tac-Toe play.
    AI is always the maximizing player.
    """
    result = check_winner_board(board)
    if result == ai_symbol:
        return 10
    if result == human_symbol:
        return -10
    if result == "draw":
        return 0

    if is_maximizing:
        best = -math.inf
        for i in range(9):
            if board[i] == "":
                board[i] = ai_symbol
                score = minimax(board, False, ai_symbol, human_symbol)
                board[i] = ""
                best = max(best, score)
        return best
    else:
        best = math.inf
        for i in range(9):
            if board[i] == "":
                board[i] = human_symbol
                score = minimax(board, True, ai_symbol, human_symbol)
                board[i] = ""
                best = min(best, score)
        return best


def get_minimax_move(board, ai_symbol="O"):
    """Return the optimal cell index for the AI using Minimax."""
    human_symbol = "X" if ai_symbol == "O" else "O"
    best_score = -math.inf
    best_move = None

    for i in range(9):
        if board[i] == "":
            board[i] = ai_symbol
            score = minimax(board, False, ai_symbol, human_symbol)
            board[i] = ""
            if score > best_score:
                best_score = score
                best_move = i

    return best_move


# ---------------------------------------------------------------------------
# Gemini API AI — human-like
# ---------------------------------------------------------------------------

def get_gemini_move(board, ai_symbol="O"):
    """
    Use Google's Gemini API to get a human-like move.
    Falls back to a random valid move if the API is unavailable.
    """
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        logger.warning("GEMINI_API_KEY not set, falling back to random move")
        return _random_move(board)

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")

        board_display = ""
        for i in range(3):
            row = []
            for j in range(3):
                cell = board[i * 3 + j]
                row.append(cell if cell else str(i * 3 + j))
            board_display += " | ".join(row) + "\n"
            if i < 2:
                board_display += "---------\n"

        available = [i for i in range(9) if board[i] == ""]

        prompt = (
            f"You are playing Tic-Tac-Toe as '{ai_symbol}'. "
            f"The current board state is:\n\n{board_display}\n"
            f"Empty positions are shown as numbers (0-8). "
            f"Available positions: {available}\n\n"
            f"Choose your next move. Play like a human — sometimes make mistakes, "
            f"sometimes play well. Don't always pick the optimal move.\n\n"
            f"Reply with ONLY a single number representing your chosen position. "
            f"Nothing else."
        )

        response = model.generate_content(prompt)
        move = int(response.text.strip())

        if move in available:
            return move

        logger.warning("Gemini returned invalid move %s, falling back to random", move)
        return _random_move(board)

    except Exception as e:
        logger.exception("Gemini API error: %s", e)
        return _random_move(board)


def _random_move(board):
    """Pick a random valid move from the board."""
    available = [i for i in range(9) if board[i] == ""]
    return random.choice(available) if available else None
