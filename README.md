# raspiot
A python code for making to make an IoT device from a Raspberry

# Install
**1 -** Install needed dependencies:
```
sudo apt-get update
sudo apt-get install screen git-core python-pip
pip install influxdb Adafruit-bitfield Adafruit-GPIO smbus
```

**2 -** Change the i2c baudrate of your Raspberry for the CCS811 sensor, otherwise it won't work:
```
sudo nano /boot/config.txt
Add this line: dtparam=i2c_baudrate=10000
```

**3 -** Once everything is done, clone this repo:
```
git clone https://github.com/algernhon/raspiot.git
```

# Config 
**1 -** In order to run this app smoothly, download this 3 files (opt):
```
wget https://raw.githubusercontent.com/algernhon/raspiot-launcher/master/start.sh
wget https://raw.githubusercontent.com/algernhon/raspiot-launcher/master/update.sh
wget https://raw.githubusercontent.com/algernhon/raspiot-launcher/master/config.py
```

`Start.sh`: This script starts the application in a screen window.

`Update.sh`: This script stops, downloads the latest version and relaunches the Raspiot app.

`Config.py`: This is the config file you need to modify if you use those 3 files. This one will be copied into your Raspiot folder every time you update the app.

Give them the permission to be executed:
```
chmod +x start.sh update.sh
```

**2 -** Add the startup script to crontab:
```
crontab -e
```
Add this line (change the path if different): `@reboot /home/pi/start.sh`

**3 -** Now config your Raspiot (InfluxDB info & sensors config):
```
nano config.py
```

# Launch
Launch the app for the first time with the update script (your config file is going to be copied to the raspiot app): 
```
./update.sh
```

If you have already launched this app at least once, execute the start script:
```
./start.sh
```