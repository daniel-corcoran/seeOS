#!/bin/bash -e
# This command runs on boot. It checks for a system update and installs it if one is available.

echo "Checking for system update in sdcard/tree/sys_flash.tar.xz"
# Unpack system update if available.

if [ -a /home/mendel/sdcard/tree/sys_flash.tar.xz ]
  then
    echo "/home/mendel/sdcard/tree/sys_flash.tar.xz"
    #TODO: make some system indication (LED, Buzzer, Web server, ect) that explains system is updating. Independent flask app?
    mv /home/mendel/sdcard/tree/sys_flash.tar.xz /home/mendel/sdcard/sys_flash.tar.xz
    rm -r /home/mendel/sdcard/tree_backup
    mv /home/mendel/sdcard/tree /home/mendel/sdcard/tree_backup
    cd /home/mendel/sdcard
    tar -xvf  /home/mendel/sdcard/sys_flash.tar.xz
    chmod +x /home/mendel/sdcard/tree/dependencies.sh
    sh /home/mendel/sdcard/tree/dependencies.sh
fi

cd /home/mendel/sdcard/tree
# Create aloas fpr debug mode. This is a live verion of the code that can be stopped and monitored
alias debug="sudo pkill -9 python3; cd ~/sdcard/tree/; sudo python3 boot.py"

sudo python3 boot.py &
exit 0