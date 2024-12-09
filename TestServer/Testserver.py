from flask import Flask, request, jsonify
from datetime import datetime
import json
import os

app = Flask(__name__)

# Define the secure token
SECRET_TOKEN = "Token"

def get_file_name():
    """Generate the file name with the current date."""
    current_date = datetime.now().strftime("%Y-%m-%d")  # Format: YYYY-MM-DD
    return f"sensor_data_{current_date}.json"

def save_data(file_name, data):
    """Save data to the JSON file."""
    with open(file_name, "w") as file:
        json.dump(data, file, indent=4)

def load_data(file_name):
    """Load existing data from the JSON file."""
    if os.path.exists(file_name):
        try:
            with open(file_name, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            return []  # Return an empty list if the file is invalid
    return []  # Return an empty list if the file doesn't exist

@app.route("/esp-data.json", methods=["POST"])
def receive_data():
    # Check for the Authorization header
    token = request.headers.get("Authorization")
    if token != SECRET_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401

    # Process the incoming data
    data = request.json
    print(data)
    return jsonify({
        "message": "Data received successfully",
        "server_timestamp": server_timestamp
    }), 200

if __name__ == "__main__":
    app.run(host="192.168.137.164", port=5000)
