This repo was made to log ping latencies, RNode Last Received RSSI's, and USB730L modem AT command responses.

Clone this repository into the `miscellaneous` directory of the gateway, and the assumption is that the gateway has the username `ubuntu`

#### Update and Install Dependencies (or nothing will work!)
 - `sudo vi /etc/apt/sources.list` and then uncomment the first line starting with deb-src
 - `sudo apt-get update`
 - `sudo apt-get upgrade`
 - `sudo reboot`
 - `sudo ln -fs /usr/share/zoneinfo/America/New_York /etc/localtime`
 - `sudo apt-get install tzdata libncurses-dev flex bison openssl libssl-dev dkms libelf-dev libudev-dev libpci-dev libiberty-dev autoconf usb-modeswitch dwarves`

#### Setting up the USB730L Driver
These commands were modified and updated to kernel version 5.15.0 from the instructions found on [Verizon's USB730L Integration Guide](https://scache.vzw.com/dam/support/pdf/verizon-usb730l-integration-guide.pdf)

 - run `uname -r`, if the kernel version is something like `5.15.0...`, run `cd miscellaneous/network_metrics/modem_USB730L/` and skip to the step starting with `sudo cp option.c`
 - `cd /tmp/`
 - `sudo apt source linux`
 - `cd /tmp/linux-5.15.0/drivers/usb/serial/`
 - open `option.c` in Vim editor `sudo vi option.c`
 - paste `#define NOVATELWIRELESS_PRODUCT_ENTERPRISE_U730L 0x9032` below the line `/* NOVATEL WIRELESS PRODUCTS */`
 - find the line `static const struct usb_device_id option_ids[ ]` by typing `/` to go into `search mode` and typing that statement. Press `ENTER` when its found
 - insert `{USB_DEVICE_AND_INTERFACE_INFO(NOVATELWIRELESS_VENDOR_ID, NOVATELWIRELESS_PRODUCT_ENTERPRISE_U730L, 0xff, 0x0, 0x0)},` at the top of the struct
 - `sudo cp option.c usb-wwan.h /usr/src/linux-headers-$(uname -r)/drivers/usb/serial/`
 #- `cd `
 - `sudo ln -fs /lib/modules/$(uname -r)/build /usr/src/linux-headers-$(uname -r)/`
 - `cd /lib/modules/$(uname -r)/build/drivers/usb/serial/`
 - `sudo cp Makefile Makefile-orig`
 - `sudo truncate -s 0 Makefile`
 - `echo "obj-m += option.o" | sudo tee Makefile`
 - `cd /lib/modules/$(uname -r)/build`
 - [`sudo cp /sys/kernel/btf/vmlinux /usr/lib/modules/$(uname -r)/build`](https://askubuntu.com/questions/1348250/skipping-btf-generation-xxx-due-to-unavailability-of-vmlinux-on-ubuntu-21-04)
 - `sudo make -C /lib/modules/$(uname -r)/build M=/usr/src/linux-headers-$(uname -r)/drivers/usb/serial/`
 - `sudo cp /usr/src/linux-headers-$(uname -r)/drivers/usb/serial/option.ko /lib/modules/$(uname -r)/kernel/drivers/usb/serial/`
 - `sudo depmod -a`

#### Changing the USB730L to Enterprise Mode
 - `sudo rmmod rndis_host`, device may freeze for a few minutes or lose connection, be patient
You can confirm by running the command `lsusb` and searching for the Novatel Wireless device. You should follow these instructions if it has a vendor:product number of `1410:9030`:
 - `sudo usb_modeswitch -v 0x1410 -p 0x9030 -u 4`

If the vendor:product number is `1410:9032`, call the following command:
 - `sudo usb_modeswitch -v 0x1410 -p 0x9032 -u 4`

Then reboot the device to ensure the changes have been made.
 - `sudo reboot` <- find other command that doesn't require a whole reboot maybe

#### Locating the USB730L 
 - run `lsusb` and find the display. make sure the product number is `9032` and not `9030`
 - `ip a` and find the modem interface, should be something like `enx0015ff030033`
 - `sudo dhclient enx0015ff030033`
 - `ls -l /dev/ttyUSB*` to locate the modem. it should be something like `/dev/ttyUSB0`
 - If it displays, woohoo! Ready for [[AT Commands]], if not, then scream and pull the fire alarm

### Setting up logging scripts
 - `sudo rm -rf tncattach`
 - `git clone https://github.com/michael-kricheldorf/tncattach.git`
 - `cd tncattach`
 - `make`
 - `sudo make install`
 - `cd ~/miscellaneous`
 - `git clone https://github.com/michael-kricheldorf/network_metrics.git`


Make sure that the `ping_config.json` is configured properly

#### Installing `systemd` unit files
While in the `miscellaneous/network_metrics` directory:
 - 
 - `pip3 install pythonping`
 - `crontab -e` and command out the bottom lines for `lora-radio.sh`
 - `cp ping/ping_configs/ping_config_$(hostname).json ping/ping_config.json`
 - `sudo cp modem_USB730L/modem_USB730L.service modem_USB730L/modem_USB730L.timer /etc/systemd/system/`
 - `sudo cp ping/ping.service ping/ping.timer /etc/systemd/system/`
 - `sudo cp rnode/rnode.service /etc/systemd/system`
 - `sudo cp tncattach/tncattach.service tncattach/tncattach.timer /etc/systemd/system`
 - `sudo systemctl daemon-reload`
 - `sudo systemctl enable ping.timer`
 - `sudo systemctl enable rnode.service`
 - `sudo systemctl enable tncattach.timer`
 - `sudo reboot`