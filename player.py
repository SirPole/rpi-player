from gpiozero import Button, PWMLED, LED
from signal import pause
from subprocess import Popen, run, PIPE
from time import sleep

class Display:
	BACKLIGHT = PWMLED(13, initial_value=1)
	E = LED(6)
	RS = LED(5)
	D4 = LED(12)
	D5 = LED(26)
	D6 = LED(16)
	D7 = LED(20)
	PULSE = 0.002
	WIDTH = 16
	savedText = [None, "", ""]

	def __init__(self):
		self.sendCommand(0x33)
		self.sendCommand(0x32)
		self.sendCommand(0x06)
		
		# self.sendCommand(0x0C) # Screen ON, cursor Off, production
		self.sendCommand(0x0F) # Screen ON, cursor ON, development
		self.clear()
		self.setLine(1)

	def sendCommand(self, command):
		self.RS.off()
		sleep(self.PULSE)
		self.send(command)

	def sendData(self, data):
		self.RS.on()
		sleep(self.PULSE)
		self.send(data)

	def send(self, data):
		self.resetBits() # high bits
		if data & 0x10 == 0x10:
			self.D4.on()
		if data & 0x20 == 0x20:
			self.D5.on()
		if data & 0x40 == 0x40:
			self.D6.on()
		if data & 0x80 == 0x80:
			self.D7.on()
		self.push()

		self.resetBits() # low bits
		if data & 0x01 == 0x01:
			self.D4.on()
		if data & 0x02 == 0x02:
			self.D5.on()
		if data & 0x04 == 0x04:
			self.D6.on()
		if data & 0x08 == 0x08:
			self.D7.on()
		self.push()

	def resetBits(self):
		self.D4.off()
		self.D5.off()
		self.D6.off()
		self.D7.off()

	def push(self):
		sleep(self.PULSE)
		self.E.on()
		sleep(self.PULSE)
		self.E.off()
		sleep(self.PULSE)

	def clear(self):
		self.sendCommand(0x01)

	def setLine(self, line):
		if (line == 2):
			self.sendCommand(0xC0)
		else:
			self.sendCommand(0x80)
	
	def text(self, text, line):
		text = text.center(self.WIDTH, " ")
		if text != self.savedText[line]:
			self.setLine(line)
			for char in text:
				self.sendData(ord(char))
			self.savedText[line] = text

display = Display()
display.text("INDIGO QUARTET", 1)

def next():
	run(["/usr/bin/cmus-remote", "--next"])

def prev():
	run(["/usr/bin/cmus-remote", "--prev"])

def volume(newVolume):
	run(["/usr/bin/cmus-remote", "--volume", str(newVolume)])
	currentVolume = newVolume

def volumeUp():
	volume(currentVolume + 5)

def volumeDown():
	volume(currentVolume - 5)

def getCurrentSong():
	status = run(["/usr/bin/cmus-remote", "-Q"], universal_newlines=True, stdout=PIPE)
	return status.stdout.splitlines()[1][20:-4]

currentVolume = 100

nextButton = Button(17)
nextButton.when_pressed = next

prevButton = Button(27)
prevButton.when_pressed = prev

upButton = Button(3)
upButton.when_pressed = volumeUp

downButton = Button(4)
downButton.when_pressed = volumeDown

run(["/usr/bin/pkill", "-f", "cmus"])
cmus = Popen(["/usr/bin/cmus"], stdout=PIPE, stderr=PIPE, universal_newlines=True)
sleep(5)
volume(currentVolume)
run(["/usr/bin/cmus-remote", "--clear", "/home/pi/music/playlist.pls"])
run(["/usr/bin/cmus-remote", "--play"])

while True:
	display.text(getCurrentSong(), 2)
	sleep(1)
