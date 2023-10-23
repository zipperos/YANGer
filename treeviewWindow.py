import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from lxml import etree
from ncclient import manager
import re
from tkinter import filedialog as fd
from collections import deque
from copy import deepcopy
from netconfhandler import *


class treeViewWindow(tk.Toplevel):

##    What is planned for this class is:
##    1. take the data and data type
##    2. depending on data type generate proper treeview
##    3. types can be:
##      3.1 RPC xml - serialized (etree.Element) -> with this fucker it would be good to get ns .yangs as well !!!!DONE!!!!!
##      3.2 filter xml (etree.Element)
##      3.4 Capabilities
##      3.5 Yang - File
    
    def __init__(self, **kwargs):
        super().__init__()
        self.data = kwargs['data']
        self.datacopy = deepcopy(self.data)

        # configure the root window
        self.title('titlebar')
        self.geometry('800x600')
        self.__drawContent()

        self.TV1.focus_set()

        children = self.TV1.get_children()
        if children:
            self.TV1.focus(children[0])
            self.TV1.selection_set(children[0])

        self.TV1.bind("<<TreeviewSelect>>", self.data_collect)


    def data_collect(self, event):
        self.entry_id = self.TV1.selection()[0]
        if self.TV1.item(self.entry_id)['values']:
            value = self.TV1.item(self.entry_id)['values'][0]
            self.valueSelected.set(value)

            # print(self.valueSelected.get())
        else:
            pass
# I HAVE NO FUCKING CLUE WHY IT DOESNT WORK WITHOUT CALLBACK!!!!!
# Update - now I know, but kept dual var for logic clarity
    def value_callback(self, *args):
        # print('callback')
        self.valueEntry.delete(0, tk.END)
        self.valueEntry.insert(0, self.valueSelected.get())
    


    def __drawContent(self):

        self.columnconfigure(0, weight =1)

        self.TV1 = treeViews(self, data=self.data, datacopy=self.datacopy)
        self.TV1.grid(row=0, column=0, sticky='we')
        
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.TV1.yview)
        self.TV1.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        self.valueLabel = ttk.Label(self, text='Selected Value. Input new and press Save')
        self.valueLabel.grid(column=0, row=1, sticky=tk.W)
        self.valueSelected = tk.StringVar()
        self.displayedVal = tk.StringVar()
        self.valueEntry = ttk.Entry(self, textvariable=self.displayedVal)
        self.valueEntry.grid(column=0, row=2, sticky=tk.W)
        self.valueEntry.config(state='enabled')
        self.valueEntry.insert(0, 'whatever')
        self.valueSelected.trace_add('write', self.value_callback)

        #radiobutton -> enable saving; label + entry + file for saving config
        self.edit_sts = tk.BooleanVar(False)
        self.edit_checkbox = ttk.Checkbutton(self,
                text='Edit config enable',
                variable=self.edit_sts,
                onvalue='ON',
                offvalue='OFF')
        self.edit_checkbox.grid(column=0, row=3, sticky=tk.W)

        ##        select and save file
        self.fileLabel = ttk.Label(self, text='select file to save config')
        self.fileLabel.grid(column=0, row=4, sticky='we')
        self.cfgfilepath = tk.StringVar()
        self.config_filepathEntry = ttk.Entry(self, textvariable=self.cfgfilepath)
        self.config_filepathEntry.grid(column=0, row=5, sticky='we')
        self.config_filepathEntry.insert(0,'C:/Projects/new_config.xml')
        self.config_filepathEntry.config(state='enabled')
        self.selectButton = ttk.Button(self, text='Select')
        self.selectButton['command'] = self.select_clicked
        self.selectButton.grid(column=0, row=4, sticky='e')
        self.selectButton.config(state='enabled')

        # Select new file to save full config (somewhat useless, but can be used to re-head to serve as a full-config-send xml
        self.newCfgFile = open(self.cfgfilepath.get(), 'w')

        self.saveButton = ttk.Button(self, text='Save')
        self.saveButton['command'] = self.save_clicked
        self.saveButton.grid(column=0, row=6, sticky='w')
        self.saveButton.config(state='enabled')

        self.updateButton = ttk.Button(self, text='Update View')
        self.updateButton['command'] = self.update_clicked
        self.updateButton.grid(column=0, row=2, sticky='e')
        self.updateButton.config(state='enabled')

        # Items for generating minimised cfg-file with only modified items
        self.items_to_keep = set()
        self.copyitems_to_keep = set()

        self.minCfgButton = ttk.Button(self, text='Save minimized config file')
        self.minCfgButton['command'] = self.savecfg_clicked
        self.minCfgButton.grid(column=0, row=7, sticky='w')
        self.minCfgButton.config(state='enabled')


    def savecfg_clicked(self):
        self.generate_minimized_config()


    def update_clicked(self):
        for key, values in self.TV1.tree_dict.items():

            if int(values[0]) == int(self.entry_id):
                self.modify_content(element=key, copy_element=values[2])

    def modify_content(self, element, copy_element=None):
        if copy_element == None:
            copy_element = self.TV1.tree_dict[element][2]
        # Update the etree part
        element.text = self.displayedVal.get()
        copy_element.text = self.displayedVal.get()
        # Update visual part
        self.TV1.item(self.entry_id, values=(self.displayedVal.get()), tags='modified')

        
        cfg_namespace='urn:ietf:params:xml:ns:netconf:base:1.0'
        roottag = '{' + cfg_namespace + '}' + 'config'
        
        self.items_to_keep.add(element)

        # mincfg copy tree block *****
        self.copyitems_to_keep.add(copy_element)
        for parent in copy_element.iterancestors():
            self.copyitems_to_keep.add(parent)

        for sibling in copy_element.getparent().iterchildren():
            if not sibling.getchildren():
                self.copyitems_to_keep.add(sibling)
        # mincfg copy tree block END

        for parent in element.iterancestors():
            self.items_to_keep.add(parent)

        for sibling in element.getparent().iterchildren():
            if not sibling.getchildren():
                self.items_to_keep.add(sibling)

        print('items', self.items_to_keep)
        print('copyitems', self.copyitems_to_keep)
       

    def generate_minimized_config(self, cfg_namespace='urn:ietf:params:xml:ns:netconf:base:1.0'):
        roottag = '{' + cfg_namespace + '}' + 'config'

        cfgstr = 'rpc-reply|data'

        treecopy = self.datacopy

        deleteset = set()

        # Iterate through NOT SET!!! - iterate through old CFG. if not in SET - kick them out
        for item in treecopy.iter():
            print('item analyzed: ', item)
            if not item in self.copyitems_to_keep:
                print('in 1st if')
                if not item.getparent() == None:
                    print('in 2nd if - remove: ', item)
                    deleteset.add(item)
            else:
                print('in continue')
                continue
        for item in deleteset:
            item.getparent().remove(item)

        treecopy_t = etree.ElementTree(treecopy)


        treecopy_t.write('C:/Projects/minexperiment.xml', encoding='utf-8')
        
        formatToConfig(file='C:/Projects/minexperiment.xml')
        # RESET THE DATACOPY
        # self.datacopy = deepcopy(self.data)

        self.minCfgButton.config(state='disabled')



        # RESET the dictionary for treeview
        # idx = 0
        # wrappertree = self.data.getroottree()
        # text_check = lambda x: x if x else " "
        # for item in self.data.iter():
        #     if re.search(cfgstr, item.tag):
        #         pass
        #     else:
        #         record_stripped = self.TV1.gettag(item)
        #         record_parent = item.getparent()
        #         record = (record_stripped, text_check(item.text))

        #         if not record_parent in self.TV1.tree_dict.keys():
        #             xpathstr = wrappertree.getpath(item)
        #             copy_element = self.datacopy.xpath(xpathstr)[0]
        #             self.TV1.tree_dict.update({item: (idx, '', copy_element)})
        #         else:
        #             xpathstr = wrappertree.getpath(item)
        #             copy_element = self.datacopy.xpath(xpathstr)[0]
        #             self.TV1.tree_dict.update({item: (idx, self.TV1.tree_dict[record_parent][0], copy_element)})
        #     idx += 1
        
    def save_clicked(self):
        for key, values in self.TV1.tree_dict.items():
            if int(values[0]) == int(self.entry_id):
                # print('!!!Found Key:   ', key)

                self.modify_content(element=key)


        self.data.getroottree().write(self.newCfgFile.name, encoding='utf-8')
        return True


    def select_clicked(self):
        self.newCfgFile = self.select_file()
        self.cfgfilepath.set(str(self.newCfgFile.name))

    
    def select_file(self):
        filetypes = (
            ('xml files', '*.xml'),
            ('All files', '*.*')
        )
        file = fd.asksaveasfile(
            initialfile = 'new_config.xml',
            defaultextension = '.xml',
            initialdir='/',
            filetypes=filetypes)
        return file


class treeViews(ttk.Treeview):
    def __init__(self, container, **kwargs):
        super().__init__(container)
        self.data = kwargs['data']
        self.datacopy = kwargs['datacopy']
        self['columns'] = ('values')

##        self.config(show = '')
        self.generate_entries(self.data, self.datacopy)

    def dbg1(self):
        print("asdf")


    def generate_entries(self, data, datacopy, type='rpc_reply'):
        self.tree_dict = dict()
        text_check = lambda x: x if not x == None else " "
        idx = 0

        wrappertree = etree.ElementTree(data)

        if type == 'rpc_reply':
            cfgstr = 'rpc-reply|data'
        for item in data.iter():
            if re.search(cfgstr, item.tag):
                pass
            else:
                record_stripped = self.gettag(item)
                record_parent = item.getparent()
                record = (record_stripped, text_check(item.text))

                if not record_parent in self.tree_dict.keys():
                    xpathstr = wrappertree.getpath(item)
                    copy_element = datacopy.xpath(xpathstr)[0]
                    self.tree_dict.update({item: (idx, '', copy_element)})
                else:
                    xpathstr = wrappertree.getpath(item)
                    copy_element = datacopy.xpath(xpathstr)[0]
                    self.tree_dict.update({item: (idx, self.tree_dict[record_parent][0], copy_element)})

                self.insert(parent=self.tree_dict[item][1], index='end', iid=self.tree_dict[item][0], text=record[0], values=record[1].replace(' ', '\ '), tags='not_modified')
                self.tag_configure('modified', background='yellow', font='bold')
            idx += 1
            
    def gettag(self, element):
        return etree.QName(element).localname