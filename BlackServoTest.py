import RPi.GPIO as GPIO
import time

# Set the GPIO mode to BCM
GPIO.setmode(GPIO.BCM)

# Set the GPIO pin connected to the servo motor
servo_pin = 18


# Set up the GPIO pin as an output
GPIO.setup(servo_pin, GPIO.OUT)

# Create a PWM instance on the servo pin with a frequency of 50Hz
pwm = GPIO.PWM(servo_pin, 50)

# Start the PWM with a 0% duty cycle (it won't move initially)
pwm.start(0)

# Function to move the servo to a specific angle
def move_servo(angle):
    # The duty cycle for a given angle
    duty = angle / 18 + 2
    GPIO.output(servo_pin, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)  # Wait for the servo to reach the position
    GPIO.output(servo_pin, False)
    pwm.ChangeDutyCycle(0)

# Function to rock the crib
def rock_crib():
    while True:
        # Move to the left position (e.g., 45 degrees)
        move_servo(45)
        time.sleep(0.1)  # Wait for the rocking to simulate a pause
        
        # Move to the right position (e.g., 135 degrees)
        move_servo(90)
        time.sleep(0.1)  # Wait for the rocking to simulate a pause

        move_servo(0)
        time.sleep(0.1)

try:
    print("Rocking the crib...")
    rock_crib()  # Start rocking the crib
except KeyboardInterrupt:
    print("Program stopped by user.")
finally:
    # Stop PWM and clean up GPIO pins when the program ends
    pwm.stop()
    GPIO.cleanup()
