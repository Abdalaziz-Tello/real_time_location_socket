from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
from flasgger import Swagger
import random
import time
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# Swagger configuration
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Real-time Location Socket.IO API",
        "description": "API documentation for real-time location updates using Socket.IO",
        "version": "1.0.0",
        "contact": {
            "email": "your-email@example.com"
        }
    },
    "host": "localhost:5002",
    "basePath": "/",
    "schemes": [
        "http",
        "ws"
    ],
    "consumes": [
        "application/json"
    ],
    "produces": [
        "application/json"
    ],
    "paths": {
        "/": {
            "get": {
                "tags": ["Web Interface"],
                "summary": "Get the web interface",
                "responses": {
                    "200": {
                        "description": "Returns the web interface HTML"
                    }
                }
            }
        }
    },
    "definitions": {
        "Location": {
            "type": "object",
            "properties": {
                "latitude": {
                    "type": "number",
                    "format": "float",
                    "description": "Latitude coordinate"
                },
                "longitude": {
                    "type": "number",
                    "format": "float",
                    "description": "Longitude coordinate"
                },
                "timestamp": {
                    "type": "number",
                    "format": "float",
                    "description": "Unix timestamp"
                }
            }
        }
    }
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

# Simulated location data
def generate_location():
    return {
        'latitude': 37.7749 + random.uniform(-0.01, 0.01),
        'longitude': -122.4194 + random.uniform(-0.01, 0.01),
        'timestamp': time.time()
    }

def send_location_updates():
    while True:
        location = generate_location()
        socketio.emit('location_update', location)
        time.sleep(1)  # Send update every second

@app.route('/')
def index():
    """
    Get the web interface
    ---
    responses:
      200:
        description: Returns the web interface HTML
    """
    return render_template('index.html')

@app.route('/api/location')
def get_current_location():
    """
    Get the current location
    ---
    responses:
      200:
        description: Returns the current location
        schema:
          $ref: '#/definitions/Location'
    """
    return jsonify(generate_location())

@socketio.on('connect')
def handle_connect():
    """
    Handle client connection
    ---
    responses:
      200:
        description: Client connected successfully
    """
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    """
    Handle client disconnection
    ---
    responses:
      200:
        description: Client disconnected successfully
    """
    print('Client disconnected')

if __name__ == '__main__':
    # Start the location update thread
    location_thread = threading.Thread(target=send_location_updates)
    location_thread.daemon = True
    location_thread.start()
    
    # Run the Socket.IO server
    socketio.run(app, debug=True, host='0.0.0.0', port=5002) 