import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog as fd
from lxml import etree

from ncclient import manager

from netconfhandler import *
from treeviewWindow import *

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        consts = tk.BooleanVar(False)
        cfgsts = tk.BooleanVar(False)
        session = manager
        cfg_tree = etree.Element('Empty')
        cfgfilepath = tk.StringVar()
        self.sharedData = {
            'connected': consts,
            'session_handler': session,
            'cfg_tree': cfg_tree,
            'cfg_available': cfgsts,
            'cfgfilepath': cfgfilepath
            }
        
        # configure the root window
        self.title('YANGer')
        self.geometry('600x600')
        self.__drawFrames()

        
    def __drawFrames(self): 
        frame1 = ConnectFrame(self)
        frame1.grid(column=0, row=0)
        frame2 = FilesFrame(self)
        frame2.grid(column=0, row=1)

# File handling frame       
class FilesFrame(tk.Frame):
    
    def __init__(self, container):
        super().__init__(container)
        options = {'padx': 5, 'pady': 5}

        
        self.container = container
        self.connected = self.container.sharedData['connected']
        self.cfg_available = self.container.sharedData['cfg_available']
        self.session = self.container.sharedData['session_handler']
        self.cfg_tree = self.container.sharedData['cfg_tree']
        self.cfgfilepath = self.container.sharedData['cfgfilepath']
##        print(type(self.cfg_tree))
##        print(self.connected, type(self.connected))
        self.fileLabel = ttk.Label(self, text='Select file to save config')
        self.fileLabel.grid(column=0, row=0, **options, sticky=tk.W)

        #save filepath
        self.svfilepath = tk.StringVar()
        self.save_filepathEntry = ttk.Entry(self, textvariable=self.svfilepath)
        self.save_filepathEntry.grid(column=1, row=0, **options, sticky=tk.W)
        self.save_filepathEntry.insert(0,'/config.xml')
        self.save_filepathEntry.config(state='disabled')

        self.selectsButton = ttk.Button(self, text='Select')
        self.selectsButton['command'] = self.select_s_clicked
        self.selectsButton.grid(column=2, row=0, **options, sticky=tk.W)
        self.selectsButton.config(state='enabled')
        
        self.saveButton = ttk.Button(self, text='Save')
        self.saveButton['command'] = self.save_clicked
        self.saveButton.grid(column=0, row=1, **options, sticky=tk.W)
        self.saveButton.config(state='disabled')

##        select and Load file
        self.fileLabel = ttk.Label(self, text='Select file to load')
        self.fileLabel.grid(column=0, row=2, **options, sticky=tk.W)
        self.ldfilepath = tk.StringVar()
        self.load_filepathEntry = ttk.Entry(self, textvariable=self.ldfilepath)
        self.load_filepathEntry.grid(column=1, row=2, **options, sticky=tk.W)
        self.load_filepathEntry.insert(0,'C:/Projects/config.xml')
        self.load_filepathEntry.config(state='disabled')

        self.loadtoparseButton = ttk.Button(self, text='Select')
        self.loadtoparseButton['command'] = self.loadtoparse_clicked
        self.loadtoparseButton.grid(column=2, row=2, **options, sticky=tk.W)
        self.loadtoparseButton.config(state='enabled')


        self.loadButton = ttk.Button(self, text='Load')
        self.loadButton['command'] = self.load_clicked
        self.loadButton.grid(column=0, row=3, **options, sticky=tk.W)
        self.loadButton.config(state='enabled')

##        select and Load newcfg
        self.fileLabel = ttk.Label(self, text='Select new config to upload')
        self.fileLabel.grid(column=0, row=4, **options, sticky=tk.W)
        self.load_cfgpathEntry = ttk.Entry(self, textvariable=self.cfgfilepath)
        self.load_cfgpathEntry.grid(column=1, row=4, **options, sticky=tk.W)
        self.load_cfgpathEntry.insert(0,'C:/Projects/new_config_2send.xml')

        self.loadcfgButton = ttk.Button(self, text='Select')
        self.loadcfgButton['command'] = self.loadcfg_clicked
        self.loadcfgButton.grid(column=2, row=4, **options, sticky=tk.W)
        self.loadcfgButton.config(state='enabled')

##        Callbacks
        self.connected.trace_add('write', self.connected_callback)
        self.cfg_available.trace_add('write', self.cfg_callback)
    
    def loadtoparse_clicked(self):
        self.ldfilepath.set(self.select_files())

    def loadcfg_clicked(self):
        self.cfgfilepath.set(self.select_files())


    def load_clicked(self):
        et = etree.parse(self.ldfilepath.get())
        datatopass = et.getroot()
        TVwindow = treeViewWindow(data=datatopass)

    def select_s_clicked(self):
        self.svfilepath.set(self.select_files())


    def save_clicked(self):
        savepath = self.svfilepath.get()
        
        self.cfg_tree = self.container.cfg_tree
        ltree = etree.ElementTree(self.cfg_tree)
        ltree.write(savepath, pretty_print=True)

    def connected_callback(self, *args):
##        self.saveButton.config(state='enabled')
##        self.save_filepathEntry.config(state='enabled')
        pass

    def cfg_callback(self, *args):
        self.saveButton.config(state='enabled')
        self.save_filepathEntry.config(state='enabled')

    def select_files(self):
        filetypes = (
            ('xml files', '*.xml'),
            ('text files', '*.txt'),
            ('All files', '*.*'))
        filenames = fd.askopenfilename(
            title='Open files',
            initialdir='/',
            filetypes=filetypes)
        return filenames

        
# Netconf session frame       
class ConnectFrame(tk.Frame):
    
    def __init__(self, container):
        super().__init__(container)
        self.container = container
        self.connected = self.container.sharedData['connected']
        self.session = self.container.sharedData['session_handler']
        self.cfg_eltree = self.container.sharedData['cfg_tree']
        self.cfg_sts = self.container.sharedData['cfg_available']
        self.cfgfilepath = self.container.sharedData['cfgfilepath']
        options = {'padx': 5, 'pady': 5}
        
        self.hostLabel = ttk.Label(self, text='Host')
        self.hostLabel.grid(column=0, row=0, **options, sticky=tk.W)

        #Host entry
        self.netconfHost = tk.StringVar()
        self.hostEntry = ttk.Entry(self, textvariable=self.netconfHost)
        self.hostEntry.grid(column=1, row=0, **options, sticky=tk.W)
        self.hostEntry.insert(0,'192.168.2.64')

        #Port label and entry

        self.portLabel = ttk.Label(self, text='Port')
        self.portLabel.grid(column=0, row=1, **options, sticky=tk.W)
        self.netconfPort = tk.StringVar()
        self.portEntry = ttk.Entry(self, textvariable=self.netconfPort)
        self.portEntry.grid(column=1, row=1, **options, sticky=tk.W)
        self.portEntry.insert(0,'830')
        

        #User entry
        self.userLabel = ttk.Label(self, text='User')
        self.userLabel.grid(column=0, row=2, **options, sticky=tk.W)
        self.netconfUser = tk.StringVar()
        self.userEntry = ttk.Entry(self, textvariable=self.netconfUser)
        self.userEntry.grid(column=1, row=2, **options, sticky=tk.W)
        self.userEntry.insert(0,'sys-admin')

        #PWD entry
        self.pwdLabel = ttk.Label(self, text='Pwd')
        self.pwdLabel.grid(column=0, row=3, **options, sticky=tk.W)
        self.netconfPWD = tk.StringVar()
        self.pwdEntry = ttk.Entry(self, show='*', textvariable=self.netconfPWD)
        self.pwdEntry.grid(column=1, row=3, **options, sticky=tk.W)
        self.pwdEntry.insert(0,'sys-admin')
       
        # connect button
        self.connectButton = ttk.Button(self, text='Connect')
        self.connectButton['command'] = self.connect_clicked
        self.connectButton.grid(column=2, row=0, **options, sticky=tk.W)

        # capabilities button
        self.capabilitiesButton = ttk.Button(self, text='get capabilities', state='disabled')
        self.capabilitiesButton['command'] = self.capabilites_clicked
        self.capabilitiesButton.grid(column=3, row=0, **options, sticky=tk.W)

        #get_config button
        self.getcfgButton = ttk.Button(self, text='get config', state='disabled')
        self.getcfgButton['command'] = self.getcfg_clicked
        self.getcfgButton.grid(column=3, row=1, **options, sticky=tk.W)

        #show_config button
        self.showcfgButton = ttk.Button(self, text='show config', state='disabled')
        self.showcfgButton['command'] = self.showcfg_clicked
        self.showcfgButton.grid(column=3, row=2, **options, sticky=tk.W)

        #send_config button
        self.sendButton = ttk.Button(self, text='send config', state='disabled')
        self.sendButton['command'] = self.sendclicked
        self.sendButton.grid(column=3, row=3, **options, sticky=tk.W)

    def sendclicked(self):

        # print(self.cfgfilepath.get())
        send_config(self.session, self.cfgfilepath.get())

    def showcfg_clicked(self):
        TVwindow = treeViewWindow(data=self.container.cfg_tree)
        

    def connect_clicked(self):
        self.session = session_start(self.netconfHost.get(), self.netconfPort.get(), self.netconfUser.get(), self.netconfPWD.get())
        if self.session != 0:
            self.connected_action()


    def connected_action(self):
        # print(type(self.connected))
        self.userEntry.config(state = 'disabled')
        self.pwdEntry.config(state = 'disabled')
        self.portEntry.config(state = 'disabled')
        self.userEntry.config(state = 'disabled')
        self.hostEntry.config(state = 'disabled')
        self.getcfgButton.config(state = 'enabled')
        self.sendButton.config(state = 'enabled')
        self.capabilitiesButton.config(state = 'enabled')
        self.connected.set(True)
        

    def config_available_action(self):
        self.showcfgButton.config(state = 'enabled')

    def capabilites_clicked(self):
        print('capabilities_clicked()')
    
    def getcfg_clicked(self):
        print('getcfg_clicked()')
        
        reply = self.session.get_config(source='running')

        self.cfg_tree = etree.fromstring(str(reply))
        if self.cfg_tree.tag != 'None':
            self.cfg_sts.set(True)
            self.config_available_action()
        print(type(self.cfg_tree))
        print(self.cfg_tree.tag)
        self.container.cfg_tree = self.cfg_tree
        

if __name__ == "__main__":
    app = App()

    app.mainloop()
