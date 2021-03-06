#!/usr/bin/env python

# Import python lib
import time
import config
import sys
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

# Import GPIO lib if FAN is enabled
if config.fan['enabled'] == True:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(config.fan['pin'], GPIO.OUT)
    GPIO.setwarnings(False)

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

count = 0

def setFan(mode):
    GPIO.output(config.fan['pin'], mode)

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
            print("Error BME680: Can't read data")

        # CSS811 loop
        try:
            if sCCS811.available():
                # Set temperature and humidity from BME680 in order to compensate changes in CCS811 algo.
                if count == 1 and type(db_message[0]['fields']['temperature']) is float and type(db_message[0]['fields']['humidity']) is float:
                    sCCS811.setEnvironmentalData(db_message[0]['fields']['humidity'], sCCS811.calculateTemperature())
                    print("(!) CSS811 Environmental data updated")
  
                if not sCCS811.readData() and sCCS811.geteCO2() > 0 and sCCS811.geteCO2() < 8192:
                    db_message[0]['fields']['eco2'] = sCCS811.geteCO2()
                    db_message[0]['fields']['tvoc'] = sCCS811.getTVOC()

                    if config.fan['enabled'] == True and db_message[0]['fields']['eco2'] > 800 and GPIO.input(config.fan['pin']) != True:
                        setFan(True)

                    if config.fan['enabled'] == True and db_message[0]['fields']['eco2'] <= 800 and GPIO.input(config.fan['pin']) != False:
                        setFan(False)

        except:
            print("Error CCS811: Can't read data")

        # TSL2561 loop
        try:
            db_message[0]['fields']['lux'] = sTSL2561.lux()
        except:
            print("Error TSL2561: Can't read data")

        # Send all data to Database
        try:
            clientDB.write_points(db_message)
            print(db_message) # Feel free to remove this line
        except:
            print("Error connection to database")

        # Wait 
        time.sleep(config.device['loop-delay'])
        count = (count + 1) % 20

except KeyboardInterrupt:
    pass
