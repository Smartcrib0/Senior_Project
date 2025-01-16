import RPi.GPIO as GPIO
import time

# Set the GPIO mode to BCM
GPIO.setmode(GPIO.BCM)

# Set the GPIO pin connected to the servo motor
servo_pin = 18

# Set up the GPIO pin as an output
GPIO.setup(servo_pin, GPIO.OUT)

# Create a PWM instance on the servo pin with a frequency of 50Hz
pwm = GPIO.PWM(servo_pin, 50)  # 50Hz for most servos

# Start the PWM with a neutral duty cycle (stopped position)
pwm.start(0)

# Function to set servo speed and direction
def set_servo_rotation(speed):
    """
    Controls the rotation of a continuous rotation servo.
    - Neutral position (stopped): ~7.5% duty cycle
    - Rotate clockwise: Duty cycle < 7.5%
    - Rotate counterclockwise: Duty cycle > 7.5%
    - Speed varies as you move further from 7.5%
    """
    pwm.ChangeDutyCycle(0.075)  # Set the duty cycle
    time.sleep(1)             # Small delay for stability

try:
    print("Rotating servo endlessly...")
    while True:
        set_servo_rotation(6.5)  # Rotate clockwise (adjust as needed for your servo)
        time.sleep(0.001)         # Optional delay to control responsiveness
except KeyboardInterrupt:
    print("Program stopped by user.")
finally:
    # Stop PWM and clean up GPIO pins when the program ends
    pwm.stop()
    GPIO.cleanup()
