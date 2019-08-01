# raspiot
A python code for making to make an IoT device from a Raspberry

# Install
Install needed dependencies:
```
sudo apt-get update
sudo apt-get install screen git-core python-pip
pip install influxdb Adafruit-bitfield Adafruit-GPIO smbus
```

We have to change the i2c baudrate for the CCS811 sensor, otherwise it won't work:
```
sudo nano /boot/config.txt
Add this lane: dtparam=i2c_baudrate=10000
```

Once everything is done, clone this repo:
```
git clone https://github.com/algernhon/raspiot.git
```

# Config 
In order to run this app smoothly, download this 3 files (opt):
```
wget https://raw.githubusercontent.com/algernhon/raspiot-launcher/master/start.sh
wget https://raw.githubusercontent.com/algernhon/raspiot-launcher/master/update.sh
wget https://raw.githubusercontent.com/algernhon/raspiot-launcher/master/config.py
```

Start.sh: Start the application in a screen window
Update: Stop, download the latest version and relaunch the app
Config: This is the config file you need to change if you use those 3 files. This one will be copied into your Raspio folder every time you update the app.

Give them the permission to be executed:
```
chmod +x start.sh update.sh
```

Add the startup script to crontab:
```
crontab -e
```
Add this line (change the path if different): `@reboot /home/pi/start.sh`

Now config your Raspiot (InfluxDB info & sensors config):
```
nano config.py
```

# Launch
Launch the app for the first time with the update script (your config file is going to be copied to the raspiot app): 
```
./update.sh
```