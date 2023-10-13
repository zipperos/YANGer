from ncclient import manager
from lxml import etree
from tkinter import messagebox


def session_start(hostname, portno, user, pwd):
    try:
        print(str(hostname), str(portno), str(user), str(pwd), sep='\n')
        s = manager.connect(host=hostname, port=portno, username=user, password=pwd, hostkey_verify=False)
    except Exception as e:
        messagebox.showinfo(title='Information', message=e)
        return 0
    else:
        return s
def dummyDataEtree(self):
    my_config_root = etree.Element("{urn:ietf:params:xml:ns:netconf:base:1.0}config")
    interfaces = etree.SubElement(my_config_root, "{urn:ietf:params:xml:ns:yang:ietf-interfaces}interfaces")
    interface = etree.SubElement(interfaces, 'interface')
    interface_name = etree.SubElement(interface, 'name')
    interface_name.text = "PORT_0"

    description = etree.SubElement(interface, 'description')
    description.text = "some random shit"
    bridgeport = etree.SubElement(interface, "{urn:ieee:std:802.1Q:yang:ieee802-dot1q-bridge}bridge-port")
    gateparamtable = etree.SubElement(bridgeport, "{urn:ieee:std:802.1Q:yang:ieee802-dot1q-sched}gate-parameter-table")

    sdutable = etree.SubElement(gateparamtable, 'queue-max-sdu-table')
    trafficClass = etree.SubElement(sdutable, 'traffic-class')
    trafficClass.text = '0'
    sdu = etree.SubElement(sdutable, 'queue-max-sdu')
    sdu.text = "1000"
    
    return my_config_root