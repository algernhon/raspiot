#!/usr/bin/env python

# Import python lib
import time

# Import sensors
import BME680
import CCS811
import TLS2561

# Instance sensors
sBME680 = BME680.BME680(0x77, -2)
sCCS811 = CCS811.CCS811()
sTLS2561 = TLS2561.TLS2561()

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

        print sTLS2561.lux(), "Lux"

        # Wait 
        time.sleep(3)

except KeyboardInterrupt:
    pass