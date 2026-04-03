(function () {
    "use strict";

    const board = document.getElementById("board");
    const cells = board.querySelectorAll(".cell");
    const statusText = document.getElementById("status-text");
    const statusBanner = document.getElementById("status-banner");
    const playerSymbolEl = document.getElementById("player-symbol");
    const resetBtn = document.getElementById("reset-btn");
    const copyBtn = document.getElementById("copy-code");

    let playerSymbol = null;
    let gameStatus = "waiting";
    let currentTurn = "X";
    let socket = null;

    const WIN_COMBOS = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6],
    ];

    // ---- WebSocket Connection ----
    function connectWebSocket() {
        const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
        const wsUrl = `${protocol}//${window.location.host}/ws/game/${ROOM_CODE}/`;

        socket = new WebSocket(wsUrl);

        socket.onopen = function () {
            setStatus("Connected. Waiting for game...", "status-waiting");
        };

        socket.onmessage = function (e) {
            const data = JSON.parse(e.data);

            if (data.type === "player_assigned") {
                playerSymbol = data.symbol;
                playerSymbolEl.textContent = playerSymbol;
                playerSymbolEl.className = `player-symbol symbol-${playerSymbol.toLowerCase()}`;
            }

            if (data.type === "game_state") {
                updateBoard(data.board);
                gameStatus = data.status;
                currentTurn = data.current_turn;

                if (data.status === "waiting") {
                    setStatus("Waiting for opponent to join...", "status-waiting");
                    resetBtn.style.display = "none";
                } else if (data.status === "playing") {
                    if (data.current_turn === playerSymbol) {
                        setStatus("Your turn!", "");
                    } else {
                        const opponent = data.game_mode !== "multiplayer" ? "AI" : "Opponent";
                        setStatus(`${opponent}'s turn...`, "");
                    }
                    resetBtn.style.display = "none";
                } else if (data.status === "finished") {
                    if (data.winner === null) {
                        setStatus("It's a draw!", "status-draw");
                    } else if (data.winner === playerSymbol) {
                        setStatus("You win!", "status-win");
                    } else {
                        setStatus("You lose!", "status-lose");
                    }
                    highlightWinCells(data.board, data.winner);
                    resetBtn.style.display = "inline-block";
                }
            }

            if (data.type === "error") {
                console.error("Server error:", data.message);
            }
        };

        socket.onclose = function () {
            setStatus("Disconnected. Refresh to reconnect.", "status-lose");
        };

        socket.onerror = function () {
            setStatus("Connection error.", "status-lose");
        };
    }

    // ---- Board Rendering ----
    function updateBoard(boardState) {
        cells.forEach((cell, i) => {
            const val = boardState[i];
            cell.textContent = val || "";
            cell.className = "cell";
            if (val === "X") cell.classList.add("cell-x", "cell-filled");
            else if (val === "O") cell.classList.add("cell-o", "cell-filled");
        });
    }

    function highlightWinCells(boardState, winner) {
        if (!winner) return;
        for (const combo of WIN_COMBOS) {
            if (
                boardState[combo[0]] === winner &&
                boardState[combo[1]] === winner &&
                boardState[combo[2]] === winner
            ) {
                combo.forEach((idx) => cells[idx].classList.add("cell-win"));
                break;
            }
        }
    }

    function setStatus(text, cls) {
        statusText.textContent = text;
        statusBanner.className = "status-banner";
        if (cls) statusBanner.classList.add(cls);
    }

    // ---- Event Handlers ----
    cells.forEach((cell) => {
        cell.addEventListener("click", function () {
            if (gameStatus !== "playing") return;
            if (currentTurn !== playerSymbol) return;
            if (cell.classList.contains("cell-filled")) return;

            const position = cell.getAttribute("data-index");
            socket.send(JSON.stringify({
                action: "make_move",
                position: parseInt(position),
            }));
        });
    });

    resetBtn.addEventListener("click", function () {
        socket.send(JSON.stringify({ action: "reset" }));
    });

    copyBtn.addEventListener("click", function () {
        navigator.clipboard.writeText(ROOM_CODE).then(function () {
            copyBtn.textContent = "✅";
            setTimeout(function () { copyBtn.textContent = "📋"; }, 1500);
        });
    });

    // ---- Init ----
    connectWebSocket();
})();
