# installer_skimage.sh will install the necessary packages to run
# Where U At Plants? in scikit-image mode.

# create a virtual enviornment
VENV="wuap-sk"
pip3 install virtualenv
mkvirtualenv $VENV
workon $VENV

# Define packages to install
PACKAGES="python3-dev python3-pip"
DEPENDENCIES="libgtk2.0-dev libtbb-dev libjasper-dev libjpeg-dev libpng-dev libtiff5-dev libavcodec-dev libavutil-dev libavformat-dev libswscale-dev libdc1394-22-dev libv4l-dev libatlas-base-dev"
PIPMODULES="numpy scipy scikit-image picamera"

# Update firmware
apt-get update
apt-get upgrade -y

# Install packages
apt-get install $PACKAGES $DEPENENCIES -y
pip3 install $PIPMODULES

# clean installation
apt autoremove
