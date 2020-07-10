# Service Commands

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