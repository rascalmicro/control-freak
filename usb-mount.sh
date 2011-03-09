#!/bin/sh

umount -d /dev/loop0
losetup -d /dev/loop0 
modprobe g_file_storage file=/root/usb_mass_storage_dev_backing.bin

losetup -o 4096 /dev/loop0 /root/usb_mass_storage_dev_backing.bin
