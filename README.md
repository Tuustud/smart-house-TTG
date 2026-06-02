# 🍺 Shooters — Smart House Setup Guide

## Project Structure
```
smart_house/
├── app.py               ← Main Flask server
├── requirements.txt     ← Python dependencies
├── README.md
└── templates/
    └── index.html       ← Web interface
```

---

## 1. Hardware Wiring

### LED Lamp — GPIO 17
```
GPIO 17 ──→ 330Ω resistor ──→ LED (+)
GND     ──→ LED (−)
```

### DHT11 Sensor — GPIO 27
```
3.3V    ──→ DHT11 VCC
GND     ──→ DHT11 GND
GPIO 27 ──→ DHT11 DATA  (add 10kΩ pull-up to 3.3V)
```

### Servo Motor — GPIO 26
```
5V      ──→ Servo Red
GND     ──→ Servo Brown/Black
GPIO 26 ──→ Servo Orange/Yellow (signal)
```
> ⚠️ For multiple servos or a strong servo, use an external 5V supply rather than
> powering directly from the Pi's 5V pin.

### 16×2 LCD I²C — SDA=GPIO 5, SCL=GPIO 6
These are non-standard I²C pins, so you must enable a software I²C bus.

**Step 1** — Open the boot config:
```bash
sudo nano /boot/firmware/config.txt
# (On older RPi OS it's /boot/config.txt)
```

**Step 2** — Add this line at the bottom:
```
dtoverlay=i2c-gpio,bus=3,i2c_gpio_sda=5,i2c_gpio_scl=6
```

**Step 3** — Reboot:
```bash
sudo reboot
```

**Step 4** — Verify the bus appeared and find your LCD's I²C address:
```bash
sudo apt install -y i2c-tools
i2cdetect -y 3
```
You should see `27` or `3f` in the grid. Update `LCD_ADDRESS` in `app.py` accordingly.

### NeoPixel Strip — GPIO 16
```
External 5V PSU (+) ──→ Strip VCC  (do NOT use Pi's 5V for more than ~5 LEDs)
External 5V PSU (−) ──→ Strip GND  AND  Pi GND  (common ground is required!)
GPIO 16             ──→ 300–500Ω resistor ──→ Strip DATA
```
> ⚠️ **GPIO 16 note:** The `rpi_ws281x` library officially supports GPIO 10, 12, 18, 21
> for DMA-driven timing. If GPIO 16 produces flickering or no output, switch the wire
> to **GPIO 18** and change `NEOPIXEL_PIN = 18` in `app.py`.

---

## 2. Software Installation

```bash
# 1. System packages
sudo apt update
sudo apt install -y python3-pip python3-dev libgpiod2 i2c-tools git

# 2. Enable I²C & SPI interfaces
sudo raspi-config
# → Interface Options → I2C → Enable
# → Interface Options → SPI → Enable  (needed by some NeoPixel setups)

# 3. Python libraries
pip3 install -r requirements.txt
```

---

## 3. Configuration

Open `app.py` and adjust the constants at the top if needed:

| Variable         | Default | Description                              |
|------------------|---------|------------------------------------------|
| `LED_PIN`        | 17      | GPIO for LED                             |
| `DHT_PIN`        | 27      | GPIO for DHT11                           |
| `SERVO_PIN`      | 26      | GPIO for servo signal                    |
| `NEOPIXEL_PIN`   | 16      | GPIO for NeoPixel data (try 18 if issue) |
| `NUM_LEDS`       | 30      | Number of pixels in your strip           |
| `LCD_ADDRESS`    | 0x27    | I²C address from `i2cdetect -y 3`        |
| `LCD_I2C_PORT`   | 3       | I²C bus number (set by dtoverlay)        |

---

## 4. Running the Server

NeoPixels require DMA memory access, so run as root:
```bash
cd smart_house
sudo python3 app.py
```

Open a browser on any device on the same network:
```
http://<raspberry-pi-ip>:5000
```

Find your Pi's IP address:
```bash
hostname -I
```

---

## 5. API Reference

| Method | Endpoint             | Body / Params                                     |
|--------|----------------------|---------------------------------------------------|
| GET    | `/api/state`         | Returns full device state JSON                    |
| GET    | `/api/dht`           | Returns `{ temperature, humidity }`               |
| POST   | `/api/led/toggle`    | Toggles LED, returns `{ led: bool }`              |
| POST   | `/api/servo`         | `{ "angle": 0–180 }`                              |
| POST   | `/api/neopixel`      | `{ "color": "#rrggbb", "brightness": 0–100 }`     |
| POST   | `/api/neopixel/off`  | Turns all pixels off                              |

---

## 6. Troubleshooting

**LCD shows nothing / I²C error:**
- Run `i2cdetect -y 3` and check address; try `0x3F` if `0x27` fails.
- Confirm the `dtoverlay` line is in the correct config file and you've rebooted.

**DHT11 always reads `--`:**
- Add a 10kΩ pull-up resistor from DATA pin to 3.3V.
- The DHT11 needs ~2 s warm-up time; wait a moment after boot.

**NeoPixels flicker or don't light:**
- Switch to GPIO 18 (PWM0) — the most reliable pin for `rpi_ws281x`.
- Make sure Pi GND and PSU GND share a common connection.
- Must run with `sudo` for DMA access.

**Servo jitters at rest:**
- The code already sends `ChangeDutyCycle(0)` after each move to suppress jitter.
  If it persists, add a small capacitor (100µF) across the servo power lines.
