MAX_BRIGHTNESS_STEPS = 8
BRIGHTNESS_STEP = 4  # Default to 4/8 (50% brightness)
BRIGHTNESS = BRIGHTNESS_STEP / MAX_BRIGHTNESS_STEPS


def get_brightness_step():
    """Return the current brightness step (1 to 8)."""
    return BRIGHTNESS_STEP


def change_brightness_step(delta):
    """Adjust the global brightness step by delta, clamped safely between 1 and 8."""
    global BRIGHTNESS_STEP, BRIGHTNESS
    BRIGHTNESS_STEP = max(1, min(MAX_BRIGHTNESS_STEPS, BRIGHTNESS_STEP + delta))
    BRIGHTNESS = BRIGHTNESS_STEP / MAX_BRIGHTNESS_STEPS
    return BRIGHTNESS_STEP


def scale_color(color):
    """Dim an [R, G, B] color using the live global BRIGHTNESS factor."""
    return [int(channel * BRIGHTNESS) for channel in color]


def scale_pixels(pixels):
    """Dim a 64-pixel list of [R, G, B] colors using the live global BRIGHTNESS factor."""
    return [scale_color(pixel) for pixel in pixels]


def get_sense_hat():
    """
    Connect to the physical Sense HAT if attached; otherwise fall back
    to the desktop Sense HAT Emulator.
    """
    try:
        from sense_hat import SenseHat

        return SenseHat()
    except (ImportError, OSError):
        from sense_emu import SenseHat

        return SenseHat()


class BaseApp:
    """Shared blueprint (base class) for all Sense HAT apps."""

    name = "App"
    icon_letter = "?"
    icon_color = (255, 255, 255)
    frame_delay = 0.5  # Seconds between draw() calls
    low_light = True   # Whether this app prefers dimmed LEDs

    def start(self):
        """Called every time this app is opened to set up its starting state."""

    def draw(self, sense):
        """Draw a single frame to the 8x8 LED matrix."""

    def draw_preview(self, sense):
        """
        Draw this app's preview card in the App Picker.
        Apps can override this method later to draw custom 8x8 pixel art.
        """
        sense.show_letter(self.icon_letter, text_colour=scale_color(self.icon_color))

    # Default joystick direction handlers (do nothing unless an app overrides them)
    def on_up(self):
        pass

    def on_down(self):
        pass

    def on_left(self):
        pass

    def on_right(self):
        pass
