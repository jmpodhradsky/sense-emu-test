#had to update .venv file pyvenv.cfg to include system pkgs
from sense_emu import SenseHat
import time

sense = SenseHat()

# Clear display and set a test color
sense.clear(0, 0, 0)
sense.show_message("RP5 Sim", text_colour=[0, 255, 0], scroll_speed=0.08)

# Read simulated sensor data
temp = sense.get_temperature()
humidity = sense.get_humidity()
print(f"Simulated Temp: {temp:.1f} °C, Humidity: {humidity:.1f}%")
