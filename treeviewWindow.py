import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from lxml import etree
from ncclient import manager
import re


class treeViewWindow(tk.Tk):

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
        entry_id = self.TV1.selection()[0]
        if self.TV1.item(entry_id)['values']:
            value = self.TV1.item(entry_id)['values'][0]
            self.valueSelected.set(value)
            print(self.valueSelected.get())
        else:
            pass

    def value_callback(self, *args):
        print('callback')
        self.valueEntry.insert(0, self.valueSelected.get())

    def __drawContent(self):
##        datapass = self.dummyDataEtree()
        datapass = self.data
        self.columnconfigure(0, weight =1)

        self.TV1 = treeViews(self, data=datapass)
        self.TV1.grid(row=0, column=0, sticky='we')
        
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.TV1.yview)
        self.TV1.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        self.valueLabel = ttk.Label(self, text='Selected Value')
        self.valueLabel.grid(column=0, row=1, sticky=tk.W)
        self.valueSelected = tk.StringVar()
        self.valueEntry = ttk.Entry(self, textvariable=self.valueSelected)
        self.valueEntry.grid(column=0, row=2, sticky=tk.W)
        self.valueEntry.config(state='enabled')
        self.valueSelected.trace_add('write', self.value_callback)
        


class treeViews(ttk.Treeview):
    def __init__(self, container, **kwargs):
        super().__init__(container)
        self.data = kwargs['data']
        # print(self.data)
        self['columns'] = ('values')

##        self.config(show = '')
        self.generate_entries(self.data)


    def generate_entries(self, data, type='rpc_reply'):
        tree_dict = dict()
        text_check = lambda x: x if x else " "
        idx = 0
        if type == 'rpc_reply':
            cfgstr = 'rpc-reply|data|config'
        for item in data.iter():
            if re.search(cfgstr, item.tag):
                pass
            else:
                record_stripped = self.gettag(item)
                record_parent = item.getparent()
                record = (record_stripped, text_check(item.text))

                if not record_parent in tree_dict.keys():
                    tree_dict.update({item: (idx, '')})
                else:
                    tree_dict.update({item: (idx, tree_dict[record_parent][0])})

                self.insert(parent=tree_dict[item][1], index='end', iid=tree_dict[item][0], text=record[0], values=record[1])
            idx += 1
            
    def gettag(self, element):
        return etree.QName(element).localname