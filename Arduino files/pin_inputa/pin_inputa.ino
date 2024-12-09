#include <MHZ19.h>
#include <DHT11.h>

#define co2pwmPin 13 // GPIO13 for PWM input

//MHZ19 input: 
MHZ19 co2Sensor; // Create an instance of the MH-Z19 class

// DHT11 input: 

// - For ESP32: Connect the sensor to pin GPIO2 or P2.
// - For ESP8266: Connect the sensor to GPIO2 or D4.
DHT11 dht11(2);

int co2Ppm = 0;
float temperature = 0.0;
int humidity = 0;

int getCO2() {
  return co2Ppm;
}
float getTemp(){
  return temperature;
}
int getHumidity(){
  return humidity;
}

void setup() {
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

void loop() {
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
  delay(5000); // Wait 5 seconds before the next reading
}
