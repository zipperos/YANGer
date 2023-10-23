from ncclient import manager
from lxml import etree
from tkinter import messagebox
from copy import deepcopy


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

def formatToConfig(file=None, data=None):
    if file == None and data == None:
        print('no input')
    elif file == None:
        old_cfg = data.getroottree()
        oldroot = data
    elif data == None:
        old_cfg = etree.parse(file)
        oldroot = old_cfg.getroot()

    newroot = deepcopy(oldroot)
    newroot.tag = "{urn:ietf:params:xml:ns:netconf:base:1.0}config"

    for element in newroot.getchildren()[0].getchildren():
        newroot.append(deepcopy(element))
    
    newroot.remove(newroot.find('{urn:ietf:params:xml:ns:netconf:base:1.0}data'))

    newroot.attrib.pop('message-id', None)

    newroot.getroottree().write('C:/Projects/new_config_2send.xml', encoding='utf-8')

def send_config(session, data):
    s = session
    dataroot = etree.parse(data).getroot()
    print(type(dataroot))
    print(dataroot)
    with s.locked(target="candidate"):
        s.edit_config(config=dataroot, default_operation="merge", target="candidate")
        s.commit()


