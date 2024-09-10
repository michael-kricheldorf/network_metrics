### How to install the uploader

If this is a gateway with little connectivity, i.e. it is connected via
LoRa radio, then use the `/usb` directory instructions, but if it has good connectivity to the internet, use the `github` directory

##### `/usb` instructions
1. `sudo mkdir /media/usb/`
2. `sudo cp ./usb/usb-upload.rule /etc/udev/rules.d/usb-upload.rule`
3. `sudo udevadm control --reload-rules`
4. `sudo cp ./usb/usb-upload.service /etc/systemd/system/` 
5. `sudo systemctl daemon-reload`
