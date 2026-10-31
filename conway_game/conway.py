# had to update .venv file pyvenv.cfg to include system pkgs
import random
import sys
import time
from collections import deque
from pathlib import Path

# Allow running this file directly (`python3 conway_game/conway.py`) as well as via `main.py`
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from base_app import BaseApp, get_sense_hat, scale_color

GRID_SIZE = 8
ALIVE_COLOR = [0, 255, 0]        # Green
STILL_ALERT_COLOR = [255, 0, 0]  # Red flash for frozen still lifes
DEAD_COLOR = [0, 0, 0]           # Off
FRAME_DELAY = 0.5                # Seconds between generations
HISTORY_SIZE = 8                 # Number of prior generations to remember

STATE_DEAD = "DEAD"
STATE_STILL = "STILL"
STATE_OSCILLATOR = "OSCILLATOR"

GRACE_FRAMES = {
    STATE_DEAD: 1,         # 0.5s on a dark screen before resetting
    STATE_STILL: 8,        # 4.0s (8 frames) flashing Green/Red before resetting
    STATE_OSCILLATOR: 16,   # 8.0s PARTY MODE WOOO
}


def create_empty_board():
    """Create an 8x8 2D list initialized with dead cells."""
    return [[DEAD_COLOR for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]


def create_random_board(alive_probability=0.35):
    """Create an 8x8 2D list with randomly placed living cells."""
    board = create_empty_board()
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if random.random() < alive_probability:
                board[row][col] = ALIVE_COLOR
    return board


def count_neighbors(board, row, col):
    """Count the living neighbors around (row, col) safely within 8x8 boundaries."""
    alive_neighbors = 0
    for row_offset in (-1, 0, 1):
        for col_offset in (-1, 0, 1):
            if row_offset == 0 and col_offset == 0:
                continue  # Skip the cell itself

            neighbor_row = row + row_offset
            neighbor_col = col + col_offset

            # Check boundaries to prevent out-of-index errors
            if (
                0 <= neighbor_row < GRID_SIZE
                and 0 <= neighbor_col < GRID_SIZE
                and board[neighbor_row][neighbor_col] == ALIVE_COLOR
            ):
                alive_neighbors += 1

    return alive_neighbors


def compute_next_generation(current_board, next_board):
    """
    Read from current_board, apply Conway's rules, and write the result
    into next_board (double buffering).
    """
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            neighbors = count_neighbors(current_board, row, col)
            is_alive = current_board[row][col] == ALIVE_COLOR

            if (is_alive and neighbors in (2, 3)) or (not is_alive and neighbors == 3):
                next_board[row][col] = ALIVE_COLOR
            else:
                next_board[row][col] = DEAD_COLOR


def random_party_color():
    """Generate a bright, saturated random [R, G, B] color for Oscillator Party Mode."""
    channels = [
        random.randint(200, 255),  # One high channel guarantees brightness
        random.randint(0, 50),     # One low channel guarantees vivid color (not white)
        random.randint(0, 255),    # One free channel for variety
    ]
    random.shuffle(channels)
    return channels


def flatten_board(board, stuck_state=None, grace_remaining=0):
    """
    Flatten the 8x8 2D board into a 64-element pixel list for sense.set_pixels(),
    applying visual effects and software brightness scaling.
    """
    pixels = []
    for row in board:
        for cell in row:
            if cell != ALIVE_COLOR:
                pixels.append(DEAD_COLOR)
            elif stuck_state == STATE_STILL:
                # Alternate between Green and Red across the 8 grace frames
                color = ALIVE_COLOR if grace_remaining % 2 == 0 else STILL_ALERT_COLOR
                pixels.append(scale_color(color))
            elif stuck_state == STATE_OSCILLATOR:
                pixels.append(scale_color(random_party_color()))
            else:
                pixels.append(scale_color(ALIVE_COLOR))
    return pixels


def snapshot_board(board):
    """Create a lightweight 64-boolean tuple representing living cells on the board."""
    return tuple(
        pixel == ALIVE_COLOR
        for row in board
        for pixel in row
    )


def detect_stuck_state(snapshot, history):
    """
    Check if the current board snapshot is stuck.
    Returns STATE_DEAD, STATE_STILL, STATE_OSCILLATOR, or None.
    """
    if not any(snapshot):
        return STATE_DEAD
    if history and snapshot == history[-1]:
        return STATE_STILL
    if snapshot in history:
        return STATE_OSCILLATOR
    return None


class ConwayApp(BaseApp):
    """Conway's Game of Life app for the 8x8 Sense HAT grid."""

    name = "Conway"
    icon_letter = "C"
    icon_color = (0, 255, 0)  # Green preview letter in the App Picker
    frame_delay = FRAME_DELAY
    low_light = True

    def __init__(self):
        self.reset_board()

    def start(self):
        """Generate a fresh random board whenever Conway is opened."""
        self.reset_board()

    def draw_preview(self, sense):
        """Display custom 'LIFE' pixel art in the App Picker."""
        L = scale_color([0, 255, 100])   # Green
        I = scale_color([0, 200, 255])   # Cyan
        F = scale_color([255, 180, 0])   # Amber
        E = scale_color([255, 50, 200])  # Magenta
        _ = [0, 0, 0]                    # Off

        life_text = [
            L, _, _, _, I, I, I, _,
            L, _, _, _, _, I, _, _,
            L, _, _, _, _, I, _, _,
            L, L, L, _, I, I, I, _,
            F, F, F, _, E, E, E, _,
            F, F, _, _, E, E, _, _,
            F, _, _, _, E, _, _, _,
            F, _, _, _, E, E, E, _,
        ]

        sense.set_pixels(life_text)

    def reset_board(self):
        """Randomize the current board, clear the secondary buffer, and reset history."""
        self.current_board = create_random_board()
        self.next_board = create_empty_board()
        self.history = deque(maxlen=HISTORY_SIZE)
        self.stuck_state = None
        self.grace_remaining = 0

    # All 4 directions randomize the board for now; easy to customize individually later!
    def on_up(self):
        self.reset_board()

    def on_down(self):
        self.reset_board()

    def on_left(self):
        self.reset_board()

    def on_right(self):
        self.reset_board()

    def draw(self, sense):
        """Render the current generation and advance the board by one step."""
        if self.stuck_state is None:
            snapshot = snapshot_board(self.current_board)
            self.stuck_state = detect_stuck_state(snapshot, self.history)
            self.history.append(snapshot)
            if self.stuck_state is not None:
                self.grace_remaining = GRACE_FRAMES[self.stuck_state]

        sense.set_pixels(
            flatten_board(self.current_board, self.stuck_state, self.grace_remaining)
        )

        if self.stuck_state is not None:
            self.grace_remaining -= 1
            if self.grace_remaining <= 0:
                self.reset_board()
                return

        compute_next_generation(self.current_board, self.next_board)
        self.current_board, self.next_board = self.next_board, self.current_board


if __name__ == "__main__":
    sense = get_sense_hat()
    app = ConwayApp()
    app.start()
    sense.low_light = app.low_light
    try:
        while True:
            for event in sense.stick.get_events():
                if event.action == "pressed":
                    app.reset_board()
            app.draw(sense)
            time.sleep(app.frame_delay)
    except KeyboardInterrupt:
        sense.clear()
