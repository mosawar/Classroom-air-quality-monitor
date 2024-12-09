from flask import Flask, request, render_template
from twilio.rest import Client
from apscheduler.schedulers.background import BackgroundScheduler
import json
import os

app = Flask(__name__)

# Define the secure token
SECRET_TOKEN = "Token"

# The server IP
HOST_NAME = '0.0.0.0'
# Twilio configuration #################### DELETE BEFORE MAKING REPO PUBLIC #################
ACCOUNT_SID = ''
AUTH_TOKEN = ''
TWILIO_PHONE_NUMBER = '+'

client = Client(ACCOUNT_SID, AUTH_TOKEN)

# File path for storing registered phone numbers
REGISTERED_PHONE_FILE = 'registered_phone_numbers.txt'

# Function to get CO2 status based on the given index ranges
def get_co2_status(co2_value):
    if co2_value <= 799:
        return "Good"
    elif 800 <= co2_value <= 1099:
        return "Moderate"
    elif 1100 <= co2_value <= 1499:
        return "Poor"
    elif 1500 <= co2_value <= 1999:
        return "Unhealthy"
    elif 2000 <= co2_value <= 2999:
        return "Very Unhealthy"
    elif 3000 <= co2_value <= 4999:
        return "Hazardous"
    else:
        return "Extreme"

# Function to read data from the static 'data.json' file
def read_data_from_json():
    file_path = os.path.join(app.static_folder, 'data.json')
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error reading data.json: {e}")
        return []

# Function to read registered phone numbers from file
def read_registered_phone_numbers():
    if os.path.exists(REGISTERED_PHONE_FILE):
        with open(REGISTERED_PHONE_FILE, 'r') as f:
            phone_numbers = f.read().splitlines()
        return phone_numbers
    return []

# Function to save a new phone number to the file
def save_phone_number(phone_number):
    with open(REGISTERED_PHONE_FILE, 'a') as f:
        f.write(f"{phone_number}\n")

# Function to send SMS with the latest CO2 data to all registered phone numbers
def send_sms_to_users():
    # Read the latest data from the 'data.json' file
    data = read_data_from_json()
    
    if data:
        # Get the most recent entry
        latest_data = data[-1]
        co2_value = latest_data.get('CO2', 0)
        temperature = latest_data.get('temperature', 0)
        humidity = latest_data.get('humidity', 0)
        timestamp = latest_data.get('timestamp', 'N/A') # defaults N/A
        
        # Get CO2 status
        co2_status = get_co2_status(co2_value)
        
        # put together the message
        message_body = (
            f"~Status~\n"
            f"Timestamp: {timestamp}\n"
            f"CO2 Level: {co2_value} PPM.\n"
            f"Temperature: {temperature}°F.\n"
            f"Humidity: {humidity}%.\n"
            f"Air Quality: {co2_status}."
        )
        # Get registered phone numbers from the file
        phone_numbers = read_registered_phone_numbers()

        # Send SMS using Twilio to all registered phone numbers
        for phone_number in phone_numbers:
            try:
                client.messages.create(
                    body=message_body,
                    from_=TWILIO_PHONE_NUMBER,
                    to=phone_number
                )
                print(f"Message sent to {phone_number}")
            except Exception as e:
                print(f"Error sending message to {phone_number}: {e}")
    else:
        print("No data available to send.")

# Setting up APScheduler to send SMS every minute
scheduler = BackgroundScheduler()
scheduler.add_job(func=send_sms_to_users, trigger="interval", minutes=1) # adjust timer
scheduler.start()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/phone-number')
def phone_number():
    return render_template('phone-number.html')

@app.route('/project-info')
def project_info():
    return render_template('project-info.html')

@app.route('/data.json')
def serve_data():
    return app.send_static_file('data.json')
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

@app.route("/data.json", methods=["POST"])
def receive_data():
    # Check for the Authorization header
    token = request.headers.get("Authorization")
    if token != SECRET_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401

    # Process the incoming data
    data = request.json
    if not data:
        return jsonify({"error": "No data received"}), 400

    # Generate server-side timestamp
    server_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    # Extract and validate data from the request
    try:
        co2_ppm = data["co2Ppm"]
        temperature = data["temperature"]
        temperature = int(float(temperature) * 1.8 + 32)  # Convert temperature to Fahrenheit
        humidity = data["humidity"]
    except KeyError as e:
        return jsonify({"error": f"Missing field: {e.args[0]}"}), 400

    # Prepare the data entry
    entry = {
        "timestamp": server_timestamp,
        "CO2": co2_ppm,
        "temperature": temperature,
        "humidity": humidity,
    }

    # Save data to the appropriate file
    file_name = get_file_name()
    existing_data = load_data(file_name)
    existing_data.append(entry)
    save_data(file_name, existing_data)

    # Log received data with timestamp
    print(f"Timestamp: {server_timestamp}")
    print(f"CO2 (PPM): {co2_ppm}")
    print(f"Temperature (F): {temperature}")
    print(f"Humidity: {humidity}")

    # Respond to the client
    return jsonify({
        "message": "Data received successfully",
        "server_timestamp": server_timestamp
    }), 200

@app.route('/register_phone', methods=['POST'])
def register_phone():
    phone_number = request.form['phone']
    
    # Check if the phone number is already registered
    phone_numbers = read_registered_phone_numbers()
    if phone_number not in phone_numbers:
        save_phone_number(phone_number)
        
        try:
            # Send a confirmation SMS to the registered phone number
            client.messages.create(
                body="Thank you for signing up for alerts!",
                from_=TWILIO_PHONE_NUMBER,
                to=phone_number
            )
            return render_template('project-info.html')
        except Exception as e:
            print(f"Error: {e}")
            return "There was an error while registering your number. Please try again later.", 500
    else:
        return render_template('index.html')

if __name__ == '__main__':
    app.run(host=HOST_NAME, port=5000)
