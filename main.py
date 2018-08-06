#!/usr/bin/env python

# Import python lib
import time
import config
from datetime import datetime
from influxdb import InfluxDBClient

# Config control
if config.device['id'] == '':
    print("Error: No device ID")
    print("You need to give an ID to your device (#001, Alpha, JohnSnow...)")
    sys.exit(0)

# Import sensors
import BME680
import CCS811
import TSL2561

# InfluxDB config
clientDB = InfluxDBClient(config.database['host'], config.database['port'], config.database['user'], config.database['password'], config.database['database'])

# Instance sensors
sBME680 = BME680.BME680(config.BME680['i2c-address'], config.BME680['temperature-offset'], config.BME680['humidity-offset'])
sCCS811 = CCS811.CCS811(config.CCS811['i2c-address'], config.CCS811['drive-mode'])
sTSL2561 = TSL2561.TSL2561(config.TSL2561['i2c-address'], config.TSL2561['integration-time'], config.TSL2561['gain'])

#BME680 config 
sBME680.set_gas_heater_temperature(config.BME680['heater-temperature'])
sBME680.set_gas_heater_duration(config.BME680['heater-duration'])
sBME680.select_gas_heater_profile(config.BME680['heater-profile'])

print("----------------")
print("Launching RaspIOT...")
print("Device: ", config.device['id'])
print("Location: ", config.device['location'])
print("----------------")
print("")
print("Waiting for data...")

# Main loop
try:
    while True:
        # Influx data
        current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        db_message = [
            {
                "measurement": config.database['measurement'],
                "tags": {
                    "device": config.device['id'],
                    "location": config.device['location']
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
            print(db_message) # Feel free to remove this line
        except:
            print("Error connection to database")

        # Wait 
        time.sleep(config.device['loop-delay'])

except KeyboardInterrupt:
    pass