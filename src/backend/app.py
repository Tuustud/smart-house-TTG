from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import glob
import os

app = Flask(__name__)
CORS(app)

sensors = [
    {'id': '1', 'type': 'temperature', 'value': None, 'error': None},
    {'id': '2', 'type': 'humidity', 'value': 45.0},
]

def read_gpio4_temperature():
    base_dir = '/sys/bus/w1/devices'
    if not os.path.isdir(base_dir):
        return None, '1-Wire devices directory is missing. Enable w1-gpio on the Raspberry Pi.'

    device_folders = glob.glob(os.path.join(base_dir, '28*'))
    if not device_folders:
        return None, 'No DS18B20 temperature sensor found on GPIO4.'

    device_file = os.path.join(device_folders[0], 'w1_slave')
    try:
        with open(device_file, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        return None, f'Sensor file not found: {device_file}'

    if len(lines) < 2 or not lines[0].strip().endswith('YES'):
        return None, 'Sensor data invalid or CRC check failed.'

    temp_marker = lines[1].find('t=')
    if temp_marker == -1:
        return None, 'Temperature value not found in sensor output.'

    temp_c = float(lines[1][temp_marker + 2:]) / 1000.0
    return temp_c, None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/sensors', methods=['GET'])
def get_sensors():
    temp, error = read_gpio4_temperature()
    sensors[0]['value'] = temp if error is None else None
    sensors[0]['error'] = error
    return jsonify({'sensors': sensors})

@app.route('/api/sensors/<sensor_id>', methods=['GET'])
def get_sensor(sensor_id):
    if sensor_id == '1':
        temp, error = read_gpio4_temperature()
        if error:
            return jsonify({'id': '1', 'type': 'temperature', 'value': None, 'error': error}), 500
        return jsonify({'id': '1', 'type': 'temperature', 'value': temp})

    if sensor_id == '2':
        return jsonify({'id': '2', 'type': 'humidity', 'value': 45.0})

    return jsonify({'error': 'Sensor not found.'}), 404

@app.route('/api/sensors', methods=['POST'])
def add_sensor():
    data = request.json or {}
    new_id = str(int(sensors[-1]['id']) + 1 if sensors else 1)
    sensor = {
        'id': new_id,
        'type': data.get('type', 'unknown'),
        'value': data.get('value', 0),
    }
    sensors.append(sensor)
    return jsonify(sensor), 201

@app.route('/api/sensors/<sensor_id>', methods=['DELETE'])
def delete_sensor(sensor_id):
    global sensors
    sensors = [s for s in sensors if s['id'] != sensor_id]
    return jsonify({'message': f'Sensor {sensor_id} deleted.'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
