#!/usr/bin/env python
# -*- coding: UTF-8 -*-

##########
## Fan control for odroid xu4
## when hit hiTmp manage fan speed until hit loTmp then stop.
## steps make fan wants to speed down more than speed up, for silence.
## recommanded governor : conservative
############################
import os, sys, signal, re, time, collections

# settings
hiTmp = 90
loTmp = 50

stepUp = 20
stepDown = 5
minSpd = 22 # in percent

# files location
if os.path.isdir("/sys/devices/odroid_fan.14"):
	fanctl = "/sys/devices/odroid_fan.14"
elif os.path.isdir("/sys/devices/odroid_fan.13"):
	fanctl = "/sys/devices/odroid_fan.13"

fTmp = "/sys/devices/10060000.tmu/temp"
fMode = fanctl+"/fan_mode"
fSpd = fanctl+"/pwm_duty"

class fan():
	def __init__(self):
		self.tmpLst = collections.deque(maxlen=300)

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
		#temp = max(tmps) / 1000
		temp = sum(tmps) / len(tmps) / 1000
		self.tmpLst.append(temp)
		tmpAvg = float(sum(self.tmpLst) / len(self.tmpLst))
		return [temp, tmpAvg]

	def cool(self):
		delta = hiTmp - loTmp + 20
		tmps = self.getTmp()
		temp = tmps[0]
		tmpAvg = tmps[1]
		time.sleep(1)
		while tmpAvg > loTmp:
			tmps = self.getTmp()
			temp = tmps[0]
			tmpAvg = tmps[1]
			diff = tmpAvg - loTmp
			percent = int(float(diff) / float(delta) * 100)
			if temp >= hiTmp:
				self.setSpd(100)
			else:
				self.setSpd(percent)
			time.sleep(1)

	def setSpd(self, percent=0):
		if percent > 100:
			percent = 100
		pwm = int(float(percent) * 255 / 100)
		if pwm < 58 and pwm > 1:
			pwm = 58
		if pwm < 1: pwm = 1
		with open(fSpd, "r") as f:
			curPwm = int(f.read())
		if not pwm == curPwm:
			with open(fSpd, "w") as f:
				f.write(str(pwm))

class GracefulKiller:
	kill_now = False
	def __init__(self):
		signal.signal(signal.SIGINT, self.exit_gracefully)
		signal.signal(signal.SIGTERM, self.exit_gracefully)

	def exit_gracefully(self,signum, frame):
		self.kill_now = True

def main():
	killer = GracefulKiller()
	done = False
	fan.setManual()
	fan.setSpd(0)
	while not done:
		if killer.kill_now:
			fan.setAuto()
			break
		if fan.getTmp()[0] > hiTmp:
			fan.cool()
		time.sleep(1)

if __name__ == "__main__":
	fan = fan()
	try:
		main()
	except Exception as error:
		print('caught this error: ' + repr(error))
		fan.setAuto()
