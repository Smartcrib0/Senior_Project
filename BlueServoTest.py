import RPi.GPIO as GPIO
import time

# Set GPIO mode to BCM
GPIO.setmode(GPIO.BCM)

# Define the GPIO pin for the servo
servo_pin = 18  # You can change this to any other GPIO pin

# Set the GPIO pin as output
GPIO.setup(servo_pin, GPIO.OUT)

# Create PWM instance on the servo pin with a frequency of 50Hz
pwm = GPIO.PWM(servo_pin, 50)

# Start PWM with a 0% duty cycle (servo won't move initially)
pwm.start(0)

# Function to rotate the servo continuously
def rotate_servo(direction='clockwise'):
    """
    direction can be 'clockwise' or 'counterclockwise'
    """
    if direction == 'clockwise':
        # Duty cycle for clockwise rotation (usually between 7 and 12)
        pwm.ChangeDutyCycle(7)  # You can adjust this for speed
    elif direction == 'counterclockwise':
        # Duty cycle for counterclockwise rotation (usually between 3 and 7)
        pwm.ChangeDutyCycle(3)  # You can adjust this for speed

# Function to stop the servo rotation
def stop_servo():
    pwm.ChangeDutyCycle(0)  # Stop the servo from rotating

try:
    # Start rotating clockwise
    print("Servo is rotating clockwise...")
    rotate_servo('clockwise')
    time.sleep(10)  # The servo will rotate clockwise for 10 seconds
    
    # Switch to counterclockwise rotation
    print("Now, the servo is rotating counterclockwise...")
    rotate_servo('counterclockwise')
    time.sleep(10)  # The servo will rotate counterclockwise for 10 seconds

    # Stop the servo
    stop_servo()
    print("Servo has stopped.")
except KeyboardInterrupt:
    print("Program stopped by user.")
finally:
    pwm.stop()  # Stop the PWM signal
    GPIO.cleanup()  # Clean up GPIO settings
