import time
import random

def read_sensor_data():
    # Simulate reading data from a sensor
    return random.uniform(20.0, 30.0)  # Simulated temperature in Celsius

def calibrate_sensor(sensor_value, calibration_factor):
    # Adjust the sensor value based on the calibration factor
    return sensor_value + calibration_factor

def main():
    calibration_factor = 1.5  # Example calibration factor
    print("Starting sensor calibration...")

    for _ in range(5):  # Calibrate 5 times
        sensor_value = read_sensor_data()
        calibrated_value = calibrate_sensor(sensor_value, calibration_factor)
        print(f"Raw sensor value: {sensor_value:.2f} °C, Calibrated value: {calibrated_value:.2f} °C")
        time.sleep(1)  # Simulate time delay between readings

    print("Sensor calibration completed.")

if __name__ == "__main__":
    main()