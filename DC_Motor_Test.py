import RPi.GPIO as GPIO
import time

# Set up the GPIO mode and pins
GPIO.setmode(GPIO.BCM)
IN1 = 17  # GPIO pin for IN1
IN2 = 27  # GPIO pin for IN2
ENA = 22  # GPIO pin for ENA (Enable)

# Set the GPIO pins as outputs
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)

# Set PWM for motor speed control
pwm = GPIO.PWM(ENA, 100)  # PWM on ENA pin with a frequency of 100Hz
pwm.start(0)  # Start PWM with 0% duty cycle (motor off initially)

# Function to rotate the motor in one direction (e.g., forward)
def move_forward():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    pwm.ChangeDutyCycle(0)  # Set motor speed to 75% (adjust as needed)

# Start motor rotation in one direction (forward)
move_forward()

try:
    while True:
        # The motor will continue to rotate in one direction (forward) with smooth speed
        time.sleep(1)  # Adjust time for smooth motion if necessary

except KeyboardInterrupt:
    print("Program stopped by user.")
    pwm.ChangeDutyCycle(0)  # Stop the motor smoothly

finally:
    GPIO.cleanup()  # Clean up GPIO settings
