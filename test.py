import RPi.GPIO as GPIO
import time

# إعداد GPIO
GPIO.setmode(GPIO.BCM)
IN1 = 17  # دبوس التحكم بالموتور

# إعداد الدبوس كمخرج
GPIO.setup(IN1, GPIO.OUT)

# إعداد PWM على دبوس IN1
pwm = GPIO.PWM(IN1, 100)  # تردد 100 هرتز
pwm.start(0)  # بدء PWM مع دورة عمل 0% (الموتور متوقف)

# وظيفة لتشغيل الموتور بسرعة معينة
def set_motor_speed(speed):
    """
    تضبط سرعة الموتور
    :param speed: سرعة الموتور بين 0 و 100
    """
    if 0 <= speed <= 100:
        pwm.ChangeDutyCycle(speed)  # تغيير دورة العمل لتحديد السرعة
        print(f"الموتور يعمل بسرعة {speed}%")
    else:
        print("خطأ: السرعة يجب أن تكون بين 0 و 100.")

try:
    while True:
        # اطلب من المستخدم إدخال السرعة
        user_speed = int(input("أدخل السرعة المطلوبة (0-100): "))
        set_motor_speed(user_speed)  # ضبط السرعة

except KeyboardInterrupt:
    print("تم إيقاف البرنامج بواسطة المستخدم.")

finally:
    print("إيقاف الموتور")
    pwm.ChangeDutyCycle(0)  # إيقاف الموتور
    pwm.stop()  # إيقاف PWM
    GPIO.cleanup()  # تنظيف إعدادات GPIO
