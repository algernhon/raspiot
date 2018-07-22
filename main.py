#!/usr/bin/env python

# Import python lib
import time

# Import sensors
import BME680
import CCS811

# Instance sensors
sBME680 = BME680.BME680(0x77, -2)
sCCS811 = CCS811.CCS811()

# BME680 These oversampling settings can be tweaked to 
sBME680.set_humidity_oversample(BME680.OS_2X)
sBME680.set_pressure_oversample(BME680.OS_4X)
sBME680.set_temperature_oversample(BME680.OS_8X)
sBME680.set_filter(BME680.FILTER_SIZE_3)
sBME680.set_gas_status(BME680.ENABLE_GAS_MEAS)

print("\n\nInitial reading:")
for name in dir(sBME680.data):
    value = getattr(sBME680.data, name)

    if not name.startswith('_'):
        print("{}: {}".format(name, value))

sBME680.set_gas_heater_temperature(320)
sBME680.set_gas_heater_duration(150)
sBME680.select_gas_heater_profile(0)

# Main loop
print("Launching main loop")
try:
    while True:
        print("Loop")
        
        # BME680 loop
        if sBME680.get_sBME680_data():
            output = "{0:.2f} C,{1:.2f} hPa,{2:.2f} %RH".format(sBME680.data.temperature, sBME680.data.pressure, sBME680.data.humidity)

            if sBME680.data.heat_stable:
                print("{0},{1} Ohms".format(output, sBME680.data.gas_resistance))

            else:
                print(output)

        # CSS811 loop
        try:
	        if ccs.available():
	            temp = ccs.calculateTemperature()
	            if not ccs.readData():
	                print "CO2: ", ccs.geteCO2(), "ppm, TVOC: ", ccs.getTVOC(), " temp: ", temp

        except:
            pass

        # Wait 
        time.sleep(3)

except KeyboardInterrupt:
    pass