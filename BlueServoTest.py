import RPi.GPIO as GPIO
import time

# Set GPIO mode to BCM
GPIO.setmode(GPIO.BCM)

# Set the GPIO pin for the servo
servo_pin = 18  # GPIO pin connected to the servo motor

# Set up the GPIO pin as an output
GPIO.setup(servo_pin, GPIO.OUT)

# Create PWM instance on the servo pin with a 50Hz frequency
pwm = GPIO.PWM(servo_pin, 50)

# Start PWM with a 0% duty cycle (servo won't move initially)
pwm.start(0)

# Function to move the servo to a specific angle
def move_servo(angle):
    # Duty cycle calculation for a given angle (0 to 180 degrees)
    duty = angle / 18 + 2
    GPIO.output(servo_pin, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(1)  # Allow the servo time to reach the angle
    GPIO.output(servo_pin, False)
    pwm.ChangeDutyCycle(0)  # Stop sending PWM signal

# Function to simulate the toy movement
def play_with_toy():
    try:
        while True:
            # Move toy to 30 degrees (start position)
            move_servo(30)
            
            # Move toy to 150 degrees (opposite position)
            move_servo(150)

            # Add a small delay between movements
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("Program stopped by user.")
    finally:
        # Stop PWM and clean up GPIO pins
        pwm.stop()
        GPIO.cleanup()

# Start the toy movement
print("Toy is moving...")
play_with_toy()
