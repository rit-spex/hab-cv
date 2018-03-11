# clean existing service files
rm /etc/systemd/system/wuap.service
rm /etc/systemd/system/wuap_skimage.service

# enable boot service to start on reboot
cp wuap.service /etc/systemd/system/wuap.service
systemctl enable wuap.service
