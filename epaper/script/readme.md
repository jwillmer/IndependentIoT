sudo cp epaper.service /etc/systemd/system/epaper.service

sudo systemctl start epaper.service
sudo systemctl stop  epaper.service
sudo systemctl status epaper.service

sudo systemctl enable myscript.service