import RPi.GPIO as GPIO
import time

# Set GPIO mode to BCM
GPIO.setmode(GPIO.BCM)

# Define the GPIO pin for the servo
servo_pin = 18  # You can change this to your connected GPIO pin

# Set the GPIO pin as output
GPIO.setup(servo_pin, GPIO.OUT)

# Create PWM instance on the servo pin with a frequency of 50Hz
pwm = GPIO.PWM(servo_pin, 50)

# Start PWM with a 0% duty cycle (servo won't move initially)
pwm.start(0)

try:
    # Rotate the servo in one direction continuously
    print("Servo is rotating clockwise...")
    pwm.ChangeDutyCycle(7)  # Adjust the duty cycle for your servo's clockwise rotation

    # Keep rotating indefinitely
    while True:
        time.sleep(1)  # Keeps the program running without interruption

except KeyboardInterrupt:
    print("Program stopped by user.")
finally:
    # Stop the servo and clean up GPIO pins
    pwm.ChangeDutyCycle(0)  # Stop the servo
    pwm.stop()
    GPIO.cleanup()
