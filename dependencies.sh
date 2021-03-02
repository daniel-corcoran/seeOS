# If these packages aren't installed, we need to install them.
sh -c "yes | sudo pip3 install python-periphery https://dl.google.com/coral/python/tflite_runtime-2.1.0.post1-cp37-cp37m-linux_aarch64.whl"
sudo apt-get -y install git build-essential cmake unzip pkg-config libjpeg-dev libpng-dev libtiff-dev libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev libgtk-3-dev libatlas-base-dev gfortran python3-dev python3-opencv
nohup sh -c "yes | sudo pip3 install flask waitress psutil imutils  flask-login PyOpenGL-accelerate dlib face_recognition twilio imgurpython wget tornado terminado" &
