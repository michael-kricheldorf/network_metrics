#!/bin/bash

# this script assumes internet connectivity for now
# TODO: add offline installation logic

log_dir=/var/log/network_metrics
dt=$(date '+%d-%m-%Y_%H%M%S');

# TODO: ------ ARGUMENTS -------
# take -p as argument to install ping
# take -r as argument to install rnode / reinstall tncattach
# take -m as argument to install modem_USB730L software

# ------ ALL ------
sed -i '/deb-src http://us.archive.ubuntu.com/ubuntu jammy main restricted/s/^#//g' /etc/apt/sources.list > /dev/null 2>&1
sudo apt-get update -y
sudo ln -fs /usr/share/zoneinfo/America/New_York /etc/localtime
sudo apt-get install tzdata libncurses-dev flex bison openssl libssl-dev dkms libelf-dev libudev-dev libpci-dev libiberty-dev autoconf usb-modeswitch dwarves ntp -y
sudo service ntp stop
sudo ntpd -gq
sudo service ntp start

# create a network metrics folder if it doesn't exist and create the log databases
if [[ ! -e "$log_dir" ]]; then
    sudo mkdir $log_dir
    sudo mkdir $log_dir/old
else # copy over all of the old log files if they exist to the /old/ subdir
    sudo mv $log_dir/ping_log.db "$log_dir/old/ping_log_$dt.db" > /dev/null 2>&1
    sudo mv $log_dir/modem_log.db "$log_dir/old/modem_log_$dt.db" > /dev/null 2>&1
    sudo mv $log_dir/rnode_log.db "$log_dir/old/rnode_log_$dt.db" > /dev/null 2>&1
    sudo mv $log_dir/throughput_log.db "$log_dir/old/throughput_log_$dt.db"  > /dev/null 2>&1
fi

sudo touch $log_dir/ping_log.db
sudo touch $log_dir/modem_log.db
sudo touch $log_dir/rnode_log.db
sudo touch $log_dir/throughput_log.db

# move any old log files from main git repo dir into the old/ subdir
for file in ./*/*.db; do
    strpd_path=${file##*/}
    new_name=${strpd_path%%.db}_$dt.db
    mv "$file" $log_dir/old/
    mv "$log_dir/old/$strpd_path" $log_dir/old/"$new_name"
done

sudo find /var/log/network_metrics/old/* -size 0 -delete

# remove the old repository and git clone the updated one
sudo rm -rf /home/ubuntu/miscellaneous/network_metrics
git clone https://github.com/michael-kricheldorf/network_metrics.git /home/ubuntu/miscellaneous/network_metrics
cd /home/ubuntu/miscellaneous/network_metrics

# ------ PING SETUP ------
sudo cp ./ping/ping_configs/ping_config_$(hostname).json ./ping/ping_config.json 

sudo cp ./ping/ping.service /etc/systemd/system/ping.service
sudo systemctl daemon-reload
sudo systemctl enable ping.service
sudo systemctl start ping.service

# # ------ MODEM SETUP ------
sudo cp ./modem_USB730L/modem_USB730L.service /etc/systemd/system/modem_USB730L.service
sudo systemctl daemon-reload
sudo systemctl enable modem_USB730L.service
sudo systemctl start modem_USB730L.service

# ------ RNODE SETUP ------
sudo cp ./rnode/rnode.service /etc/systemd/system/rnode.service
sudo systemctl daemon-reload
sudo systemctl enable rnode.service
sudo systemctl start rnode.service

# ------ THROUGHPUT SETUP ------ 
sudo cp ./throughput/throughput.service /etc/systemd/system/throughput.service
sudo systemctl daemon-reload
sudo systemctl enable throughput.service
sudo systemctl start throughput.service