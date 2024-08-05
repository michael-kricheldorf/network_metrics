This repo was made to log ping latencies, RNode Last Received RSSI's, and USB730L modem AT command responses.

Clone this repository into the `miscellaneous` directory of the gateway, and the assumption is that the gateway has the username `ubuntu`

#### Update and Install Dependencies (or nothing will work!)
1. `sudo apt-get update`
2. `sudo apt-get upgrade`
3. `sudo ln -fs /usr/share/zoneinfo/America/New_York /etc/localtime`
4. `sudo apt-get install tzdata libncurses-dev flex bison openssl libssl-dev dkms libelf-dev libudev-dev libpci-dev libiberty-dev autoconf usb-modeswitch dwarves`

#### Setting up the USB730L Driver
These commands were modified and updated to kernel version 5.15.0 from the instructions found on [Verizon's USB730L Integration Guide](https://scache.vzw.com/dam/support/pdf/verizon-usb730l-integration-guide.pdf)

5. `cd /tmp/`
6. `sudo apt source linux`
7. `cd /tmp/linux-5.15.0/drivers/usb/serial/`
8. open `option.c` in Vim editor `sudo vi option.c`
9. paste `#define NOVATELWIRELESS_PRODUCT_ENTERPRISE_U730L 0x9032` below the line `/* NOVATEL WIRELESS PRODUCTS */`
10. find the line `static const struct usb_device_id option_ids[ ]` by typing `/` to go into `search mode` and typing that statement. Press `ENTER` when its found
11. insert `{USB_DEVICE_AND_INTERFACE_INFO(NOVATELWIRELESS_VENDOR_ID, NOVATELWIRELESS_PRODUCT_ENTERPRISE_U730L, 0xff, 0x0, 0x0)},` at the top of the file
12. `sudo cp option.c usb-wwan.h /usr/src/linux-headers-5.15.0-107-generic/drivers/usb/serial/`
13. `cd /lib/modules/5.15.0-107-generic/`
14. `sudo ln -fs build /usr/src/linux-headers-5.15.0-107-generic/`
15. `cd /lib/modules/5.15.0-107-generic/build/drivers/usb/serial/`
16. `sudo cp Makefile Makefile-orig`
17. `sudo truncate -s 0 Makefile`
18. `sudo vi Makefile` and then press `i` to enter `insert mode` and type `obj-m += option.o`, press ESC, then save/exit using `:wq`
19. `cd /lib/modules/5.15.0-107-generic/build`
20. [`sudo cp /sys/kernel/btf/vmlinux /usr/lib/modules/5.15.0-107-generic/build`](https://askubuntu.com/questions/1348250/skipping-btf-generation-xxx-due-to-unavailability-of-vmlinux-on-ubuntu-21-04)
21. `sudo make -C /lib/modules/5.15.0-107-generic/build M=/usr/src/linux-headers-5.15.0-107-generic/drivers/usb/serial/`
22. `sudo cp /usr/src/linux-headers-5.15.0-107-generic/drivers/usb/serial/option.ko /lib/modules/5.15.0-107-generic/kernel/drivers/usb/serial/`
23. `sudo depmod -a`

#### Changing the USB730L to Enterprise Mode
Note: this should only need to be done once. You can confirm by running the command `lsusb` and searching for the Novatel Wireless device. You should follow these instructions if it has a vendor:product number of `1410:9030`, if the vendor:product number is `1410:9032`, you can ignore the next steps

1. `sudo rmmod rndis_host`
2. `sudo usb_modeswitch -v 0x1410 -p 0x9030 -u 4`
3. `sudo reboot` <- find other command that doesn't require a whole reboot maybe

#### Locating the USB730L 
4. run `lsusb` and find the display. make sure the product number is `9032` and not `9030`
5. `ip a` and find the modem interface, should be something like `enx0015ff030033`
6. `sudo dhclient enx0015ff030033`
7. `ls -l /dev/ttyUSB*` to locate the modem. it should be something like `/dev/ttyUSB0`
8. If it displays, woohoo! Ready for [[AT Commands]], if not, then scream and pull the fire alarm

### Setting up logging scripts
Note: Make sure that the `ping_config.json` is configured properly

#### Installing `systemd` unit files
While in the `miscellaneous/network_metrics` directory:
1. `crontab -e` and command out the bottom lines for `lora-radio.sh`
2. `sudo cp modem_USB730L.service modem_USB730L.timer ping.service ping.timer rnode.service tncattach.service tncattach.timer /etc/systemd/system/`
3. `sudo systemctl daemon-reload`
4. `sudo systemctl enable ping.timer`
5. `sudo systemctl enable rnode.service`
6. `sudo systemctl enable tncattach.timer`
7. `sudo reboot`