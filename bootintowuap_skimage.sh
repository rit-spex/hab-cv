# clean existing service files
rm /etc/systemd/system/wuap.service
rm /etc/systemd/system/wuap_skimage.service

# enable boot service to start on reboot
cp wuap_skimage.service /etc/systemd/system/wuap_skimage.service
systemctl enable wuap_skimage.service
