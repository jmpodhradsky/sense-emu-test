import time

from sense_emu import SenseHat

from clock import ClockApp
from conway_game.conway import ConwayApp

# Three states for the launcher state machine
STATE_HOME = "HOME"      # Default Clock homepage
STATE_PICKER = "PICKER"  # Previewing an app icon with Left/Right before launching
STATE_APP = "APP"        # Running the selected app

POLL_INTERVAL = 0.05     # Check the joystick mailbox 20 times per second (50ms)


def apply_hardware_settings(sense, low_light):
    """Wipe the LED matrix and set brightness cleanly when switching screens."""
    sense.clear()
    sense.low_light = low_light


def main():
    sense = SenseHat()

    # Homepage app (always starts here and returns here on Center-click)
    home_app = ClockApp()

    # List of all apps in the carousel (index 0 is the Clock homepage).
    # To add a new app later, import it and add it here!
    apps = [
        home_app,
        ConwayApp(),
    ]

    state = STATE_HOME
    selected_app_index = 0
    active_app = home_app

    # Clear any old joystick presses sitting in the mailbox before we start
    sense.stick.get_events()
    apply_hardware_settings(sense, home_app.low_light)
    next_draw_time = 0.0

    try:
        while True:
            # 1. Open the joystick mailbox and handle any new button presses
            for event in sense.stick.get_events():
                if event.action != "pressed":
                    continue

                direction = event.direction

                # State 1: On the Clock Homepage
                if state == STATE_HOME:
                    if direction == "right":
                        state = STATE_PICKER
                        selected_app_index = 1 % len(apps)
                        apply_hardware_settings(sense, False)
                        apps[selected_app_index].draw_preview(sense)
                    elif direction == "left":
                        state = STATE_PICKER
                        selected_app_index = (len(apps) - 1) % len(apps)
                        apply_hardware_settings(sense, False)
                        apps[selected_app_index].draw_preview(sense)

                # State 2: In the App Picker (previewing an app icon)
                elif state == STATE_PICKER:
                    if direction == "right":
                        selected_app_index = (selected_app_index + 1) % len(apps)
                        apps[selected_app_index].draw_preview(sense)
                    elif direction == "left":
                        selected_app_index = (selected_app_index - 1) % len(apps)
                        apps[selected_app_index].draw_preview(sense)
                    elif direction == "middle":
                        # Center-click launches the previewed app (or returns to Clock if index 0)
                        active_app = apps[selected_app_index]
                        if active_app is home_app:
                            state = STATE_HOME
                        else:
                            state = STATE_APP
                            active_app.start()
                        apply_hardware_settings(sense, active_app.low_light)
                        next_draw_time = 0.0

                # State 3: Inside a running App (route 4 directions to the app, middle exits to Clock)
                elif state == STATE_APP:
                    if direction == "middle":
                        state = STATE_HOME
                        active_app = home_app
                        apply_hardware_settings(sense, home_app.low_light)
                        next_draw_time = 0.0
                    elif direction == "up":
                        active_app.on_up()
                        next_draw_time = 0.0
                    elif direction == "down":
                        active_app.on_down()
                        next_draw_time = 0.0
                    elif direction == "left":
                        active_app.on_left()
                        next_draw_time = 0.0
                    elif direction == "right":
                        active_app.on_right()
                        next_draw_time = 0.0

            # 2. Draw the next frame if we are in HOME or APP mode and the timer is up
            now = time.monotonic()
            if state in (STATE_HOME, STATE_APP) and now >= next_draw_time:
                active_app.draw(sense)
                next_draw_time = now + active_app.frame_delay

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        sense.clear()


if __name__ == "__main__":
    main()
