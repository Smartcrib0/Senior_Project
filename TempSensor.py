# import Adafruit_DHT
# import requests
# import time

# # إعدادات المستشعر
# SENSOR_TYPE = Adafruit_DHT.DHT11
# SENSOR_PIN = 4  # GPIO pin connected to the DHT22

# # إعدادات السيرفر
# SERVER_URL = "http://185.37.12.147:5000/temperature"  # تأكد من تغيير الـ IP إذا لزم الأمر

# def read_temperature():
#     """
#     قراءة درجة الحرارة والرطوبة من مستشعر DHT22.
#     """
#     humidity, temperature = Adafruit_DHT.read_retry(SENSOR_TYPE, SENSOR_PIN)
#     if temperature is not None:
#         return temperature
#     else:
#         print("Failed to retrieve data from sensor")
#         return None

# def send_temperature(temperature):
#     """
#     إرسال درجة الحرارة إلى السيرفر باستخدام HTTP POST.
#     """
#     data = {"temperature": temperature}
#     try:
#         response = requests.post(SERVER_URL, json=data)
#         print(f"Temperature sent: {temperature}°C, Response: {response.text}")
#     except Exception as e:
#         print(f"Failed to send temperature: {e}")

# if __name__ == "__main__":
#     while True:
#         temperature = read_temperature()
#         if temperature is not None:
#             send_temperature(temperature)
#         time.sleep(10)  # انتظر 10 ثواني قبل الإرسال التالي

import requests

url = "http://185.37.12.147:5000"
r= requests.get(url)
print(r.json())