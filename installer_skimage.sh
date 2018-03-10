# installer_skimage.sh will install the necessary packages to run
# Where U At Plants? in scikit-image mode.

# Define packages to install
PACKAGES="python3-dev python3-pip"
PIPMODULES="numpy scikit-image picamera"

# Update firmware
apt-get update
apt-get upgrade -y

# Install packages
apt-get install $PACKAGES -y
pip3 install $PIPMODULES
