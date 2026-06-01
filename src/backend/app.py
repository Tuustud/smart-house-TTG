from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# In-memory sensor data for a school project
sensors = [
    {"id": "1", "type": "temperature", "value": 22.5},
    {"id": "2", "type": "humidity", "value": 45.0},
]

@app.route('/')
def home():
    return "Welcome to the Smart House System!"

@app.route('/api/sensors', methods=['GET'])
def get_sensors():
    return jsonify({"sensors": sensors})

@app.route('/api/sensors/<sensor_id>', methods=['GET'])
def get_sensor(sensor_id):
    sensor = next((s for s in sensors if s['id'] == sensor_id), None)
    if sensor is None:
        return jsonify({"error": "Sensor not found."}), 404
    return jsonify(sensor)

@app.route('/api/sensors', methods=['POST'])
def add_sensor():
    data = request.json or {}
    new_id = str(int(sensors[-1]['id']) + 1 if sensors else 1)
    sensor = {
        "id": new_id,
        "type": data.get("type", "unknown"),
        "value": data.get("value", 0),
    }
    sensors.append(sensor)
    return jsonify(sensor), 201

@app.route('/api/sensors/<sensor_id>', methods=['DELETE'])
def delete_sensor(sensor_id):
    global sensors
    sensors = [s for s in sensors if s['id'] != sensor_id]
    return jsonify({"message": f"Sensor {sensor_id} deleted."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
