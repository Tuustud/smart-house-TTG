from flask import Flask
from flask_cors import CORS
from api import api_bp

app = Flask(__name__)
CORS(app)

# Load configuration from environment variables or a config file
app.config.from_object('config.Config')

# Register blueprints
app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/')
def home():
    return "Welcome to the Smart House System!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)