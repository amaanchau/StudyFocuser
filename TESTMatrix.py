import time
from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.virtual import viewport
from luma.core.legacy import text, show_message, textsize
from luma.core.legacy.font import proportional, CP437_FONT, TINY_FONT, SINCLAIR_FONT, LCD_FONT


serial = spi(port=0, device=0, gpio=noop())
device = max7219(serial, cascaded=4, block_orientation=-90)

print ("Test Led Matrix Max7219")

while True:
	string = input("Input Text:")
	time.sleep(0.5)
	if string:
		msg = str(string)
		w, h = textsize(msg, font=proportional(CP437_FONT))
		if w <= device.width:
			print("Show static text: " + str(string))
			x = round((device.width - w) / 2)
			with canvas(device) as draw:
				text(draw, (x, 0), msg, fill="white", font=proportional(CP437_FONT))
		else:
			print("Show running text: " + str(string))
			show_message(device, msg, fill="white", font=proportional(CP437_FONT),scroll_delay=0.04)

	time.sleep(0.5)

		
device.clear()	



