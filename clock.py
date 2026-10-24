from sense_emu import SenseHat
import time

sense = SenseHat()

# Each digit (0-9) is drawn on a 4x4 mini-grid (16 pixels per digit).
# 1 = LED on, 0 = LED off.
# The left column of every 4x4 box is kept 0 to leave a 1-pixel gap between digits.
number = [
    0, 1, 1, 1,  # Zero
    0, 1, 0, 1,
    0, 1, 0, 1,
    0, 1, 1, 1,

    0, 0, 1, 0,  # One
    0, 0, 1, 0,
    0, 0, 1, 0,
    0, 0, 1, 0,

    0, 1, 1, 1,  # Two
    0, 0, 0, 1,
    0, 1, 1, 0,
    0, 1, 1, 1,

    0, 1, 1, 1,  # Three
    0, 0, 1, 1,
    0, 0, 0, 1,
    0, 1, 1, 1,

    0, 1, 0, 1,  # Four
    0, 1, 0, 1,
    0, 1, 1, 1,
    0, 0, 0, 1,

    0, 1, 1, 1,  # Five
    0, 1, 0, 0,
    0, 0, 1, 1,
    0, 1, 1, 1,

    0, 1, 0, 0,  # Six
    0, 1, 1, 1,
    0, 1, 0, 1,
    0, 1, 1, 1,

    0, 1, 1, 1,  # Seven
    0, 0, 0, 1,
    0, 0, 1, 0,
    0, 1, 0, 0,

    0, 1, 1, 1,  # Eight
    0, 1, 0, 1,
    0, 1, 1, 1,
    0, 1, 2, 1,

    0, 1, 1, 1,  # Nine
    0, 1, 0, 1,
    0, 1, 1, 1,
    0, 0, 0, 1,
]

hourColour = [255, 255, 255]  # White for top row (hours)
minuteColour = [0, 255, 255]  # Cyan for bottom row (minutes)
empty = [0, 0, 0]             # Off / black


def update_clock():
    """Build and display the current time on the 8x8 LED grid."""
    clockImage = [0] * 64

    current_time = time.localtime()
    hour = current_time.tm_hour % 12 or 12  # Convert 0-23 into 12-hour format (1-12)
    minute = current_time.tm_min

    # Stamp the four 4x4 digit stencils into the 8x8 clockImage array
    pixelOffset = 0
    index = 0

    for indexLoop in range(0, 4):
        for counterLoop in range(0, 4):
            # Shift top row 1 pixel left so hours start at (0,0)
            if counterLoop > 0:
                # Top-left quadrant: Hour tens digit (columns 0-2)
                clockImage[index - 1] = number[int(hour / 10) * 16 + pixelOffset]
                # Top-right quadrant: Hour ones digit (columns 4-6)
                clockImage[index + 3] = number[int(hour % 10) * 16 + pixelOffset]

            # Bottom-left quadrant: Minute tens digit (columns 1-3)
            clockImage[index + 32] = number[int(minute / 10) * 16 + pixelOffset]
            # Bottom-right quadrant: Minute ones digit (columns 5-7)
            clockImage[index + 36] = number[int(minute % 10) * 16 + pixelOffset]

            pixelOffset = pixelOffset + 1
            index = index + 1
        index = index + 4

    # Paint the 1s and 0s with actual RGB colors
    for index in range(0, 64):
        if clockImage[index]:
            if index < 32:
                clockImage[index] = hourColour
            else:
                clockImage[index] = minuteColour
        else:
            clockImage[index] = empty

    sense.low_light = True
    sense.set_pixels(clockImage)


if __name__ == "__main__":
    try:
        while True:
            update_clock()
            time.sleep(1)
    except KeyboardInterrupt:
        sense.clear()

