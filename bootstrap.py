
import os
from keystoneauth1 import loading
from keystoneauth1 import session
from keystoneclient.v3 import client as keystone_v3
from cinderclient import client as cinder
from novaclient import client as nova
from glanceclient import client as glance
from neutronclient.v2_0 import client as neutron


def authentification():
    #get keystone auth
    openstack_credentials = {}
    openstack_credentials['username'] = os.environ['OS_USERNAME']
    openstack_credentials['password'] = os.environ['OS_PASSWORD']
    openstack_credentials['project_id'] = os.environ['OS_TENANT_ID']
    openstack_credentials['auth_url'] = os.environ['OS_AUTH_URL']
    loader = loading.get_plugin_loader('password')
    auth = loader.load_from_options(**openstack_credentials)
    sess = session.Session(auth=auth)
    return sess

def createInstance(keystonToken,instanceNAme,regionName,sshKeyName,flavorName,imageName,ip):
    VERSION = "2"
    sess = keystonToken
    instance = {}
    instance['name'] = instanceNAme
    instance['key_name'] = sshKeyName
    #Find Image ID in glance
    glanceConnect = glance.Client(VERSION, session=sess,region_name=regionName)
    allImages = glanceConnect.images.list()
    for t in allImages:
        if t['name'] == imageName:
            imageId = t['id']
    instance['image'] = imageId

    #Find flavor ID in Nova
    novaConnect = nova.Client(VERSION, session=sess,region_name=regionName)
    for t in novaConnect.flavors.list():
        if t.name == flavorName:
            flavorId = t.id
    instance['flavor'] = flavorId

    #addFileUserData
    fileUserData = os.path.join(os.getcwd(),'userdata',instance['name'])
    if os.path.isfile(fileUserData):
        file = open(fileUserData).read()
        instance["userdata"] = file.replace("{IP}", ip)

    neutronConnect = neutron.Client(session=sess,region_name=regionName)
    network = []
    #Ext-Net
    extNetwork = neutronConnect.list_networks(name='Ext-Net')['networks'][0]['id']
    network.append({"net-id": extNetwork, "v4-fixed-ip": ''})
    #Public
    publicNetwork = neutronConnect.list_networks(name='public')['networks'][0]['id']
    network.append({"net-id": publicNetwork, "v4-fixed-ip": ''})
    #Management
    managementNetwork = neutronConnect.list_networks(name='management')['networks'][0]['id']
    network.append({"net-id": managementNetwork, "v4-fixed-ip": ip})

    instance['nics'] = network
    novaConnect.servers.create(**instance)

if __name__ == "__main__":
    regionName = os.environ['OS_REGION_NAME']
    flavorName = "c2-7"
    imageName = "Ubuntu 16.04"
    sshKeyName = "deploy"
    toCreateInstance = [('deployer','192.168.0.10'),
                        ('rabbit','192.168.0.11'),
                        ('mysql','192.168.0.12'),
                        ('keystone','192.168.0.13'),
                        ('nova','192.168.0.14'),
                        ('glance','192.168.0.15'),
                        ('neutron','192.168.0.16'),
                        ('horizon','192.168.0.17'),
                        ('compute-1','192.168.0.18')]

    sess = authentification()
    for instance,ip in toCreateInstance:
        createInstance(sess,instance,regionName,sshKeyName,flavorName,imageName,ip)
