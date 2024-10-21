#!/bin/bash

sudo cp /home/ubuntu/miscellaneous/network_metrics/modem_USB730L/option.c /home/ubuntu/miscellaneous/network_metrics/modem_USB730L/usb-wwan.h /usr/src/linux-headers-$(uname -r)/drivers/usb/serial/
sudo ln -fs /lib/modules/$(uname -r)/build /usr/src/linux-headers-$(uname -r)/
cd /lib/modules/$(uname -r)/build/drivers/usb/serial/

#if Makefile-orig doesn't exist, then copy sudo cp Makefile Makefile-orig
if [[ ! -e "Makefile-orig" ]]; then
    sudo mv Makefile Makefile-orig
else
    sudo rm Makefile Module.symvers modules.order option.ko option.mod* option.o
fi
sudo touch Makefile
echo "obj-m += option.o" | sudo tee Makefile
cd /lib/modules/$(uname -r)/build
# from https://askubuntu.com/questions/1348250/skipping-btf-generation-xxx-due-to-unavailability-of-vmlinux-on-ubuntu-21-04
sudo cp /sys/kernel/btf/vmlinux /usr/lib/modules/$(uname -r)/build
sudo make -C /lib/modules/$(uname -r)/build M=/usr/src/linux-headers-$(uname -r)/drivers/usb/serial/
sudo cp /usr/src/linux-headers-$(uname -r)/drivers/usb/serial/option.ko /lib/modules/$(uname -r)/kernel/drivers/usb/serial/
sudo depmod -a
sudo rmmod rndis_host
sudo usb_modeswitch -v 0x1410 -p 0x$(lsusb | grep '1410:\K903\d' -Po) -u 4
sudo dhclient $(ip a | grep 'enx[^:]*' -Po)