# clean existing service files
rm /etc/systemd/system/wuap.service
rm /etc/systemd/system/wuap_sk.service

# enable boot service to start on reboot
cp wuap_sk-ir.service /etc/systemd/system/wuap_sk.service
systemctl enable wuap_sk.service
