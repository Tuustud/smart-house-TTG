// This file contains the JavaScript code for the frontend application, handling client-side interactions and API calls.

document.addEventListener('DOMContentLoaded', function() {
    const statusElement = document.getElementById('led-status');

    function updateStatus(data) {
        statusElement.textContent = data.on ? 'LED is ON' : 'LED is OFF';
    }

    function fetchStatus() {
        fetch('/api/led/status')
            .then(response => response.json())
            .then(updateStatus)
            .catch(() => {
                statusElement.textContent = 'Unable to fetch LED status.';
            });
    }

    function sendLedCommand(endpoint) {
        fetch(endpoint, { method: 'POST' })
            .then(response => response.json())
            .then(updateStatus)
            .catch(() => {
                statusElement.textContent = 'Unable to update LED state.';
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

    fetchStatus();
});
