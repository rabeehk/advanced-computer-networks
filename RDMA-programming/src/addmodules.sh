#!/bin/bash

file_exist()
{
    if [ -z "${1}" ]; then
        echo "ERROR: no filename given"
        exit 1
    fi

    if [ ! -f "${1}" ]; then
        echo "ERROR: file ${1} missing"
        # showing help message
        if [ ! -z "${2}" ]; then
            echo "  ${2}"
        fi
        exit 1
    fi
}

dir_exist()
{
    if [ -z "${1}" ]; then
        echo "ERROR: no dirname given"
        exit 1
    fi

    if [ ! -d "${1}" ]; then
        echo "ERROR: dir ${1} missing"
        # showing help message
        if [ ! -z "${2}" ]; then
            echo "  ${2}"
        fi
        exit 1
    fi

}


# making sure the compiled kernel module for soft-iWARP exists
locK="/lib/modules/`uname -r`/extra/siw.ko"
if [ ! -f "${locK}" ]; then
    echo "ERROR: siw.ko does not exist at expected location ${locK}"
    echo "  Make sure that you have compiled and installed the kernel part from 'rmda_assignment_handout/siw/kernel' "
    exit 1
fi

locI="/usr/local/etc/libibverbs.d"
if [ ! -d "${locI}"  ]; then
    echo "ERROR:  Userspace driver for softiWARP is not compiled [${locI}]"
    echo "  Make sure that you have compiled and installed the userlib part from 'rmda_assignment_handout/siw/userlib' "
    exit 1
fi

locU="/etc/libibverbs.d/siw.driver"
if [ ! -f "${locU}"  ]; then
    echo "ERROR:  Userspace driver for softiWARP is not copied at proper location [${locU}]"
    echo "  Make sure that you have copied it from  ${locI} to ${locU}"
    echo "  Following command should do the trick"
    echo "sudo ln -s /usr/local/etc/libibverbs.d /etc/libibverbs.d"
    exit 1
fi

udevf="/etc/udev/rules.d/90-ib.rules"
if [ ! -f "${udevf}"  ]; then
    echo "ERROR:  udev rules file is missing [${udevf}]"
    echo "  Make sure that you have copied it from  rmda_assignment_handout/90-ib.rules to ${udevf}"
    echo "  Following command should do the trick"
    echo "sudo cp rmda_assignment_handout/90-ib.rules ${udevf}"
    exit 1
fi

set -x
set -e

echo "Removing existing sort-iWARP modules"
sudo rmmod siw.ko || true

echo "Inserting modules needed to support sort-iWARP"
sudo modprobe  rdma_cm
sudo modprobe ib_uverbs
sudo modprobe rdma_ucm
sudo insmod  /lib/modules/`uname -r`/extra/siw.ko
sudo lsmod

echo "Making sure that kernel modules are present"
sudo lsmod | grep "ib" || echo "ERROR: ib related kernel modules not found"
sudo lsmod | grep "siw" || echo "ERROR: siw kernel modules not found"

echo "Making sure that the IB device are present!"
ls /dev/infiniband/* || echo "ERROR: ib devices are not present!"


echo "The kernel part is good, lets check the userspace part now"
ibv_devinfo || echo "ERROR: devices detected in userspace"
ibv_devices

