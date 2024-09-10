#!/bin/bash

find_by_id(){
    v=${1%:*}; p=${1#*:}  # split vid:pid into 2 vars
    v=${v#${v%%[!0]*}}; p=${p#${p%%[!0]*}}  # strip leading zeros
    grep -il "^PRODUCT=$v/$p" /sys/bus/usb/devices/*:*/uevent |
    sed s,uevent,, |
    xargs -r grep -r '^DEVNAME=' --include uevent
}

# from ChatGPT, vendor ID and product ID were found using 
x=$(find_by_id "0781:55a3" | grep -o 'DEVNAME=[^/]*' | sed 's/DEVNAME=//')

# from https://stackoverflow.com/questions/10586153/how-to-split-a-string-into-an-array-in-bash
readarray -td '' arr < <(awk '{ gsub(/, /,"\0"); print; }' <<<"$x, "); unset 'arr[-1]';
declare -p arr > /dev/null 2>&1;

# (this assumes only one will work)
for i in $arr
do
    if sudo mount -t ext4 /dev/$i /media/usb > /dev/null 2>&1; then
        echo "Found SanDisk USB and mounted. Please do not remove the device."
        sudo mkdir /media/usb/$(hostname) > /dev/null 2>&1

        sudo cp /home/ubuntu/miscellaneous/network_metrics/modem_USB730L/modem_log.db /media/usb/$(hostname)/
        sudo cp /home/ubuntu/miscellaneous/network_metrics/rnode/rnode_log.db /media/usb/$(hostname)/
        sudo cp /home/ubuntu/miscellaneous/network_metrics/ping/ping_log.db /media/usb/$(hostname)/
        sudo cp /home/ubuntu/miscellaneous/network_metrics/throughput/throughput_log.db /media/usb/$(hostname)/

        # modify to unmount all the possible usb devices
        sudo umount /dev/$i
        echo "Databased copied and SanDisk USB unmounted"
    fi
done