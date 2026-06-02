// This file contains the JavaScript code for the frontend application, handling client-side interactions and API calls.

document.addEventListener('DOMContentLoaded', function() {
    const ledStatus = document.getElementById('led-status');
    const temperatureStatus = document.getElementById('temperature-status');
    const humidityStatus = document.getElementById('humidity-status');

    function updateLedStatus(data) {
        ledStatus.textContent = data.on ? 'LED is ON' : 'LED is OFF';
    }

    function updateTemperatureStatus(data) {
        if (data.error) {
            temperatureStatus.textContent = 'Temperature error: ' + data.error;
            humidityStatus.textContent = '';
            return;
        }

        temperatureStatus.textContent = 'Temperature: ' + data.temperature_c.toFixed(1) + ' °C';
        humidityStatus.textContent = 'Humidity: ' + (data.humidity !== null ? data.humidity.toFixed(1) + ' %' : 'N/A');
    }

    function fetchLedStatus() {
        fetch('/api/led/status')
            .then(response => response.json())
            .then(updateLedStatus)
            .catch(() => {
                ledStatus.textContent = 'Unable to fetch LED status.';
            });
    }

    function fetchTemperature() {
        fetch('/api/temperature')
            .then(response => response.json())
            .then(updateTemperatureStatus)
            .catch(() => {
                temperatureStatus.textContent = 'Unable to fetch temperature.';
                humidityStatus.textContent = '';
            });
    }

    function sendLedCommand(endpoint) {
        fetch(endpoint, { method: 'POST' })
            .then(response => response.json())
            .then(updateLedStatus)
            .catch(() => {
                ledStatus.textContent = 'Unable to update LED state.';
            });
    }

    document.getElementById('led-on').addEventListener('click', function() {
        sendLedCommand('/api/led/on');
    });

    document.getElementById('led-off').addEventListener('click', function() {
        sendLedCommand('/api/led/off');
    });

    document.getElementById('led-toggle').addEventListener('click', function() {
        sendLedCommand('/api/led/toggle');
    });

    fetchLedStatus();
    fetchTemperature();
    setInterval(fetchTemperature, 10000);
});
