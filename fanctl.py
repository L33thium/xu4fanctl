#!/usr/bin/env python
# -*- coding: UTF-8 -*-

##########
## Fan control for odroid xu4
## when hit hiTmp manage fan speed until hit loTmp then stop.
## steps make fan wants to speed down more than speed up, for silence.
## recommanded governor : conservative
############################
import sys, re, time

# settings
hiTmp = 85
loTmp = 55

stepUp = 20
stepDown = 5
minSpd = 20 # in percent

# files location
fTmp = "/sys/devices/10060000.tmu/temp"
fMode = "/sys/devices/odroid_fan.14/fan_mode"
fSpd = "/sys/devices/odroid_fan.14/pwm_duty"

class fan():	
	def setManual(self):
		with open(fMode, "w") as f:
			f.write("0")	
	def setAuto(self):
		with open(fMode, "w") as f:
			f.write("1")
	
	def getTmp(self):
		with open(fTmp, "r") as f:
			 t = f.read()
		tmps = re.findall("[0-9]{5}", t)
		tmps = map(int, tmps)
		return max(tmps) / 1000
	def setSpd(self, percent=0):
		if percent < minSpd:
			if not percent == 0:
				percent = minSpd
		if percent > 100:
			percent = 100
		pwm = int(float(percent) * 255 / 100)
		if pwm == 0:
			pwm = 1
		with open(fSpd, "w") as f:
			f.write(str(pwm))
	def cool(self):
		delta = hiTmp - loTmp
		temp = self.getTmp()
		diff = temp - loTmp
		lastPercent = None
		while temp > loTmp:
			time.sleep(1)
			temp = self.getTmp()
			diff = temp - loTmp
			percent = int(float(diff) / float(delta) * 100)
			if lastPercent:
				if percent > lastPercent and percent - lastPercent > stepUp:
					lastPercent = percent
					self.setSpd(percent)
				elif percent < lastPercent and lastPercent - percent > stepDown:
					lastPercent = percent
					self.setSpd(percent)
			else:
				lastPercent = percent
				self.setSpd(percent)
		self.setSpd(0)

def main():
	done = False
	fan.setManual()
	fan.setSpd(0)
	while not done:
		if fan.getTmp() > hiTmp:
			fan.cool()
		time.sleep(.5)

if __name__ == "__main__":
	fan = fan()
	try:
		main()
	except:
		fan.setAuto()
