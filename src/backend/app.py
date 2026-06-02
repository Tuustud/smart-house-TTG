from flask import Flask, jsonify, render_template
from flask_cors import CORS
from gpiozero import LED

app = Flask(__name__)
CORS(app)

led = LED(4)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
