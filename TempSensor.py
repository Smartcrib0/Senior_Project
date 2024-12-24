import Adafruit_DHT

# Select sensor type: DHT11 or DHT22
sensor = Adafruit_DHT.DHT11  # Change to Adafruit_DHT.DHT22 if using DHT22

# GPIO pin connected to the DATA pin of the sensor
pin = 4  # Use the GPIO pin number you've connected

try:
    while True:
        # Read temperature and humidity from the sensor
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

        # Check if valid readings are received
        if humidity is not None and temperature is not None:
            print(f"Temperature: {temperature:.1f}°C  Humidity: {humidity:.1f}%")
        else:
            print("Failed to retrieve data from the sensor. Retrying...")

except KeyboardInterrupt:
    print("Exiting program.")
