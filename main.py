#!/usr/bin/env python

# Import python lib
import time
import sys
from datetime import datetime
from influxdb import InfluxDBClient

# Arg control
if len(sys.argv) != 6:
    print("Error: Incorrect arguments")
    print("Expected: python main.py <db addr> <db port> <user> <user pswd> <database>")
    sys.exit(0)

# Import sensors
import BME680
import CCS811
import TSL2561

# Main config - You can change this!
DEVICE_ID = "001"                   # this ID should be unique
DEVICE_LOCATION = "living room"     # room location of the device
MAIN_LOOP_DELAY = 5                 # loop delay in second

# InfluxDB config
clientDB = InfluxDBClient(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
DB_MEASUREMENT = "home"

# Instance sensors
sBME680 = BME680.BME680(0x77, -2.5)         # I2C address and temperature offeset
sCCS811 = CCS811.CCS811(0x5A, 0x01)         # I2C address and drive mode
sTSL2561 = TSL2561.TSL2561(0x39)            # I2C address

#BME680 config 
sBME680.set_gas_heater_temperature(320)
sBME680.set_gas_heater_duration(150)
sBME680.select_gas_heater_profile(0)

print("-------------")
print("RaspIOT #", DEVICE_ID)
print("-------------")
print("Collecting and sending data...", DEVICE_ID)

# Main loop
try:
    while True:
        # Influx data
        current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        db_message = [
            {
                "measurement": DB_MEASUREMENT,
                "tags": {
                    "device": DEVICE_ID,
                    "location": DEVICE_LOCATION
                },
                "time": current_time,
                "fields": {}
            }
        ]

        # BME680 loop
        try:
            if sBME680.get_sensor_data():
                db_message[0]['fields']['temperature'] = sBME680.data.temperature
                db_message[0]['fields']['pressure'] = sBME680.data.pressure
                db_message[0]['fields']['humidity'] = sBME680.data.humidity

                if sBME680.data.heat_stable:
                    db_message[0]['fields']['air_quality'] = sBME680.data.gas_resistance

        except:
            pass

        # CSS811 loop
        try:
            if sCCS811.available():
                if not sCCS811.readData() and sCCS811.geteCO2() > 0 and sCCS811.geteCO2() < 8192:
                    db_message[0]['fields']['eco2'] = sCCS811.geteCO2()
                    db_message[0]['fields']['tvoc'] = sCCS811.getTVOC()
        except:
            pass

        # TSL2561 loop
        try:
            db_message[0]['fields']['lux'] = sTSL2561.lux()
        except:
            pass

        # Send all data to Database
        try:
            clientDB.write_points(db_message)
        except:
            print("Error connection to database")

        # Wait 
        time.sleep(MAIN_LOOP_DELAY)

except KeyboardInterrupt:
    pass