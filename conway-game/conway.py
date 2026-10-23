#had to update .venv file pyvenv.cfg to include system pkgs
import random
import time
from sense_hat import SenseHat

GRID_SIZE = 8
ALIVE_COLOR = [0, 255, 0]  # Green
DEAD_COLOR = [0, 0, 0]     # Off
FRAME_DELAY = 0.5          # Seconds between generations


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
            if 0 <= neighbor_row < GRID_SIZE and 0 <= neighbor_col < GRID_SIZE:
                if board[neighbor_row][neighbor_col] == ALIVE_COLOR:
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

            if is_alive and neighbors in (2, 3):
                next_board[row][col] = ALIVE_COLOR
            elif not is_alive and neighbors == 3:
                next_board[row][col] = ALIVE_COLOR
            else:
                next_board[row][col] = DEAD_COLOR


def flatten_board(board):
    """Flatten the 8x8 2D board into a 64-element list for sense.set_pixels()."""
    return [pixel for row in board for pixel in row]


def main():
    sense = SenseHat()
    sense.clear(0, 0, 0)

    # Initialize the two buffers for double buffering
    current_board = create_random_board()
    next_board = create_empty_board()
    reset_requested = False

    def handle_joystick(event):
        """Interrupt callback triggered in the background when the joystick moves."""
        nonlocal reset_requested
        if event.action == "pressed":
            reset_requested = True

    # Register the interrupt callback for any joystick press
    sense.stick.direction_any = handle_joystick

    try:
        while True:
            # Safely apply the joystick reset at the start of a frame
            if reset_requested:
                current_board = create_random_board()
                reset_requested = False

            # Render the current board state to the 8x8 LED matrix
            sense.set_pixels(flatten_board(current_board))

            # Write the calculated next state into the secondary buffer
            compute_next_generation(current_board, next_board)

            # Swap buffers: next_board becomes current_board for the next frame
            current_board, next_board = next_board, current_board

            time.sleep(FRAME_DELAY)
    except KeyboardInterrupt:
        sense.clear(0, 0, 0)


if __name__ == "__main__":
    main()

