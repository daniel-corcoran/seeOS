todo: Convert this into a pre-built system image or script. This method is not sustainable!

<h1>This is a working document. </h1>


<h5>Welcome, grasshopper, to the Tree Camera System. </h5>
<h5>This document will instruct you to flash seeOS to a device. </h5>
<h5>At the time of writing, the latest system build is 0.3.</h5>


<h3>Supplies</h3>
<l>
* Tree Camera device (Preferably, not inside a case, in case you need to access the board. Wait until device is fully functional to put in the case. Trust me!)
* 3A USB type C PSU (Can probably get away with 2A)
* USB type C connector (For data to host PC)
* Ubuntu 20 host PC


<h3>Directions</h3>

If you're using an old coral board, you need to run "fastboot 0" through the boards serial console to run these commands. 

... Flash debian (assuming you have this system image)
```
cd $HOME/Downloads
cd mendel-enterprise-day-13
mdt reboot-bootloader # Is this really necessary?
bash flash.sh
mdt wait-for-device && mdt shell
```


... System hostname
* ```nmtui```
* 'Set system hostname to tree'
* Don't connect it to wi-fi yet, we will wait until all filesystem junk has been handled first.

... Edit system hosts
```
sudo sh -c 'echo "127.0.0.1       localhost
::1             localhost ip6-localhost ip6-loopback
ff02::1         ip6-allnodes
ff02::2         ip6-allrouters
127.0.0.1 tree" > /etc/hosts'
sudo reboot now 
```
... reboot with ```sudo reboot now``` then use ```mdt shell``` to log back in. 

... Add the SSH Keys with 
```
echo 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQChDeAOf7P8+4QA5uoULBl2DwPSkPJwNX0VrYCnqpXf/V/6Av68mGqJhNzmT7eYetmeOUxDBBwK0QGKrcY8gfpO8CnjgGx/R1ThXasSDV5Adz8+3j+VPWVaQBzMarukn+TfEm8g17MrXE+cx1VqJ+8AYMKxEPdPnowhPavGa/z1R3bUPL4yMLCyw50nmsq67kvxiFM8MFlbKBXpmLcpAwIOiLN7cp/g+S1SaIvcKY3kBraWLF3a7IfY1IEanmcbqaio8Y9OskCtZha11L1WbGS/xWd59MKTSOJteEV5zkVFEhy51aKtyoyWVK9/8DCa/vY37e1pta5SkMsB/0o7fbHT7tt/nVZHTlayLpNCSrk/DRnCpJlyUQRs+tB5UZahvoTIYnlQgCJ8WXsKiZGJDny9Lmnb9s3ZYllw0+2IECnzXANCOaq6I0zUmTw+4GMtb3f9wDxsdvOK8hUt/iSCHl580lh0htePdKxiee6VzLoaruQcwulje5+UJIwDinOGAC0/LBDnOb8FU4j/iN3Fjp99BQg9WztQaAqBc4PPRATUZOtmY2ajzCx0hMCKkGCfHdyUYx4qCz8JMT3G4O59pSgl8bSAqbMtsqzeBaeYrETv3QwHwjxmuWiHhwzk8wzTFVsGqrpXWhcwvfshrEX9vJRPfW6Rnl0nkCUD1s4lnw5JQQ== corcordp@mail.uc.edu' >> .ssh/authorized_keys
```

... At this point, reboot the camera (```sudo reboot now```) and make sure your SSH keys work. You should be able to run this without a password. 
```
ssh mendel@tree.local
```

... format the SD card 
```
sudo fdisk /dev/mmcblk1
// create new partition. If this step gives you an error (bc of pre-existing partition), try deleting (d) first, then try again. 
Command (m for help): n
// Use the defaults, if it asks you to remove signature, say No [N]
// make this a primary partition, leave default values for first and last sector
Command (m for help): p
// Write it (by default fdisk will make this a ext4 partition)
Command (m for help): w
```
```sudo fdisk -l``` should show something like this:
```
Disk /dev/mmcblk1: 29.7 GiB, 31914983424 bytes, 62333952 sectors
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: dos
Disk identifier: 0x2aaeb742

Device         Boot Start      End  Sectors  Size Id Type
/dev/mmcblk1p1       2048 62333951 62331904 29.7G 83 Linux
```

Mount the SD Card under /home/mendel/sdcard
```
# This one usually takes a few minutes
y | sudo mkfs.ext4 /dev/mmcblk1p1

mkdir sdcard          
sudo mount /dev/mmcblk1p1 sdcard
sudo chmod 777 sdcard 
mkdir sdcard/tree

# Make the important system files editable. 
sudo chmod 666 /etc/fstab
sudo chmod 666 /etc/sysctl.conf

# Allocate a swap file on the SD Card. We will make the swappiness low to reduce wear.
 
sudo fallocate -l 2G /home/mendel/sdcard/swapfile
sudo chmod 600 /home/mendel/sdcard/swapfile
sudo mkswap /home/mendel/sdcard/swapfile
sudo swapon /home/mendel/sdcard/swapfile

# These commands make changs permanent. 
sudo echo " /dev/mmcblk1p1 /home/mendel/sdcard ext4 defaults 0 1" >> /etc/fstab
sudo echo "/home/mendel/sdcard/swapfile none swap sw 0 0" >> /etc/fstab
sudo echo "vm.swappiness=10" >> /etc/sysctl.conf
```


... Now we edit rc.local to add the bootup script

```
sudo sh -c 'echo "#!/bin/bash -e
chmod +x /home/mendel/sdcard/tree/bootloader.sh
/bin/bash /home/mendel/sdcard/tree/bootloader.sh
exit 0


sudo chmod +x /etc/rc.local

```

debug mode
```
alias debug="sudo pkill -9 python3; cd ~/sdcard/tree/; python3 boot.py"

```



... SCP OS file (from host system.)
```
rsync -avh tree/ mendel@tree.local:/home/mendel/sdcard/tree

```

... connect it to wifi using nmtui. 

```
sudo apt -y update && sudo apt -y upgrade && sudo apt -y dist-upgrade

sh -c "yes | sudo pip3 install python-periphery https://dl.google.com/coral/python/tflite_runtime-2.1.0.post1-cp37-cp37m-linux_aarch64.whl"
sudo apt-get -y install git build-essential cmake unzip pkg-config libjpeg-dev libpng-dev libtiff-dev libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev libgtk-3-dev libatlas-base-dev gfortran python3-dev python3-opencv
sh -c "yes | sudo pip3 install flask waitress psutil imutils  flask-login PyOpenGL-accelerate dlib face_recognition twilio imgurpython wget tornado terminado"


# At this point the tutorial is over and you can assemble the device. 
# TODO: Add assembly directions
# TODO: Include LED and piezo test as part of setup process
# Connect over wi-fi first before running this. We need to start setting up other boards. 
# TODO: LED/Piezo test script? 

```
<h1>Help</h1>
Did something go wrong? If you cannot SSH into the board using MDT shell or SSH, connect using the USB serial port. Log in via this. Then run 

```
mdt reboot-bootloader
this puts the board in fastboot mode, so you can re-flash the operating system
```
To restart the board into fastboot mode. This is effectively a factory reset. 
(I've probably had to do this 10,000 times.)

# TODO: Make bash script? 
# TODO: remove my wi-fi from devices
# TODO: remove my wi-fi from devices
# TODO: make simplestreamer default application
# TODO: make testing script for LED, Piezo, and camera


# These are terminal tools