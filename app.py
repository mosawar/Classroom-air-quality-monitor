from flask import Flask, request, render_template
from twilio.rest import Client
from apscheduler.schedulers.background import BackgroundScheduler
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER  = os.getenv("TWILIO_PHONE_NUMBER")

client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))

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
    app.run(host='0.0.0.0', port=5000)
