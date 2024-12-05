# CS578-Final-project-Air-quality-monitor
### <u>Team Members<u>
| Name             | Role                |
|------------------|---------------------|
| Mosawar Jamshady | Web Developer       |
| Angel Guzman     | Lead Developer      |
| Johnny Rosas     | Project Manager     |
| Hengcheng Zhang  | Product Tester      |

## Overview:
The **Air Quality Monitoring System** is designed to ensure a healthy and comfortable learning environment by continuously monitoring critical air quality parameters such as **carbon dioxide (CO2) concentration**, **temperature**, and **humidity**. The system uses sensors and automated notifications to proactively address air quality issues. When CO2 levels rise above a safe threshold or temperature and humidity reach undesirable levels, the system triggers an alarm to prompt immediate action, such as opening windows or turning on the air conditioner. Additionally, it sends real-time alerts via SMS, enabling prompt action and ensuring that the area's conditions remain optimal.

### Objective:
The primary objective of the **Air Quality Monitoring System** is to enhance indoor air quality and maintain optimal environmental conditions in areas. By employing real-time monitoring and alerting mechanisms, the system aims to:

-   Detect unhealthy levels of CO2 concentration, temperature, and humidity.
-   Provide immediate notifications to people in vicinity in order enable prompt action.
-   Reduce the health risks and cognitive impairments associated with poor air quality.
-   Facilitate long-term data logging for trend analysis and proactive facility management.

### Platform:
The **Air Quality Monitoring System** uses a combination of **Raspberry Pi** and **ESP32 microcontroller** to manage data collection, processing, and communication effectively. This setup ensures accurate monitoring and timely alerts for air quality issues.

#### <u>Components</u>

-   **ESP32 Microcontroller**:
    -   Collects data from the sensors (DHT11 and MH-Z19C).
    -   Transmits sensor readings to the Raspberry Pi for processing.
-   **Raspberry Pi**:
    -   Processes data received from the ESP32.
    -   Triggers alarms and sends SMS alerts using a GSM module.
-   **Sensors**:
    -   **DHT11**: Measures temperature and humidity.
    -   **MH-Z19C**: Monitors carbon dioxide levels.
---

## **Installation Instructions**

### **Prerequisites**
1. **Python 3.8+**
2. **Required Python Packages**:
   - Flask
   - Twilio
   - APScheduler  

Install the required packages by running:  
```bash
pip install flask twilio apscheduler