from sense_hat import SenseHat
import time

def main():
    # 1. Initialize connection to the physical Sense HAT
    sense = SenseHat()
    sense.clear()  # Ensure display starts blank

    # 2. Colors (R, G, B)
    cyan = (0, 255, 255)
    dark_blue = (0, 0, 40)
    green = (0, 255, 0)

    print("=== Sense HAT Hardware Test ===")

    # 3. Read environmental sensors
    temp = sense.get_temperature()
    humidity = sense.get_humidity()
    pressure = sense.get_pressure()

    print(f"Temperature : {temp:.1f} °C ({(temp * 9/5 + 32):.1f} °F)")
    print(f"Humidity    : {humidity:.1f} %")
    print(f"Pressure    : {pressure:.1f} mbar / hPa")

    # 4. Display scrolling text on the 8x8 LED matrix
    msg = f"T:{temp:.0f}C H:{humidity:.0f}%"
    print(f"Displaying message on LED matrix: '{msg}'...")
    sense.show_message(msg, text_colour=cyan, back_colour=dark_blue, scroll_speed=0.07)

    # 5. Brief green flash to indicate test completion
    sense.clear(green)
    time.sleep(0.5)
    sense.clear()
    print("Test completed successfully.")

if __name__ == "__main__":
    main()

