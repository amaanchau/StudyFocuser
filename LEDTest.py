from gpiozero import LED
from time import sleep

blue = LED(5)
red = LED(6)
green = LED(13)

while True:
	red.on()
	sleep(2)
	red.off()
	blue.on()
	sleep(2)
	blue.off()
	green.on()
	sleep(2)
	green.off()




