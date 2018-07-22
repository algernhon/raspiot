#!/usr/bin/env python

# Import python lib
import time

# Import sensors
import BME680 

# Instance sensors
sensor = BME680.BME680(0x77)

# BME680 These oversampling settings can be tweaked to 
sensor.set_humidity_oversample(BME680.OS_2X)
sensor.set_pressure_oversample(BME680.OS_4X)
sensor.set_temperature_oversample(BME680.OS_8X)
sensor.set_filter(BME680.FILTER_SIZE_3)
sensor.set_gas_status(BME680.ENABLE_GAS_MEAS)

print("\n\nInitial reading:")
for name in dir(sensor.data):
    value = getattr(sensor.data, name)

    if not name.startswith('_'):
        print("{}: {}".format(name, value))

sensor.set_gas_heater_temperature(320)
sensor.set_gas_heater_duration(150)
sensor.select_gas_heater_profile(0)

print("\n\nPolling:")
try:
    while True:
        if sensor.get_sensor_data():
            output = "{0:.2f} C,{1:.2f} hPa,{2:.2f} %RH".format(sensor.data.temperature, sensor.data.pressure, sensor.data.humidity)

            if sensor.data.heat_stable:
                print("{0},{1} Ohms".format(output, sensor.data.gas_resistance))

            else:
                print(output)

        time.sleep(3)

except KeyboardInterrupt:
    pass