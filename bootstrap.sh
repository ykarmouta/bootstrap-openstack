#!/bin/bash

function boot(){(
    NAME=$1
    IP=$2
    echo $IP
    openstack server create \
        --key-name deploy \
        --nic net-id=Ext-Net \
        --nic net-id=public \
	--nic net-id=management \
        --image 'Ubuntu 16.04' \
        --flavor c2-7 \
        --user-data userdata/${NAME/-[0-9]*/} \
        $NAME
)}

boot deployer 192.168.0.10
#boot rabbit
#boot mysql
#boot keystone
#boot nova
#boot glance
#boot neutron
#boot horizon
#boot compute-1
