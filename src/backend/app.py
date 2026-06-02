from flask import Flask, jsonify, render_template
from flask_cors import CORS
from gpiozero import LED

app = Flask(__name__)
CORS(app)

# GPIO pins
led = LED(17)
DHT11_PIN = 27

# Try CircuitPython DHT library first (adafruit-circuitpython-dht)
try:
    import adafruit_dht
    HAS_CIRCUITPY_DHT = True
except Exception:
    adafruit_dht = None
    HAS_CIRCUITPY_DHT = False

# Fallback to legacy Adafruit_DHT (if installed)
try:
    import Adafruit_DHT as legacy_Adafruit_DHT
    HAS_LEGACY_DHT = True
except Exception:
    legacy_Adafruit_DHT = None
    HAS_LEGACY_DHT = False

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/led/status', methods=['GET'])
def led_status():
    return jsonify({'on': led.is_lit})

@app.route('/api/led/on', methods=['POST'])
def led_on():
    led.on()
    return jsonify({'on': led.is_lit})

@app.route('/api/led/off', methods=['POST'])
def led_off():
    led.off()
    return jsonify({'on': led.is_lit})

@app.route('/api/led/toggle', methods=['POST'])
def led_toggle():
    if led.is_lit:
        led.off()
    else:
        led.on()
    return jsonify({'on': led.is_lit})

@app.route('/api/temperature', methods=['GET'])
def get_temperature():
    # Try CircuitPython DHT (preferred)
    if HAS_CIRCUITPY_DHT:
        try:
            import board
            # board exposes attributes like D4, D17, D27 — derive attribute name from pin number
            pin_attr_name = f"D{DHT11_PIN}"
            pin = getattr(board, pin_attr_name, None)
            if pin is None:
                return jsonify({'error': f'board module has no pin {pin_attr_name}. Check pin mapping.'}), 500

            dht = adafruit_dht.DHT11(pin)
            try:
                temperature = dht.temperature
                humidity = dht.humidity
            finally:
                # some versions require explicit cleanup
                try:
                    dht.exit()
                except Exception:
                    pass

            if temperature is None and humidity is None:
                return jsonify({'error': 'Failed to read from DHT11 sensor (CircuitPython).'}), 500
            return jsonify({'temperature_c': temperature, 'humidity': humidity})
        except RuntimeError as e:
            # DHT read timing issues are common; surface the message
            return jsonify({'error': f'DHT read error: {e}'}), 500
        except Exception as e:
            # Fall through to legacy fallback if available
            if not HAS_LEGACY_DHT:
                return jsonify({'error': f'Failed to read DHT11 (CircuitPython): {e}'}), 500

    # Fallback: legacy Adafruit_DHT
    if HAS_LEGACY_DHT:
        humidity, temperature = legacy_Adafruit_DHT.read_retry(legacy_Adafruit_DHT.DHT11, DHT11_PIN)
        if temperature is None and humidity is None:
            return jsonify({'error': 'Failed to read from DHT11 sensor (legacy Adafruit_DHT).'}), 500
        return jsonify({'temperature_c': temperature, 'humidity': humidity})

    return jsonify({'error': 'No DHT library installed. Install adafruit-circuitpython-dht and adafruit-blinka, or Adafruit_DHT.'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)