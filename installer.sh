# installer_skimage.sh will install the necessary packages to run
# Where U At Plants? in opencv mode.

# Define packages to install
BUILDPKGS="cmake build-essential pkg-config"
DEPENDENCIES="libgtk2.0-dev libtbb-dev libjasper-dev libjpeg-dev libpng-dev libtiff-dev libavcodec-dev libavutil-dev libavformat-dev libswscale-dev libdc1394-22-dev libv4l-dev libatlas-base-dev libgstreamer1.0-0"
PYTHONPKGS="python-dev python3-dev libopencv-dev"
PIPMODULES="numpy scipy picamera opencv-python"

# Update firmware
apt-get update
apt-get upgrade -y

# Install packages
apt-get install $PYTHONPKGS -y
pip3 install $PIPMODULES

# clean installation
apt autoremove
