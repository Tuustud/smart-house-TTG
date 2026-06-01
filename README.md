# Smart House School Project

This is a simplified school-friendly version of the Smart House project.
All backend logic is contained in a single `src/backend/app.py` file, and Docker support has been removed.

## Project Structure

```
smart-house-TTG
├── src
│   ├── backend
│   │   └── app.py                # Main backend application with all API logic
│   └── scripts
│       └── calibrate_sensors.py  # Optional helper script
├── requirements.txt              # Python dependencies for the project
├── .env.example                  # Template for environment variables
├── .gitignore                    # Files and directories to ignore in Git
└── README.md                     # Project documentation
```

## Getting Started

1. **Set Up Environment**: 
   Copy `.env.example` to `.env` and update values as needed.

2. **Install Dependencies**: 
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**: 
   ```bash
   python src/backend/app.py
   ```

4. **Use the API**: 
   - `GET /api/sensors`
   - `GET /api/sensors/<sensor_id>`
   - `POST /api/sensors`
   - `DELETE /api/sensors/<sensor_id>`

## Notes

- This version is designed for learning and demonstration.
- Sensor data is stored in-memory and resets each time the app restarts.
