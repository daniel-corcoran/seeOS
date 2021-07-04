** How to set up a new tree camera workstation from fresh ubuntu 20 install **

1. install MDT

https://coral.ai/docs/dev-board/get-started/#install-mdt

sudo apt install python3-pip screen

python3 -m pip install --user mendel-development-tool

echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.bash_profile

source ~/.bash_profile

2. Change keys over serial
https://coral.ai/docs/dev-board/serial-console/#connect-with-linux
sudo usermod -aG plugdev,dialout <username>
* reboot
