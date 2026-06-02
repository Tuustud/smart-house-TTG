from flask import Flask, jsonify, render_template
from flask_cors import CORS
from gpiozero import LED

app = Flask(__name__)
CORS(app)

led = LED(17)
DHT11_PIN = 27

try:
    import Adafruit_DHT
except ImportError:
    Adafruit_DHT = None

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
    if Adafruit_DHT is None:
        return jsonify({'error': 'Adafruit_DHT library is not installed. Install with pip install Adafruit_DHT.'}), 500

    humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, DHT11_PIN)
    if temperature is None and humidity is None:
        return jsonify({'error': 'Failed to read from DHT11 sensor. Check wiring and power.'}), 500

    return jsonify({'temperature_c': temperature, 'humidity': humidity})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
