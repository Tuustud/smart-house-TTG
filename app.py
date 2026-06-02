#!/usr/bin/env python3
"""
Shooters Smart House Controller
Flask web server for Raspberry Pi
Run with: sudo python3 app.py
"""

import threading
import time
import signal
import sys
from flask import Flask, render_template, request, jsonify

# ─── Hardware Library Imports ────────────────────────────────────────────────
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except (ImportError, RuntimeError):
    GPIO_AVAILABLE = False
    print("[WARN] RPi.GPIO not available — running in mock mode")

try:
    import adafruit_dht
    import board as adafruit_board
    DHT_AVAILABLE = True
except (ImportError, RuntimeError):
    DHT_AVAILABLE = False
    print("[WARN] adafruit_dht not available")

try:
    from RPLCD.i2c import CharLCD
    LCD_AVAILABLE = True
except (ImportError, Exception):
    LCD_AVAILABLE = False
    print("[WARN] RPLCD not available")

try:
    import neopixel
    import board as neo_board
    NEOPIXEL_AVAILABLE = True
except (ImportError, Exception):
    NEOPIXEL_AVAILABLE = False
    print("[WARN] neopixel not available — NeoPixel in mock mode")

# ─── Pin & Device Configuration ──────────────────────────────────────────────
LED_PIN      = 17     # GPIO 17
DHT_PIN      = 27     # GPIO 27
SERVO_PIN    = 26     # GPIO 26
NEOPIXEL_PIN = 16     # GPIO 16  ← if unreliable, change to 18 (PWM0)
NUM_LEDS     = 30     # ← Adjust to your strip length

LCD_ADDRESS  = 0x27   # Common: 0x27 or 0x3F — run 'i2cdetect -y 3' to confirm
LCD_I2C_PORT = 3      # After dtoverlay=i2c-gpio,bus=3,i2c_gpio_sda=5,i2c_gpio_scl=6

# ─── Shared Application State ────────────────────────────────────────────────
state = {
    "led": False,
    "servo_angle": 90,
    "neopixel_color": "#ff6600",
    "neopixel_brightness": 50,
    "dht": {"temperature": "--", "humidity": "--"},
}

app = Flask(__name__)

# ─── GPIO Setup ──────────────────────────────────────────────────────────────
servo_pwm = None

if GPIO_AVAILABLE:
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(LED_PIN, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(SERVO_PIN, GPIO.OUT)
    servo_pwm = GPIO.PWM(SERVO_PIN, 50)  # 50 Hz
    servo_pwm.start(7.5)                  # Neutral (90°)
    print(f"[GPIO] LED on pin {LED_PIN}, Servo on pin {SERVO_PIN}")

# ─── DHT11 Setup ─────────────────────────────────────────────────────────────
dht_device = None
if DHT_AVAILABLE:
    try:
        dht_device = adafruit_dht.DHT11(getattr(adafruit_board, f"D{DHT_PIN}"))
        print(f"[DHT11] Sensor on GPIO {DHT_PIN}")
    except Exception as e:
        print(f"[WARN] DHT init error: {e}")

# ─── LCD Setup ───────────────────────────────────────────────────────────────
lcd = None
if LCD_AVAILABLE:
    try:
        lcd = CharLCD(
            i2c_expander="PCF8574",
            address=LCD_ADDRESS,
            port=LCD_I2C_PORT,
            cols=16, rows=2,
            charmap="A02",
            auto_linebreaks=False,
        )
        lcd.backlight_enabled = True
        lcd.clear()
        print(f"[LCD] 16x2 on I2C bus {LCD_I2C_PORT} at address 0x{LCD_ADDRESS:02X}")
    except Exception as e:
        print(f"[WARN] LCD init error: {e}")

# ─── NeoPixel Setup ──────────────────────────────────────────────────────────
pixels = None
if NEOPIXEL_AVAILABLE:
    try:
        pixel_pin = getattr(neo_board, f"D{NEOPIXEL_PIN}")
        pixels = neopixel.NeoPixel(
            pixel_pin, NUM_LEDS,
            brightness=0.5,
            auto_write=False,
            pixel_order=neopixel.GRB,
        )
        pixels.fill((255, 102, 0))  # Warm amber default
        pixels.show()
        print(f"[NeoPixel] {NUM_LEDS} pixels on GPIO {NEOPIXEL_PIN}")
    except Exception as e:
        print(f"[WARN] NeoPixel init error: {e}")

# ─── Helper Functions ────────────────────────────────────────────────────────
def angle_to_duty(angle: int) -> float:
    """Convert servo angle 0–180 to duty cycle 2.5–12.5."""
    return 2.5 + (angle / 180.0) * 10.0


def hex_to_rgb(hex_color: str) -> tuple:
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


# ─── Background Thread: DHT11 Reader ─────────────────────────────────────────
def dht_reader_thread():
    while True:
        if dht_device:
            try:
                t = dht_device.temperature
                h = dht_device.humidity
                if t is not None and h is not None:
                    state["dht"]["temperature"] = round(float(t), 1)
                    state["dht"]["humidity"] = round(float(h), 1)
            except Exception:
                pass  # DHT11 occasionally glitches; just wait for next read
        time.sleep(5)


# ─── Background Thread: LCD Scroll ───────────────────────────────────────────
def lcd_scroll_thread():
    """Row 1 — scrolling pub name; Row 2 — current temperature."""
    pub_name    = "Shooters"
    scroll_buf  = "    " + pub_name + "    "   # 4-space padding each side
    scroll_len  = len(scroll_buf)
    pos         = 0

    while True:
        if lcd:
            try:
                # 16-char sliding window
                doubled = scroll_buf + scroll_buf
                row1    = doubled[pos : pos + 16]
                lcd.cursor_pos = (0, 0)
                lcd.write_string(row1)

                # Temperature on row 2 (\xdf = ° on HD44780 charset A02)
                temp   = state["dht"]["temperature"]
                row2   = f"Temp: {temp}\xdfC".ljust(16)[:16]
                lcd.cursor_pos = (1, 0)
                lcd.write_string(row2)

                pos = (pos + 1) % scroll_len
            except Exception as e:
                print(f"[LCD] Write error: {e}")

        time.sleep(0.35)


# Start daemon threads
threading.Thread(target=dht_reader_thread, daemon=True).start()
threading.Thread(target=lcd_scroll_thread,  daemon=True).start()

# ─── Flask Routes ─────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/state")
def get_state():
    return jsonify(state)


@app.route("/api/dht")
def get_dht():
    return jsonify(state["dht"])


@app.route("/api/led/toggle", methods=["POST"])
def toggle_led():
    state["led"] = not state["led"]
    if GPIO_AVAILABLE:
        GPIO.output(LED_PIN, GPIO.HIGH if state["led"] else GPIO.LOW)
    print(f"[LED] {'ON' if state['led'] else 'OFF'}")
    return jsonify({"led": state["led"]})


@app.route("/api/servo", methods=["POST"])
def set_servo():
    data  = request.get_json(force=True)
    angle = max(0, min(180, int(data.get("angle", 90))))
    state["servo_angle"] = angle

    if GPIO_AVAILABLE and servo_pwm:
        servo_pwm.ChangeDutyCycle(angle_to_duty(angle))
        time.sleep(0.25)
        servo_pwm.ChangeDutyCycle(0)  # Kill signal to prevent jitter

    print(f"[Servo] Angle → {angle}°")
    return jsonify({"angle": angle})


@app.route("/api/neopixel", methods=["POST"])
def set_neopixel():
    data       = request.get_json(force=True)
    color      = data.get("color", state["neopixel_color"])
    brightness = int(data.get("brightness", state["neopixel_brightness"]))
    brightness = max(0, min(100, brightness))

    state["neopixel_color"]      = color
    state["neopixel_brightness"] = brightness

    if pixels:
        pixels.brightness = brightness / 100.0
        r, g, b = hex_to_rgb(color)
        pixels.fill((r, g, b))
        pixels.show()

    print(f"[NeoPixel] Color {color}  Brightness {brightness}%")
    return jsonify({"color": color, "brightness": brightness})


@app.route("/api/neopixel/off", methods=["POST"])
def neopixel_off():
    state["neopixel_color"] = "#000000"
    if pixels:
        pixels.fill((0, 0, 0))
        pixels.show()
    print("[NeoPixel] OFF")
    return jsonify({"color": "#000000"})


# ─── Cleanup ──────────────────────────────────────────────────────────────────
def cleanup(sig=None, frame=None):
    print("\n[INFO] Shutting down — cleaning up hardware…")
    if GPIO_AVAILABLE:
        if servo_pwm:
            servo_pwm.stop()
        GPIO.cleanup()
    if pixels:
        pixels.fill((0, 0, 0))
        pixels.show()
    if lcd:
        lcd.clear()
        lcd.backlight_enabled = False
    print("[INFO] Done. Goodbye.")
    sys.exit(0)


signal.signal(signal.SIGINT,  cleanup)
signal.signal(signal.SIGTERM, cleanup)

# ─── Entry Point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("  🍺  Shooters Smart House Server")
    print("  Listening on http://0.0.0.0:5000")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
