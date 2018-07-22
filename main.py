#!/usr/bin/env python

# Import python lib
import time

# Import sensors
import BME680
import CCS811

# Instance sensors
sBME680 = BME680.BME680(0x77, -2)
sCCS811 = CCS811.CCS811()

# BME680 settings
sBME680.set_humidity_oversample(BME680.OS_2X)
sBME680.set_pressure_oversample(BME680.OS_4X)
sBME680.set_temperature_oversample(BME680.OS_8X)
sBME680.set_filter(BME680.FILTER_SIZE_3)
sBME680.set_gas_status(BME680.ENABLE_GAS_MEAS)
sBME680.set_gas_heater_temperature(320)
sBME680.set_gas_heater_duration(150)
sBME680.select_gas_heater_profile(0)

# Main loop
try:
    while True:
        # BME680 loop
        try:
            if sBME680.get_sBME680_data():
                output = "{0:.2f} C,{1:.2f} hPa,{2:.2f} %RH".format(sBME680.data.temperature, sBME680.data.pressure, sBME680.data.humidity)

                if sBME680.data.heat_stable:
                    print("{0},{1} Ohms".format(output, sBME680.data.gas_resistance))

                else:
                    print(output)
        
        except:
            pass

        # CSS811 loop
        try:
            if ccs.data_ready:
                print("CO2: ", ccs.eco2, " TVOC: ", ccs.tvoc)

        except:
            pass

        # Wait 
        time.sleep(3)

except KeyboardInterrupt:
    pass