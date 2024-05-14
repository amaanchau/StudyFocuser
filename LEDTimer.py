from gpiozero import RGBLED, LED, Button
import time
import RPi.GPIO as GPIO
from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.legacy import text, show_message, textsize
from luma.core.legacy.font import proportional, CP437_FONT

# Setup RGB LED
blue = LED(5)
red = LED(6)
green = LED(13)

# Set RGB LED to blue initially
blue.on()
red.off()
green.off()

# Setup Ultrasonic Sensor
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO_TRIGGER = 4
GPIO_ECHO = 17
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

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
        minutes = int(input("Input number of minutes: "))
        total_seconds = minutes * 60
        
        # Set RGB LED to green when countdown starts
        blue.off()
        red.off()
        green.on()
        
        with canvas(device) as draw:
            #text(draw, (0, 0), "Study Time!", fill="white", font=proportional(CP437_FONT) scroll_delay=0.04)
            show_message(device, "Study Time!", fill="white", font=proportional(CP437_FONT),scroll_delay=0.04)

        device.clear()

        while total_seconds > 0:
            distance = measureDistance()
            print("Distance: {:.2f} cm".format(distance))
            
            if distance < 7:
                print("Object is less than 7 cm away!")
                # Set LED to green
                blue.off()
                red.off()
                green.on()
            else:
                print("Object is further than 7 cm away!")
                # Set LED to red
                blue.off()
                red.on()
                green.off()

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

        # Break time
        print("Break time!")
        blue.on()
        red.off()
        green.off()

        # Display "Break time" message
        with canvas(device) as draw:
            show_message(device, "Break Time!", fill="white", font=proportional(CP437_FONT),scroll_delay=0.04)
        device.clear()

        # Restart timer with 1/5 of the inputted minutes
        minutes = minutes // 3
        total_seconds = minutes * 60

        while total_seconds >= 0:
            remaining_minutes, remaining_seconds = divmod(total_seconds, 60)
            remaining_time = "{:02d}:{:02d}".format(remaining_minutes, remaining_seconds)

            with canvas(device) as draw:
                text(draw, (0, 0), remaining_time, fill="white", font=proportional(CP437_FONT))

            time.sleep(0.5)
            total_seconds -= 1

except KeyboardInterrupt:
    # User pressed CTRL-C
    # Reset GPIO settings
    GPIO.cleanup()

