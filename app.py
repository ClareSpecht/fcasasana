import wx
from wx import xrc 
import wx.grid as gridlib
import Audit
import os
import sys
import threading
import queue
from datetime import date
import Audit
import config
import asana
import datetime
import pandas as pd
client = asana.Client.access_token(config.token)
client.headers={"asana-enable": "new_user_task_lists"}
Audit.setClientWithToken(client)

class TabOne(wx.Panel):    
    def __init__(self, parent):
        #super().__init__(parent=None, title='Asana updates')
        wx.Panel.__init__(self, parent)
        #panel = wx.Panel(self)
        
        self.txt = wx.StaticText(self, pos=(5, 25), label = "Inventory")
        self.txt2 = wx.StaticText(self, pos=(5, 50), label = "Foster Inventory")
        self.txt3 = wx.StaticText(self, pos=(5, 75), label = "Heartworm")
        self.txt4 = wx.StaticText(self, pos=(5, 100), label = "Outcomes")

        self.fileCtrl = wx.FilePickerCtrl(self, pos=(100, 25))
        self.fileCtrl2 = wx.FilePickerCtrl(self, pos=(100, 50))
        self.fileCtrl3 = wx.FilePickerCtrl(self, pos=(100, 75))
        self.fileCtrl4 = wx.FilePickerCtrl(self, pos=(100, 100))
        
        my_btn = wx.Button(self, label='Run Updates', pos=(5, 130))
        my_btn.Bind(wx.EVT_BUTTON, self.on_press)

        my_btn2 = wx.Button(self, label='Create Audit Report', pos=(5, 160))
        my_btn2.Bind(wx.EVT_BUTTON, self.runAudit)

        #self.Show()
    def runAudit(self, event):    
        Audit.InventoryPath = getASpath(self.fileCtrl.GetPath())
        Audit.fosterpath = getASpath(self.fileCtrl2.GetPath())
        Audit.HWPath = getASpath(self.fileCtrl3.GetPath())
        Audit.OutcomePath = getASpath(self.fileCtrl4.GetPath())
        Audit.runAudit();

    def on_press(self, event):
        Audit.InventoryPath = getASpath(self.fileCtrl.GetPath())
        Audit.fosterpath = getASpath(self.fileCtrl2.GetPath())
        Audit.HWPath = getASpath(self.fileCtrl3.GetPath())
        Audit.OutcomePath = getASpath(self.fileCtrl4.GetPath())
        run(doAudit, 
            timeout=10000,
            finish_function=result_callback,
            timeout_function=timeout_callback,
            exception_function=exception_callback, )
    
class TabTwo(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        #t = wx.StaticText(self, -1, "This is t
        # he second tab", (20,20))
        self.txt = wx.StaticText(self, pos=(5, 25), label = "search by Id")
        self.txtinput = wx.TextCtrl(self,pos=(5, 50)) 
        my_btn = wx.Button(self, label='Search', pos=(5, 110))
        my_btn.Bind(wx.EVT_BUTTON, self.search)
    def search(self, event):
        aid = self.txtinput.GetValue()
        result = Audit.searchById(aid)
        dogs = []
        for dog in result:
            dogs.append({'name' : dog['name'], 'link' : dog['permalink_url']})
        myGrid = gridlib.Grid(self, pos=(5,150), size=(1000, 1000))
        myGrid.CreateGrid(len(dogs)+1, 2)
        myGrid.SetCellValue(0, 0, 'name')
        myGrid.SetCellValue(0, 1, 'link')

        row = 1
        for dog in dogs:
            #dogs.append({'name' : dog['name'], 'link' : dog['permalink_url']})
            myGrid.SetCellValue(row, 0, dog['name'])
            myGrid.SetCellValue(row, 1, dog['link'])
            row = row + 1

class TabThree(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.txt = wx.StaticText(self, pos=(5, 25), label = "report")

        self.fileCtrl = wx.FilePickerCtrl(self, pos=(100, 25))
        
        my_btn = wx.Button(self, label='Update Asana', pos=(5, 110))
        my_btn.Bind(wx.EVT_BUTTON, self.updateAsana)

        #self.Show()
    def updateAsana(self, event):    
        Audit.CACPath = getCACPath(self.fileCtrl.GetPath())
        print(Audit.CACPath)
        #Audit.runAudit();

class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="Asana updates")

        # Create a panel and notebook (tabs holder)
        p = wx.Panel(self)
        nb = wx.Notebook(p)
        tab1 = TabOne(nb)
        tab2 = TabTwo(nb)
        tab3 = TabThree(nb)
        # Add the windows to tabs and name them.
        nb.AddPage(tab1, "Update from Reports")
        nb.AddPage(tab2, "Search")
        nb.AddPage(tab3, "CAC Reports")
        #nb.AddPage(tab4, "Tab 4")

        # Set noteboook in a sizer to create the layout
        sizer = wx.BoxSizer()
        sizer.Add(nb, 1, wx.EXPAND)
        p.SetSizer(sizer)

def pictures():
    print("add pictures")
    Audit.addPicturesToNewDogs()
    return "pictures"

def inventory():
    print("update from Inventory")
    Audit.updateFromInventory()
    return "inventory"

def content():
    print("add to content")
    Audit.addToContentCreators()
    return "content"

def RTG():
    print("add to RTG")
    Audit.addToRTG()
    Audit.removeRTG()
    return "RTG"

def MT():
    Audit.addToMidtown()
    return "MT"

def website():
    print("update from website")
    Audit.updateFromWebsite()
    return "website"

def BT():
    print("move BT dogs")
    Audit.moveBTdogs()
    return "BT"

def rcontent():
    print("remove from content creators")
    Audit.removeFromContentCreators()
    return "rcontent"

def inCare():
    print('Sorting')
    Audit.moveInCareColumn()
    Audit.moveInFosterColumn()
    Audit.moveRTG()
    Audit.moveWalkBoard()
    Audit.moveMT()
    return "inCare"

def foster():
    print("Update from foster")
    Audit.updateFosterLocations()
    return "foster"
    
def HW():
    print("update HW")
    Audit.updateHWStatus()
    return "HW"

def subclean():
    print("Subtask Cleanup")
    Audit.cleansubs()
    return "subclean"

def doAudit():
    print(Audit.InventoryPath)
    print(Audit.fosterpath)
    print(Audit.HWPath)
    print("create missing dogs")
    today = str(date.today())
    tempupdate = client.tasks.update_task('1203776022137703', {'due_on':today}, opt_pretty=True)
    # Audit.createMissingDogs()
    # Audit.createMissingFosters()
    return "create"

def runNext(crnt):
     
    mp = {"create" : subclean}

    # mp = {"create" : pictures, 
    # "pictures" :inventory, 
    # "inventory" : website,
    # "website" : foster,
    # "foster" : RTG,
    # "RTG" : MT,
    # "MT" : inCare,
    # "inCare" : HW,
    # "HW" : subclean}

    if crnt in mp:
        fnct = mp[crnt]
        run(fnct, 
            timeout=10000,
            finish_function=result_callback,
            timeout_function=timeout_callback,
            exception_function=exception_callback, )

def result_callback(result):
    #label.SetLabel(result)
    runNext(result)
    print('finish '+result)
 
def timeout_callback():
    #label.SetLabel('timeout')
    print('timeout')

def exception_callback(e):
    print(e)
    #label.SetLabel('exception')

def getASpath(file_path):
    print (file_path)
    print('convert path')
    if os.path.splitext(file_path)[1] == '.xlsx' or os.path.splitext(file_path)[1] == '.xls':
        print('convert excel')
        read_file = pd.read_excel(file_path)
        read_file.to_csv (os.path.splitext(file_path)[0]+".csv", 
                        index = None,
                        header=True,
                        encoding = 'utf-8-sig')
        file_path = os.path.splitext(file_path)[0]+".csv"
    return file_path

def run(function,
        args=None,
        timeout=None,
        finish_function=None,
        timeout_function=None,
        exception_function=None, ):
    if args is None:
        args = ()
    result_queue = queue.Queue()
    worker_thread = WorkerThread(function, args, result_queue)
    monitor_thread = MonitorThread(result_queue,
                                   timeout,
                                   finish_function,
                                   timeout_function,
                                   exception_function)
    worker_thread.start()
    monitor_thread.start()

class WorkerThread(threading.Thread):
    def __init__(self, function, args, result_queue):
        threading.Thread.__init__(self)
        self.function = function
        self.result_queue = result_queue
        self.args = args

    def run(self):
        try:
            result = self.function(*self.args)
        except Exception as e:
            self.result_queue.put((False, e))
        else:
            self.result_queue.put((True, result))

class MonitorThread(threading.Thread):
    def __init__(self,
                 result_queue,
                 timeout,
                 finish_function,
                 timeout_function,
                 exception_function, ):
        threading.Thread.__init__(self)
        self.result_queue = result_queue
        self.timeout = timeout
        self.finish_function = finish_function
        self.timeout_function = timeout_function
        self.exception_function = exception_function

    def run(self):
        try:
            (finished, result) = self.result_queue.get(True, self.timeout)
            if finished:
                if self.finish_function is not None:
                    wx.CallAfter(self.finish_function, result)
            else:
                if self.exception_function:
                    wx.CallAfter(self.exception_function, result)
        except Exception as e:
            print(e)
            if self.timeout_function is not None:
                wx.CallAfter(self.timeout_function)

if __name__ == '__main__':
    app = wx.App()
    MainFrame().Show()
    #label = wx.StaticText(MainFrame().tab1.panel, pos=(5,150))
    #label = wx.StaticText(frame, pos=(5,150))
    #label.SetLabel("Results")
    app.MainLoop()
