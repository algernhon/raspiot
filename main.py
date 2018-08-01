#!/usr/bin/env python

# Import python lib
import time
import sys
from influxdb import InfluxDBClient

# Arg control
if len(sys.argv) != 6:
    print("Expected: python main.py <db addr> <db port> <user> <user pswd> <database>")
    sys.exit(0)

# Import sensors
import BME680
import CCS811
import TSL2561

# Main config
MAIN_LOOP_DELAY = 5 # second

# InfluxDB config
client = InfluxDBClient('localhost', 8086, 'root', 'root', 'example')

# Instance sensors
sBME680 = BME680.BME680(0x77, -2)
sCCS811 = CCS811.CCS811(0x5A, 0x01)
sTSL2561 = TSL2561.TSL2561(0x39)

#BME680 config 
sBME680.set_gas_heater_temperature(320)
sBME680.set_gas_heater_duration(150)
sBME680.select_gas_heater_profile(0)

# Main loop
try:
    while True:
        # BME680 loop
        try:
            if sBME680.get_sensor_data():
                output = "{0:.2f}C, {1:.2f}hPa, {2:.2f}%RH".format(sBME680.data.temperature, sBME680.data.pressure, sBME680.data.humidity)

                if sBME680.data.heat_stable:
                    print("{0}, {1}Ohms".format(output, sBME680.data.gas_resistance))

                else:
                    print(output)
        except:
            pass

        # CSS811 loop
        try:
            if sCCS811.available():
                if not sCCS811.readData() and sCCS811.geteCO2() > 0:
                    print "CO2: ", sCCS811.geteCO2(), "ppm, TVOC: ", sCCS811.getTVOC()
        except:
            pass

        # TSL2561 loop
        try:
            print sTSL2561.lux(), "Lux"
        except:
            pass

        # Wait 
        time.sleep(MAIN_LOOP_DELAY)

except KeyboardInterrupt:
    pass