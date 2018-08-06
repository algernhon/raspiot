# InfluxDB config
database = {
    'host': 'localhost',
    'port': 8086,
    'database': '',
    'measurement': '',
    'user': '',
    'password': ''
}

# Your device's information
device = {
    'id': '',
    'location': '',
    'loop-delay': 10
}

# BME680 config
BME680 = {
    'i2c-address': 0x77,
    'temperature-offset': '',
    'humidity-offset': '',
    'heater-temperature': 320,
    'heater-duration': 150,
    'heater-profile': 0
}

# CCS811 config
CCS811 = {
    'i2c-address': 0x5A,
    'drive-mode': 0x02
}

# TSL2561 config
TSL2561 = {
    'i2c-address': 0x39,
    'integration-time': 0x02,
    'gain': 0x00
}