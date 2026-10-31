import sys
import time
from pathlib import Path

# Allow running this file directly (`python3 system_tools/brightness.py`) as well as via `main.py`
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from base_app import (
    MAX_BRIGHTNESS_STEPS,
    BaseApp,
    change_brightness_step,
    get_brightness_step,
    get_sense_hat,
    scale_pixels,
)

BULB_GLASS = [255, 220, 0]     # Warm yellow bulb glass
BULB_CORE = [255, 255, 180]    # Bright inner filament glow
BULB_BASE = [160, 170, 180]    # Silver screw base
METER_ON = [0, 220, 255]       # Cyan level bar on the right edge
OFF = [0, 0, 0]                # Off / black


def build_brightness_screen(step=None):
    """
    Build the 64-pixel list showing the lightbulb on columns 0..5
    and the 8-step vertical level bar on column 7 (bottom-to-top).
    """
    current_step = step if step is not None else get_brightness_step()
    Y = BULB_GLASS
    W = BULB_CORE
    B = BULB_BASE
    _ = OFF

    grid = [
        [_, Y, Y, Y, Y, _, _, _],
        [Y, Y, W, W, Y, Y, _, _],
        [Y, W, Y, Y, W, Y, _, _],
        [Y, Y, Y, Y, Y, Y, _, _],
        [_, Y, Y, Y, Y, _, _, _],
        [_, B, B, B, B, _, _, _],
        [_, B, B, B, B, _, _, _],
        [_, _, B, B, _, _, _, _],
    ]

    # Fill column 7 from bottom (row 7 = step 1) to top (row 0 = step 8)
    for level in range(1, MAX_BRIGHTNESS_STEPS + 1):
        row = MAX_BRIGHTNESS_STEPS - level
        if current_step >= level:
            grid[row][7] = METER_ON

    flat_pixels = [pixel for row in grid for pixel in row]
    return scale_pixels(flat_pixels)


class BrightnessApp(BaseApp):
    """System tool to adjust global LED brightness across all apps."""

    name = "Brightness"
    icon_letter = "B"
    icon_color = (255, 220, 0)
    frame_delay = 0.2
    low_light = True

    def draw_preview(self, sense):
        """Display a centered 8x8 lightbulb icon in the App Picker."""
        Y = BULB_GLASS
        W = BULB_CORE
        B = BULB_BASE
        _ = OFF

        bulb_icon = [
            _, _, Y, Y, Y, Y, _, _,
            _, Y, Y, W, W, Y, Y, _,
            _, Y, W, Y, Y, W, Y, _,
            _, Y, Y, Y, Y, Y, Y, _,
            _, _, Y, Y, Y, Y, _, _,
            _, _, B, B, B, B, _, _,
            _, _, B, B, B, B, _, _,
            _, _, _, B, B, _, _, _,
        ]

        sense.set_pixels(scale_pixels(bulb_icon))

    def draw(self, sense):
        """Render the lightbulb and 8-dot brightness bar at the current global brightness."""
        sense.set_pixels(build_brightness_screen())

    def on_up(self):
        """Increase brightness by 1 step."""
        change_brightness_step(1)

    def on_down(self):
        """Decrease brightness by 1 step."""
        change_brightness_step(-1)

    def on_right(self):
        """Increase brightness by 3 steps."""
        change_brightness_step(3)

    def on_left(self):
        """Decrease brightness by 3 steps."""
        change_brightness_step(-3)


if __name__ == "__main__":
    sense = get_sense_hat()
    app = BrightnessApp()
    sense.low_light = app.low_light
    try:
        while True:
            for event in sense.stick.get_events():
                if event.action != "pressed":
                    continue
                if event.direction == "up":
                    app.on_up()
                elif event.direction == "down":
                    app.on_down()
                elif event.direction == "right":
                    app.on_right()
                elif event.direction == "left":
                    app.on_left()
            app.draw(sense)
            time.sleep(app.frame_delay)
    except KeyboardInterrupt:
        sense.clear()

