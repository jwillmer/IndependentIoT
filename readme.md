# Independent IoT

The scripts are collecting data from IoT sensors and storing, displaying and sending it to a remote monitoring system. A detailed project description can be found at https://jwillmer.de/blog/projects/independent-iot-system-part-1

## Sensors

- WeMos SHT30 Temp & Humidity Sensor
- 4-ch Current/Voltage/Power Monitor HAT

## Output

- CSV file
- 2.9inch E-Ink display 
- Thinger.io

The scripts in the project are used in a Raspberry Pi that only runs on solar power. The scripts will track the system performance, collect sensor data and sends it to a remote monitoring solution.

## Environment Configuration

Copy the `.env.bak` file in the scripts folder and call it `.env`. Set the environment variables before running the scripts.

## ePaper Service

Displays latest sensor data on ePaper. Is triggered by button press. Check that the path in the `epaper.service` is correct!

```
sudo cp epaper.service /etc/systemd/system/epaper.service

sudo systemctl start epaper.service
sudo systemctl status epaper.service
sudo systemctl stop epaper.service

sudo systemctl enable epaper.service
```

## Sensor Collection Service

Collects sensor data and saves it to CSV and thinger.io. Check that the path is correct!

```
crontab -e
*/15 * * * * /usr/bin/python3 -u /home/pi/IndependentPi/scripts/collectData.py
```
