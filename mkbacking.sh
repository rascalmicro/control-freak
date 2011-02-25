#!/bin/sh
if [ "${#}" != "1" ]; then
  echo "usage: $0 <backing_file_name>"
  exit 1
fi 

/bin/dd bs=1M count=64 if=/dev/zero of=${1}
if [ "$?" != "0" ]; then
  echo "Failed to create block file $1"
  exit 2
fi

/usr/sbin/parted ${1} mklabel msdos
if [ "$?" != "0" ]; then
  echo "Failed to create partition label on $1"
  exit 3
fi

/usr/sbin/parted ${1} mkpartfs primary fat32 0 64
if [ "$?" != "0" ]; then
  echo "Failed to create partition on $1"
  exit 4
fi

NSTART=`/sbin/fdisk -lu ${1} | /usr/bin/awk '/FAT32/ { print $2*512 }'`
if [ "$?" != "0" ]; then
  echo "Failed to set NSTART"
  exit 5
fi

/sbin/losetup -o ${NSTART} /dev/loop0 ${1}
if [ "$?" != "0" ]; then
  echo "Failed to create loopback for $1"
  exit 6
fi

/usr/sbin/mkdosfs /dev/loop0
if [ "$?" != "0" ]; then
  echo "Failed to make dos fs for file $1"
  exit 7
fi

MTPT=`pwd`/loopback
/bin/mkdir -p ${MTPT}
if [ "$?" != "0" ]; then
  echo "Failed to create mount point ${MTPT}"
  exit 8
fi

/bin/mount -t vfat /dev/loop0 ${MTPT}
if [ "$?" != "0" ]; then
  echo "Failed to mount $1 on ${MTPT}"
  exit 9
fi

echo "Created ${1} and mounted on ${MTPT}"
echo ""
echo "To unmount:"
echo "  umount /dev/loop0"
echo "  losetup -d /dev/loop0"

