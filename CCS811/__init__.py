from Adafruit_bitfield import Adafruit_bitfield
from time import sleep
import math

from .constants import *

class CCS811(object):
	def __init__(self, address=CCS811_ADDRESS, mode=CCS811_DRIVE_MODE_1SEC, i2c=None, **kwargs):
		# Check that mode is valid.
		if mode not in [CCS811_DRIVE_MODE_IDLE, CCS811_DRIVE_MODE_1SEC, CCS811_DRIVE_MODE_10SEC, CCS811_DRIVE_MODE_60SEC, CCS811_DRIVE_MODE_250MS]:
			raise ValueError('Unexpected mode value {0}.  Set mode to one of CCS811_DRIVE_MODE_IDLE, CCS811_DRIVE_MODE_1SEC, CCS811_DRIVE_MODE_10SEC, CCS811_DRIVE_MODE_60SEC or CCS811_DRIVE_MODE_250MS'.format(mode))

		# Create I2C device.
		if i2c is None:
			import Adafruit_GPIO.I2C as I2C
			i2c = I2C
		self._device = i2c.get_i2c_device(address, **kwargs)

		#set up the registers
		self._status = Adafruit_bitfield([('ERROR' , 1), ('unused', 2), ('DATA_READY' , 1), ('APP_VALID', 1), ('unused2' , 2), ('FW_MODE' , 1)])
		
		self._meas_mode = Adafruit_bitfield([('unused', 2), ('INT_THRESH', 1), ('INT_DATARDY', 1), ('DRIVE_MODE', 3)])

		self._error_id = Adafruit_bitfield([('WRITE_REG_INVALID', 1), ('READ_REG_INVALID', 1), ('MEASMODE_INVALID', 1), ('MAX_RESISTANCE', 1), ('HEATER_FAULT', 1), ('HEATER_SUPPLY', 1)])

		self._TVOC = 0
		self._eCO2 = 0
		self.tempOffset = 0

			#check that the HW id is correct
		if(self._device.readU8(CCS811_HW_ID) != CCS811_HW_ID_CODE):
			raise Exception("Device ID returned is not correct! Please check your wiring.")
		
		#try to start the app
		self._device.writeList(CCS811_BOOTLOADER_APP_START, [])
		sleep(.1)
		
		#make sure there are no errors and we have entered application mode
		if(self.checkError()):
			raise Exception("Device returned an Error! Try removing and reapplying power to the device and running the code again.")
		if(not self._status.FW_MODE):
			raise Exception("Device did not enter application mode! If you got here, there may be a problem with the firmware on your sensor.")
		
		self.disableInterrupt()
		
		#default to read every second
		self.setDriveMode(CCS811_DRIVE_MODE_1SEC)


	def setDriveMode(self, mode):

		self._meas_mode.DRIVE_MODE = mode
		self._device.write8(CCS811_MEAS_MODE, self._meas_mode.get())


	def enableInterrupt(self):

		self._meas_mode.INT_DATARDY = 1
		self._device.write8(CCS811_MEAS_MODE, self._meas_mode.get())


	def disableInterrupt(self):

		self._meas_mode.INT_DATARDY = 0
		self._device.write8(CCS811_MEAS_MODE, self._meas_mode.get())


	def available(self):

		self._status.set(self._device.readU8(CCS811_STATUS))
		if(not self._status.DATA_READY):
			return False
		else:
			return True


	def readData(self):

		if(not self.available()):
			return False
		else:
			buf = self._device.readList(CCS811_ALG_RESULT_DATA, 8)

			self._eCO2 = (buf[0] << 8) | (buf[1])
			self._TVOC = (buf[2] << 8) | (buf[3])
			
			if(self._status.ERROR):
				return buf[5]
				
			else:
				return 0
		


	def setEnvironmentalData(self, humidity, temperature):

		''' Humidity is stored as an unsigned 16 bits in 1/512%RH. The
		default value is 50% = 0x64, 0x00. As an example 48.5%
		humidity would be 0x61, 0x00.'''
		
		''' Temperature is stored as an unsigned 16 bits integer in 1/512
		degrees there is an offset: 0 maps to -25C. The default value is
		25C = 0x64, 0x00. As an example 23.5% temperature would be
		0x61, 0x00.
		The internal algorithm uses these values (or default values if
		not set by the application) to compensate for changes in
		relative humidity and ambient temperature.'''

		hum_perc = (int)(humidity *1024/2)
		temp_conv = (int)((temperature +25)*1024/2)

		buf = [((hum_perc >> 8) & 0xFF), (hum_perc & 0xFF),((temp_conv >> 8) & 0xFF), (temp_conv & 0xFF)]

		self._device.writeList(CCS811_ENV_DATA, buf)



	#calculate temperature based on the NTC register
	def calculateTemperature(self):

		buf = self._device.readList(CCS811_NTC, 4)

		vref = (buf[0] << 8) | buf[1]
		vrntc = (buf[2] << 8) | buf[3]
		rntc = (float(vrntc) * float(CCS811_REF_RESISTOR) / float(vref) )

		ntc_temp = math.log(rntc / 10000.0)
		ntc_temp /= 3380.0
		ntc_temp += 1.0 / (25 + 273.15)
		ntc_temp = 1.0 / ntc_temp
		ntc_temp -= 273.15
		return ntc_temp - self.tempOffset


	def setThresholds(self, low_med, med_high, hysteresis):

		buf = [((low_med >> 8) & 0xF), (low_med & 0xF), ((med_high >> 8) & 0xF), (med_high & 0xF), hysteresis ]
		
		self._device.writeList(CCS811_THRESHOLDS, buf)


	def SWReset(self):

		#reset sequence from the datasheet
		seq = [0x11, 0xE5, 0x72, 0x8A]
		self._device.writeList(CCS811_SW_RESET, seq)


	def checkError(self):

		self._status.set(self._device.readU8(CCS811_STATUS))
		return self._status.ERROR

	def getTVOC(self):
		return self._TVOC

	def geteCO2(self):
		return self._eCO2
