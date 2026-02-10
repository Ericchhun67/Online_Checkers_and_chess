(() => {
    const boardEl = document.querySelector(".board-grid");
    if (!boardEl) {
        return;
    }

    const gameType = (boardEl.dataset.game || "checkers").toLowerCase();
    const statusEl = document.getElementById("status-message");
    const historyEl = document.getElementById("move-history-list");
    const leaveButton = document.getElementById("leave-game");
    const timerEl = document.getElementById("turn-timer");

    const chessLabels = {
        P: "P",
        R: "R",
        N: "N",
        B: "B",
        Q: "Q",
        K: "K"
    };

    const state = {
        board: [],
        turn: "white",
        winner: null
    };
    const TURN_SECONDS = 120;

    let selectedSquare = null;
    let moveNumber = 1;
    let boardBusy = false;
    let remainingSeconds = TURN_SECONDS;
    let timerHandle = null;
    let timeoutInFlight = false;
    let gameStartAt = Date.now();
    let completedMoves = 0;
    let winRedirected = false;

    const setStatus = (message) => {
        if (statusEl) {
            statusEl.textContent = message;
        }
    };

    const setBusy = (busy) => {
        boardBusy = busy;
        boardEl.classList.toggle("busy", busy);
    };

    const formatTimer = (seconds) => {
        const minutes = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${String(minutes).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
    };

    const renderTimer = () => {
        if (!timerEl) {
            return;
        }
        timerEl.textContent = formatTimer(remainingSeconds);
        timerEl.classList.remove("warning", "danger");
        if (remainingSeconds <= 10) {
            timerEl.classList.add("danger");
        } else if (remainingSeconds <= 30) {
            timerEl.classList.add("warning");
        }
    };

    const resetTimer = () => {
        remainingSeconds = TURN_SECONDS;
        renderTimer();
    };

    const appendHistoryNote = (note) => {
        if (!historyEl || !note) {
            return;
        }
        const item = document.createElement("li");
        item.textContent = `${moveNumber}. ${note}`;
        historyEl.prepend(item);
        moveNumber += 1;
    };

    const pieceColor = (piece) => {
        if (!piece) {
            return null;
        }
        if (piece.startsWith("W")) {
            return "white";
        }
        if (piece.startsWith("B")) {
            return "black";
        }
        return null;
    };

    const colorLabel = (color) => (color === "white" ? "White" : "Black");

    const formatSquare = ([row, col]) => {
        const file = String.fromCharCode("a".charCodeAt(0) + col);
        const rank = 8 - row;
        return `${file}${rank}`;
    };

    const appendHistory = (move) => {
        if (!historyEl || !move) {
            return;
        }
        const mover = pieceColor(move.piece);
        const label = colorLabel(mover || "white");
        const item = document.createElement("li");
        item.textContent = `${moveNumber}. ${label}: ${formatSquare(move.start)} -> ${formatSquare(move.end)}`;
        historyEl.prepend(item);
        moveNumber += 1;
        completedMoves += 1;
    };

    const redirectToWinPage = (winner) => {
        if (winRedirected || !winner) {
            return;
        }
        winRedirected = true;
        const duration = Math.max(1, Math.floor((Date.now() - gameStartAt) / 1000));
        const reason = gameType === "chess" ? "by checkmate" : "by capturing all opponent pieces";
        const params = new URLSearchParams({
            mode: "pvp",
            game: gameType,
            winner,
            moves: String(completedMoves),
            duration: String(duration),
            reason
        });
        window.location.href = `/game/win?${params.toString()}`;
    };

    const clearSelection = () => {
        selectedSquare = null;
        boardEl.querySelectorAll(".square.selected").forEach((el) => {
            el.classList.remove("selected");
        });
    };

    const renderBoard = () => {
        boardEl.innerHTML = "";
        for (let row = 0; row < 8; row += 1) {
            for (let col = 0; col < 8; col += 1) {
                const square = document.createElement("div");
                const darkSquare = (row + col) % 2 === 1;
                square.className = `square ${darkSquare ? "dark" : "light"}`;
                square.dataset.row = String(row);
                square.dataset.col = String(col);

                const piece = state.board[row]?.[col];
                if (piece) {
                    const pieceEl = document.createElement("div");
                    const color = pieceColor(piece);
                    if (gameType === "checkers") {
                        pieceEl.className = `piece checker ${color}`;
                        if (piece.length > 1 && piece[1] === "K") {
                            pieceEl.classList.add("king");
                            pieceEl.textContent = "K";
                        }
                    } else {
                        const type = piece[1];
                        pieceEl.className = `piece chess ${color}`;
                        pieceEl.dataset.piece = type ? type.toLowerCase() : "p";
                        pieceEl.textContent = chessLabels[type] || "P";
                    }
                    square.appendChild(pieceEl);
                }

                boardEl.appendChild(square);
            }
        }
    };

    const syncState = (payload) => {
        state.board = payload.board || state.board;
        state.turn = payload.turn || state.turn;
        state.winner = payload.winner || null;
        renderBoard();
        clearSelection();
        resetTimer();

        if (state.winner) {
            setStatus(`${colorLabel(state.winner)} wins.`);
            window.setTimeout(() => {
                redirectToWinPage(state.winner);
            }, 500);
            return;
        }
        setStatus(`${colorLabel(state.turn)} to move.`);
    };

    const submitMove = async (start, end) => {
        setBusy(true);
        try {
            const response = await fetch("/game/move", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    game_type: gameType,
                    start,
                    end,
                    ai: false
                })
            });

            const payload = await response.json();
            if (!response.ok) {
                setStatus(payload.error || "Move failed.");
                return;
            }

            appendHistory(payload.player_move);
            syncState(payload);
        } catch (error) {
            setStatus("Unable to reach game server.");
        } finally {
            setBusy(false);
        }
    };

    const handleTimeout = async () => {
        if (timeoutInFlight || state.winner) {
            return;
        }
        timeoutInFlight = true;
        setBusy(true);
        const expiredTurn = state.turn;
        setStatus(`${colorLabel(expiredTurn)} timed out. Passing turn.`);
        appendHistoryNote(`${colorLabel(expiredTurn)} turn timed out`);
        clearSelection();

        try {
            const response = await fetch("/game/timeout-turn", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    game_type: gameType,
                    ai: false
                })
            });

            const payload = await response.json();
            if (!response.ok) {
                setStatus(payload.error || "Timeout handling failed.");
                return;
            }
            syncState(payload);
        } catch (error) {
            setStatus("Unable to reach game server.");
        } finally {
            timeoutInFlight = false;
            setBusy(false);
        }
    };

    const startTimer = () => {
        if (timerHandle) {
            clearInterval(timerHandle);
        }
        renderTimer();
        timerHandle = window.setInterval(() => {
            if (state.winner || timeoutInFlight) {
                return;
            }
            remainingSeconds -= 1;
            renderTimer();
            if (remainingSeconds <= 0) {
                handleTimeout();
            }
        }, 1000);
    };

    boardEl.addEventListener("click", async (event) => {
        if (boardBusy || state.winner) {
            return;
        }

        const square = event.target.closest(".square");
        if (!square || !boardEl.contains(square)) {
            return;
        }

        const row = Number(square.dataset.row);
        const col = Number(square.dataset.col);
        const piece = state.board[row]?.[col];
        const color = pieceColor(piece);

        if (!selectedSquare) {
            if (color !== state.turn) {
                setStatus(`${colorLabel(state.turn)}: select your piece.`);
                return;
            }
            selectedSquare = [row, col];
            square.classList.add("selected");
            setStatus(`Selected ${formatSquare(selectedSquare)}. Choose destination.`);
            return;
        }

        if (selectedSquare[0] === row && selectedSquare[1] === col) {
            clearSelection();
            setStatus(`${colorLabel(state.turn)} to move.`);
            return;
        }

        if (color === state.turn) {
            clearSelection();
            selectedSquare = [row, col];
            square.classList.add("selected");
            setStatus(`Selected ${formatSquare(selectedSquare)}. Choose destination.`);
            return;
        }

        const start = selectedSquare.slice();
        clearSelection();
        await submitMove(start, [row, col]);
    });

    if (leaveButton) {
        leaveButton.addEventListener("click", () => {
            window.location.href = "/lobby";
        });
    }

    const init = async () => {
        setBusy(true);
        try {
            const response = await fetch(`/game/game?type=${encodeURIComponent(gameType)}`);
            const payload = await response.json();
            if (!response.ok) {
                setStatus(payload.error || "Failed to load board.");
                return;
            }
            syncState(payload);
            if (historyEl) {
                historyEl.innerHTML = "";
            }
            moveNumber = 1;
            completedMoves = 0;
            gameStartAt = Date.now();
            winRedirected = false;
        } catch (error) {
            setStatus("Failed to load game.");
        } finally {
            setBusy(false);
        }
    };

    startTimer();
    init();
})();
