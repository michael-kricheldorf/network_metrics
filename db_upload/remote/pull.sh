#!/bin/bash

ssh_hosts=("10.10.200.7" "10.10.200.11" "10.10.200.6" "10.10.200.5")    # list of ssh hosts to pull data from
timeout_sec=3   # time to wait for ping response

for i in "${ssh_hosts[@]}"
do
    echo $i
    # make a new directory for the host's logs
    sudo mkdir /var/log/network_metrics/remote/$i > /dev/null 2>&1

    if ping $i -c 1 -W $timeout_sec > /dev/null 2>&1; then # ping to test if connection is available
        # ssh-copy-id -i /home/ubuntu/.ssh/id_rsa.pub ubuntu@$i # copy the ssh ID if it is not already copied (this might require manually entering the password
        # sync with maximum compression all of the logs contained within the remote host's log folder
        sudo rsync --compress --compress-level=9 --recursive --verbose --rsh="ssh -i /home/ubuntu/.ssh/id_rsa" ubuntu@$i:/var/log/network_metrics/* /var/log/network_metrics/remote/$i/
    fi
done