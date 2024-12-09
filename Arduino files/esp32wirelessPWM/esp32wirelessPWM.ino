#include <WiFi.h>
#include <HTTPClient.h>
#include <MHZ19.h>
#include <DHT11.h>

#define co2pwmPin 13 // GPIO13 for PWM input

const char* ssid = "WIFI_NAME";
const char* password = "PSSWD";
const char* serverURL = "http://<Your IP here >/esp-data.json";
const char* authToken = "Token"; // Authentication token
//static IP 

// IPAddress local_IP(192, 168, 1, 184);
// // Set your Gateway IP address
// IPAddress gateway(192, 168, 1, 1);

// IPAddress subnet(255, 255, 0, 0);


unsigned long previousMillis = 0;
unsigned long WIFI_interval = 30000; //30 seconds



//MHZ19 input: 
MHZ19 co2Sensor; // Create an instance of the MH-Z19 class

// DHT11 input: 

// - For ESP32: Connect the sensor to pin GPIO2 or P2.
// - For ESP8266: Connect the sensor to GPIO2 or D4.
DHT11 dht11(2);

int co2Ppm = 0;
float temperature = 0.0;
int humidity = 0;

void initWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi ..");
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print('.');
    delay(1000);
  }
  Serial.println(WiFi.localIP());
  Serial.println("Connected to WiFi");
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  // if (!WiFi.config(local_IP, gateway, subnet, primaryDNS, secondaryDNS)) {
  //   Serial.println("STA Failed to configure");
  // }

  initWiFi();

  Serial.begin(9600); // Initialize Serial Monitor
  co2Sensor.begin(Serial); // Initialize MH-Z19 sensor with default Serial port
  Serial.println("Program Start");

  pinMode(co2pwmPin, INPUT);
  delay(100);

  if (co2Sensor.getABC()) {
    Serial.println("ABC Mode is enabled. Disabling...");
    co2Sensor.autoCalibration(false); // Disable Automatic Baseline Correction if not needed
  }

  if (co2Sensor.getTemperature() == -1) {
    Serial.println("Sensor may be preheating...");
    delay(5000); // Wait for sensor to stabilize
  }
}

void sendData() {
  if (WiFi.status() == WL_CONNECTED) { // Ensure WiFi is connected
    HTTPClient http;

    http.begin(serverURL); // Set the server URL
    http.addHeader("Content-Type", "application/json"); // Specify content type
    http.addHeader("Authorization", authToken);
    // Create JSON payload
    String jsonPayload = "{";
    jsonPayload += "\"co2Ppm\":" + String(co2Ppm) + ",";
    jsonPayload += "\"temperature\":" + String(temperature) + ",";
    jsonPayload += "\"humidity\":" + String(humidity);
    jsonPayload += "}";

    // Send HTTP POST request
    int httpResponseCode = http.POST(jsonPayload);

    // Handle the response
    if (httpResponseCode > 0) {
      Serial.print("HTTP Response code: ");
      Serial.println(httpResponseCode);
    } else {
      Serial.print("Error code: ");
      Serial.println(httpResponseCode);
    }

    http.end(); // Free resources
  } else {
    Serial.println("WiFi not connected, skipping sendData()");
  }
}

void loop() {
  // put your main code here, to run repeatedly:
  unsigned long currentMillis = millis();
  // if WiFi is down, try reconnecting
  if ((WiFi.status() != WL_CONNECTED) && (currentMillis - previousMillis >= WIFI_interval)) {
    Serial.print(millis());
    Serial.println("Reconnecting to WiFi...");
    WiFi.disconnect();
    WiFi.reconnect();
    previousMillis = currentMillis;
  }
  co2Ppm = co2Sensor.getCO2(); // Get CO2 reading
  temperature = co2Sensor.getTemperature(); // Get temperature reading

  if (co2Ppm != -1) {
    Serial.print("CO2 (PPM): ");
    Serial.println(co2Ppm);
  } else {
    Serial.println("Error reading CO2 value");
  }

  if (temperature != -1) {
    Serial.print("Temperature: ");
    Serial.println(temperature);
  } else {
    Serial.println("Error reading temperature");
  }

  humidity = dht11.readHumidity();
  if (humidity != DHT11::ERROR_CHECKSUM && humidity != DHT11::ERROR_TIMEOUT) {
        Serial.print("Humidity: ");
        Serial.print(humidity);
        Serial.println(" %");
    } else {
        // Print error message based on the error code.
        Serial.println(DHT11::getErrorString(humidity));
    }
  sendData();

  delay(5000); // Wait 5 seconds before the next reading
}
