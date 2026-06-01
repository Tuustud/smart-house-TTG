// This file contains the JavaScript code for the frontend application, handling client-side interactions and API calls.

document.addEventListener('DOMContentLoaded', function() {
    const apiUrl = '/api'; // Base URL for API calls

    // Function to fetch sensor data
    function fetchSensorData() {
        fetch(`${apiUrl}/sensors`)
            .then(response => response.json())
            .then(data => {
                // Update the UI with sensor data
                updateSensorUI(data);
            })
            .catch(error => console.error('Error fetching sensor data:', error));
    }

    // Function to update the UI with sensor data
    function updateSensorUI(data) {
        const sensorContainer = document.getElementById('sensor-data');
        sensorContainer.innerHTML = ''; // Clear previous data

        data.forEach(sensor => {
            const sensorElement = document.createElement('div');
            sensorElement.className = 'sensor';
            sensorElement.innerHTML = `<strong>${sensor.name}</strong>: ${sensor.value}`;
            sensorContainer.appendChild(sensorElement);
        });
    }

    // Initial fetch of sensor data
    fetchSensorData();

    // Set an interval to refresh sensor data every 10 seconds
    setInterval(fetchSensorData, 10000);
});