import RPi.GPIO as GPIO
import time

# إعداد GPIO
GPIO.setmode(GPIO.BCM)
IN1 = 17  # دبوس للتحكم بالاتجاه الأول
IN2 = 27  # دبوس للتحكم بالاتجاه الثاني

# إعداد الدبابيس كمخارج
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)

# إعداد PWM على دبوس IN1
pwm = GPIO.PWM(IN1, 100)  # تردد 100 هرتز
pwm.start(0)  # بدء PWM مع دورة عمل 0% (الموتور متوقف)

# دالة لتشغيل الموتور للأمام
def move_forward(speed):
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    pwm.ChangeDutyCycle(speed)

# دالة لتشغيل الموتور للخلف
def move_backward(speed):
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    pwm.ChangeDutyCycle(speed)

try:
    while True:
        print("الموتور يتحرك للأمام")
        move_forward(10)  # تشغيل الموتور للأمام بسرعة 50%
        time.sleep(2)  # الانتظار لمدة 5 ثوانٍ

        # print("الموتور يتحرك للخلف")
        # move_backward(10)  # تشغيل الموتور للخلف بسرعة 50%
        # time.sleep(2)  # الانتظار لمدة 5 ثوانٍ

except KeyboardInterrupt:
    print("تم إيقاف البرنامج بواسطة المستخدم.")

finally:
    print("إيقاف الموتور")
    pwm.ChangeDutyCycle(0)  # إيقاف الموتور
    pwm.stop()  # إيقاف PWM
    GPIO.cleanup()  # تنظيف إعدادات GPIO
