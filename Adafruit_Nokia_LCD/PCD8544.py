# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import time

import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI


LCDWIDTH = 84
LCDHEIGHT = 48
ROWPIXELS = LCDHEIGHT/6
PCD8544_POWERDOWN = 0x04
PCD8544_ENTRYMODE = 0x02
PCD8544_EXTENDEDINSTRUCTION = 0x01
PCD8544_DISPLAYBLANK = 0x0
PCD8544_DISPLAYNORMAL = 0x4
PCD8544_DISPLAYALLON = 0x1
PCD8544_DISPLAYINVERTED = 0x5
PCD8544_FUNCTIONSET = 0x20
PCD8544_DISPLAYCONTROL = 0x08
PCD8544_SETYADDR = 0x40
PCD8544_SETXADDR = 0x80
PCD8544_SETTEMP = 0x04
PCD8544_SETBIAS = 0x10
PCD8544_SETVOP = 0x80


class PCD8544(object):
	"""Nokia 5110/3310 PCD8544-based LCD display."""

	def __init__(self, dc, rst, sclk=None, din=None, cs=None, gpio=None, spi=None):
		self._sclk = sclk
		self._din = din
		self._dc = dc
		self._cs = cs
		self._rst = rst
		self._gpio = gpio
		self._spi = spi
		# Default to detecting platform GPIO.
		if self._gpio is None:
			self._gpio = GPIO.get_platform_gpio()
		if self._rst is not None:
			self._gpio.setup(self._rst, GPIO.OUT)
		# Default to bit bang SPI.
		if self._spi is None:
			self._spi = SPI.BitBang(self._gpio, self._sclk, self._din, None, self._cs)
		# Set pin outputs.
		self._gpio.setup(self._dc, GPIO.OUT)
		# Initialize buffer to Adafruit logo.
		self._buffer = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
						0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
						0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xC0, 0xE0, 0xF0, 0xF8, 0xFC, 0xFC, 0xFE, 0xFF, 0xFC, 0xE0,
						0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
						0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
						0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
						0x00, 0x00, 0x00, 0x00, 0x00, 0xF8, 0xF8, 0xF8, 0xF8, 0xF8, 0xF8, 0xF8, 0xF8, 0xF8, 0xF8, 0xF8,
						0xF8, 0xF0, 0xF0, 0xE0, 0xE0, 0xC0, 0x80, 0xC0, 0xFC, 0xFF, 0xFF, 0xFF, 0xFF, 0x7F, 0x3F, 0x7F,
						0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
						0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
						0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
						0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0F, 0x1F, 0x3F, 0x7F, 0xFF, 0xFF,
						0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xE7, 0xC7, 0xC7, 0x87, 0x8F, 0x9F, 0x9F, 0xFF, 0xFF, 0xFF,
						0xC1, 0xC0, 0xE0, 0xFC, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFC, 0xFC, 0xFC, 0xFC, 0xFE, 0xFE, 0xFE,
						0xFC, 0xFC, 0xF8, 0xF8, 0xF0, 0xE0, 0xC0, 0xC0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
						0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
						0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
						0x00, 0x80, 0xC0, 0xE0, 0xF1, 0xFB, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x7F, 0x1F, 0x0F, 0x0F, 0x87,
						0xE7, 0xFF, 0xFF, 0xFF, 0x1F, 0x1F, 0x3F, 0xF9, 0xF8, 0xF8, 0xF8, 0xF8, 0xF8, 0xF8, 0xFD, 0xFF,
						0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x7F, 0x3F, 0x0F, 0x07, 0x01, 0x00, 0x00, 0x00,
						0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
						0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
						0x00, 0x00, 0x00, 0xF0, 0xFE, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFE,
						0x7E, 0x3F, 0x3F, 0x0F, 0x1F, 0xFF, 0xFF, 0xFF, 0xFC, 0xF0, 0xE0, 0xF1, 0xFF, 0xFF, 0xFF, 0xFF,
						0xFF, 0xFC, 0xF0, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00,
						0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
						0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
						0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x03, 0x01,
						0x01, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x03, 0x0F, 0x1F, 0x3F, 0x7F, 0x7F,
						0xFF, 0xFF, 0xFF, 0xFF, 0x7F, 0x7F, 0x1F, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
						0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
						0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 ]

	def command(self, c):
		"""Send command byte to display."""
		# DC pin low signals command byte.
		self._gpio.set_low(self._dc)
		self._spi.write([c])

	def extended_command(self, c):
		"""Send a command in extended mode"""
		# Set extended command mode
		self.command(PCD8544_FUNCTIONSET | PCD8544_EXTENDEDINSTRUCTION)
		self.command(c)
		# Set normal display mode.
		self.command(PCD8544_FUNCTIONSET)
		self.command(PCD8544_DISPLAYCONTROL | PCD8544_DISPLAYNORMAL)

	def data(self, c):
		"""Send byte of data to display."""
		# DC pin high signals data byte.
		self._gpio.set_high(self._dc)
		self._spi.write([c])

	def begin(self, contrast=40, bias=4):
		"""Initialize display."""
		self.reset()
		# Set LCD bias.
		self.set_bias(bias)
		self.set_contrast(contrast)

	def reset(self):
		"""Reset the display"""
		if self._rst is not None:
			# Toggle RST low to reset.
			self._gpio.set_low(self._rst)
			time.sleep(0.1)
			self._gpio.set_high(self._rst)

	def display(self):
		"""Write display buffer to physical display."""
		# TODO: Consider support for partial updates like Arduino library.
		# Reset to position zero.
		self.command(PCD8544_SETYADDR)
		self.command(PCD8544_SETXADDR)
		# Write the buffer.
		self._gpio.set_high(self._dc)
		self._spi.write(self._buffer)

	def image(self, image):
		"""Set buffer to value of Python Imaging Library image.  The image should
		be in 1 bit mode and have a size of 84x48 pixels."""
		if image.mode != '1':
			raise ValueError('Image must be in mode 1.')
		index = 0
		# Iterate through the 6 y axis rows.
		# Grab all the pixels from the image, faster than getpixel.
		pix = image.load()
		for row in range(6):
			# Iterate through all 83 x axis columns.
			for x in range(84):
				# Set the bits for the column of pixels at the current position.
				bits = 0
				# Don't use range here as it's a bit slow
				for bit in [0, 1, 2, 3, 4, 5, 6, 7]:
					bits = bits << 1
					bits |= 1 if pix[(x, row*ROWPIXELS+7-bit)] == 0 else 0
				# Update buffer byte and increment to next byte.
				self._buffer[index] = bits
				index += 1

	def clear(self):
		"""Clear contents of image buffer."""
		self._buffer = [0] * int(LCDWIDTH * LCDHEIGHT / 8)

	def set_contrast(self, contrast):
		"""Set contrast to specified value (should be 0-127)."""
		contrast = max(0, min(contrast, 0x7f)) # Clamp to values 0-0x7f
		self.extended_command(PCD8544_SETVOP | contrast)

	def set_bias(self, bias):
		"""Set bias"""
		self.extended_command(PCD8544_SETBIAS | bias)
