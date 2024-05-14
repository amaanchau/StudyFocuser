from gpiozero import RGBLED, LED, Button
import time
import RPi.GPIO as GPIO
from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.legacy import text, show_message, textsize
from luma.core.legacy.font import proportional, CP437_FONT
import cv2
import time
from gaze_tracking import GazeTracking


# Setup RGB LED
blue = LED(5)
red = LED(6)
green = LED(13)

# Set RGB LED to blue initially
blue.on()
red.off()
green.off()


GreenButton =  Button(20)
RedButton =  Button(21)

# Setup Ultrasonic Sensor
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO_TRIGGER = 4
GPIO_ECHO = 17
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

gaze = GazeTracking()
webcam = cv2.VideoCapture(0)
# Set desired frame rate (e.g., 10 frames per second)
desired_fps = 5
# Calculate delay time in seconds based on desired frame rate
delay_time = 1 / desired_fps


# Function to measure distance
def measureDistance():
    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)

    while GPIO.input(GPIO_ECHO) == 0:
        pulse_start = time.time()

    while GPIO.input(GPIO_ECHO) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    return distance

serial = spi(port=0, device=0, gpio=noop())
device = max7219(serial, cascaded=4, block_orientation=-90)


try:
    while True:
		
		# Wait for either button to be pressed
        while not GreenButton.is_pressed and not RedButton.is_pressed:
            time.sleep(0.1)
        
        distracted = 0
        
        if GreenButton.is_pressed:
            print("Green button pressed. Starting a 3-minute timer.")
            minutes = 3
            total_seconds = minutes * 60
        elif RedButton.is_pressed:
            print("Red button pressed. Starting a 30-minute timer.")
            minutes = 30
            total_seconds = minutes * 60
        
        # Set RGB LED to green when countdown starts
        blue.on()
        red.off()
        green.off()
        
        with canvas(device) as draw:
            show_message(device, "Study Time!", fill="white", font=proportional(CP437_FONT),scroll_delay=0.04)
        device.clear()
        
        prevIsLR = False
        
        while total_seconds > 0:
            distance = measureDistance()
            print("Distance: {:.2f} cm".format(distance))
            
            # Record start time
            start_time = time.time()
            
            # We get a new frame from the webcam
            _, frame = webcam.read()

            # We send this frame to GazeTracking to analyze it
            gaze.refresh(frame)

            if (distance < 8 and gaze.is_center()):
                print("Phone is less than 8 cm away and gaze is center")
                # Set LED to GREEN
                blue.off()
                red.off()
                green.on()
                prevIsLR = False
            elif gaze.is_blinking():
                print("Blink")
            else:
                if (distance > 8):
                    print("Phone is more than 8 cm away")
                    # Set LED to red
                    blue.off()
                    red.on()
                    green.off()
                    total_seconds += 1
                    distracted += 1
                elif(not prevIsLR):
                    print("Not PrevIsLR")
                    blue.off()
                    red.off()
                    green.on()
                else:
                    print("Looking Left/Right")
                    blue.off()
                    red.on()
                    green.off()
                    total_seconds += 1
                    distracted += 1
                prevIsLR = True
            
            remaining_minutes, remaining_seconds = divmod(total_seconds, 60)
            remaining_time = "{:02d}:{:02d}".format(remaining_minutes, remaining_seconds)

            with canvas(device) as draw:
                text(draw, (0, 0), remaining_time, fill="white", font=proportional(CP437_FONT))

            time.sleep(0.5)
            total_seconds -= 1

        print("Countdown finished!")
        
        device.clear()
        
        # Set RGB LED to blue again for the next round
        blue.on()
        red.off()
        green.off()
        
        
        distracted_minutes = distracted // 60
        distracted -= distracted_minutes * 60
        distracted_time = "Distracted Time: {:02d}:{:02d}".format(distracted_minutes, distracted)
        print(distracted_time)

        # Break time
        print("Break time!")
        blue.on()
        red.off()
        green.off()

        # Display "Break time" message
        with canvas(device) as draw:
            show_message(device, "Break Time!", fill="white", font=proportional(CP437_FONT),scroll_delay=0.04)
        device.clear()

        # Restart timer with 1/3 of the inputted minutes
        minutes = minutes // 3
        total_seconds = minutes * 60

        while total_seconds >= 0:
            remaining_minutes, remaining_seconds = divmod(total_seconds, 60)
            remaining_time = "{:02d}:{:02d}".format(remaining_minutes, remaining_seconds)

            with canvas(device) as draw:
                text(draw, (0, 0), remaining_time, fill="white", font=proportional(CP437_FONT))

            time.sleep(1)
            total_seconds -= 1
            
        #Display the Distracted Time
        with canvas(device) as draw:
            show_message(device, distracted_time, fill="white", font=proportional(CP437_FONT), scroll_delay=0.06)
        device.clear()

except KeyboardInterrupt:
    GPIO.cleanup()

