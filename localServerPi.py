import requests
import time
import RPi.GPIO as GPIO

# إعداد السيرفر
SERVER_IP = "192.168.x.x"  # استبدل بـ IP السيرفر
SERVER_PORT = 5000
API_ENDPOINT = f"http://{SERVER_IP}:{SERVER_PORT}/get_detection"

# إعداد Raspberry Pi GPIO
GPIO.setmode(GPIO.BCM)
MIC_PIN = 18  # استبدل بالرقم المناسب
GPIO.setup(MIC_PIN, GPIO.OUT)

# تشغيل/إيقاف المايك
def control_microphone(state):
    GPIO.output(MIC_PIN, GPIO.HIGH if state else GPIO.LOW)
    print(f"Microphone {'ON' if state else 'OFF'}")

# مراقبة السيرفر
def monitor_server():
    while True:
        try:
            response = requests.get(API_ENDPOINT)
            data = response.json()

            phone_detected = data.get("phone_detected", False)
            cry_status = data.get("cry_status", "Silence")

            if phone_detected and cry_status == "Crying":
                control_microphone(True)
            else:
                control_microphone(False)

        except Exception as e:
            print(f"Error fetching detection data: {e}")

        time.sleep(2)  # فترة التأخير بين الطلبات

if __name__ == "__main__":
    try:
        monitor_server()
    except KeyboardInterrupt:
        GPIO.cleanup()
