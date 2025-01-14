import RPi.GPIO as GPIO
import time

# إعداد GPIO
GPIO.setmode(GPIO.BCM)
IN3 = 17  # دبوس التحكم بالموتور

# إعداد الدبوس كمخرج
GPIO.setup(IN3, GPIO.OUT)

# إعداد PWM على دبوس IN1
pwm = GPIO.PWM(IN3, 100)  # تردد 100 هرتز
pwm.start(0)  # بدء PWM مع دورة عمل 0% (الموتور متوقف)

# ضبط سرعة الموتور إلى 10%
pwm.ChangeDutyCycle(100)  # تغيير دورة العمل إلى 10%
print("الموتور يعمل بسرعة 10%")

try:
    while True:
        # استمر في تشغيل الموتور
        time.sleep(1)  # استمر بالعمل بدون أي تغيير

except KeyboardInterrupt:
    print("تم إيقاف البرنامج بواسطة المستخدم.")

finally:
    print("إيقاف الموتور")
    pwm.ChangeDutyCycle(0)  # إيقاف الموتور
    pwm.stop()  # إيقاف PWM
    GPIO.cleanup()  # تنظيف إعدادات GPIO
