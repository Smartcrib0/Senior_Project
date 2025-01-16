import RPi.GPIO as GPIO
import time

# Set the GPIO mode to BCM
GPIO.setmode(GPIO.BCM)

# Set the GPIO pin connected to the servo motor
servo_pin = 18

# Set up the GPIO pin as an output
GPIO.setup(servo_pin, GPIO.OUT)

# Create a PWM instance on the servo pin with a frequency of 50Hz
pwm = GPIO.PWM(servo_pin, 50)  # Use 50Hz for standard servos

# Start the PWM with a 0% duty cycle (it won't move initially)
pwm.start(0)

# Function to move the servo to a specific angle
def move_servo(angle):
    # Convert angle to duty cycle (calibration may vary for your servo)
    duty = angle / 18 + 2
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)  # Wait for the servo to reach the position

# Function to rock the crib indefinitely
def rock_crib():
    while True:
        # Smoothly move the servo between two angles
        for angle in range(0, 181, 5):  # Forward sweep from 0° to 180°
            move_servo(angle)
            time.sleep(0.02)  # Small delay for smooth movement
        
        for angle in range(180, -1, -5):  # Backward sweep from 180° to 0°
            move_servo(angle)
            time.sleep(0.02)

try:
    print("Rocking the crib...")
    rock_crib()  # Start rocking the crib
except KeyboardInterrupt:
    print("Program stopped by user.")
finally:
    # Stop PWM and clean up GPIO pins when the program ends
    pwm.stop()
    GPIO.cleanup()
