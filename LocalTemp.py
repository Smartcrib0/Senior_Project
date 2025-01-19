import Adafruit_DHT
from flask import Flask, jsonify

# إعداد المستشعر
SENSOR = Adafruit_DHT.DHT11  # نوع المستشعر
PIN = 4  # رقم الـ GPIO المستخدم

# تطبيق Flask
app = Flask(__name__)

@app.route('/sensor', methods=['GET'])
def get_sensor_data():
    # قراءة البيانات من المستشعر
    humidity, temperature = Adafruit_DHT.read_retry(SENSOR, PIN)
    if humidity is not None and temperature is not None:
        return jsonify({
            "temperature": temperature,
            "humidity": humidity
        })
    else:
        return jsonify({"error": "Failed to read from sensor"}), 500
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
