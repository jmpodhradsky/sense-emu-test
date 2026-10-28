class BaseApp:
    """Shared blueprint (base class) for all Sense HAT apps."""

    name = "App"
    icon_letter = "?"
    icon_color = (255, 255, 255)
    frame_delay = 0.5  # Seconds between draw() calls
    low_light = False  # Whether this app prefers dimmed LEDs

    def start(self):
        """Called every time this app is opened to set up its starting state."""

    def draw(self, sense):
        """Draw a single frame to the 8x8 LED matrix."""

    def draw_preview(self, sense):
        """
        Draw this app's preview card in the App Picker.
        Apps can override this method later to draw custom 8x8 pixel art.
        """
        sense.show_letter(self.icon_letter, text_colour=self.icon_color)

    # Default joystick direction handlers (do nothing unless an app overrides them)
    def on_up(self):
        pass

    def on_down(self):
        pass

    def on_left(self):
        pass

    def on_right(self):
        pass
