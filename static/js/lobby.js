const modeButtons = document.querySelectorAll(".mode-btn");
const gameButtons = document.querySelectorAll(".game-card");
const playButton = document.getElementById("play-btn");
const playNote = document.getElementById("play-note");

const getActive = (buttons, attr) => {
    const active = Array.from(buttons).find((btn) => btn.classList.contains("active"));
    return active ? active.getAttribute(attr) : null;
};

modeButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
        modeButtons.forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        playNote.textContent = "";
    });
});

gameButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
        gameButtons.forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        playNote.textContent = "";
    });
});

if (playButton) {
    playButton.addEventListener("click", () => {
        const mode = getActive(modeButtons, "data-mode");
        const game = getActive(gameButtons, "data-game") || "checkers";

        if (game === "online") {
            playNote.textContent = "Online rooms are still in progress. Choose Chess or Checkers.";
            return;
        }

        if (mode === "ai") {
            window.location.href = `/game/ai?game=${encodeURIComponent(game)}`;
            return;
        }

        if (mode === "pvp") {
            window.location.href = `/game/pvp?game=${encodeURIComponent(game)}`;
            return;
        }

        playNote.textContent = "Select a valid mode.";
    });
}
