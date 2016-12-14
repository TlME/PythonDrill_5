#=================================
## Python Drill 5
# A revised file-handling GUI
# By Nick Henegar
#==============================================================================================
# 
#==============================================================================================

#imports
import os
import shutil
import time
import sqlite3
from tkinter import *
from tkinter import ttk

#GUI Class
class FileTransferGUI:
    def __init__(self, master):
    # Initializing some values here:
        self.currentTime = time.time()
        self.localTime = time.localtime()
        self.src = StringVar('')
        self.dst = StringVar('')
        self.timeSince = [0,0,0,0]
    # Starting db connection
        self.sqlite_file = 'lastCheck.sqlite'
        self.conn = sqlite3.connect(self.sqlite_file)
        self.c = self.conn.cursor()
        self.c.execute('CREATE TABLE IF NOT EXISTS timestamps(epochTime REAL, localTime TEXT)')
        self.c.execute('SELECT * FROM timestamps ORDER BY epochTime DESC LIMIT 1')
        if self.c.fetchall() == []:
            self.c.execute("INSERT INTO timestamps(epochTime, localTime) VALUES(0.0, 'dummyValues')")
        self.c.execute('SELECT * FROM timestamps ORDER BY epochTime DESC LIMIT 1')
        self.lastTransfer = self.c.fetchone()[0]
        self.timeSince = timeConvert(int(self.currentTime - self.lastTransfer), self.timeSince) 
    # Styling the master window and the two slave frames
        master.title('File Transfer GUI')
        master.configure(height = 1000, width = 1000, background = 'light blue')
        self.style = ttk.Style()
        self.style.configure('Header.TLabel', font = ('Arial', 20))
        self.frame_header = ttk.Frame(master)
        self.frame_header.pack(fill = BOTH, expand = 1)
        # Adding pretty pictures (stored in same folder)
        self.header_img = PhotoImage(file = 'fileTransfer.gif')
        self.folder_img = PhotoImage(file = 'folder.gif')
        self.file_img = PhotoImage(file = 'file.gif')
        self.src_img = PhotoImage(file = 'src.gif')
        self.dst_img = PhotoImage(file = 'dst.gif')
        # Header
        ttk.Label(self.frame_header, image = self.header_img).grid(row = 0, column = 0, rowspan = 2)
        ttk.Label(self.frame_header, text = 'Basic File Transfer GUI', style = 'Header.TLabel').grid(row = 0, column = 1)
        ttk.Label(self.frame_header, wraplength = 200, justify = CENTER,
                  text = ("Click on the source and destination buttons below to set directories for file transfer.\nRecently modified items will show up highlighted in green.")).grid(row = 1, column = 1)
        # Content
        self.frame_content = ttk.Frame(master)
        self.frame_content.pack(fill = BOTH, expand = 1) 
        
        # Create a paned window to handle the file browsers
        self.fileBrowser = ttk.Frame(self.frame_content)
        self.fileBrowser.grid(row = 1, column = 0, columnspan = 2, sticky = E + W + N + S)
        self.fileBrowser.grid_rowconfigure(0, weight=1)
        self.fileBrowser.grid_columnconfigure(0, weight=1)
        # Source file viewer
        self.frame_source = ttk.Frame(self.fileBrowser, relief = SUNKEN)
        self.frame_source.grid(row = 0, column = 0, sticky = E + W + N + S)
        self.frame_source.grid_rowconfigure(0, weight=1)
        self.frame_source.grid_columnconfigure(0, weight=1)
        self.src_treeview = ttk.Treeview(self.frame_source, selectmode = 'extended')
        self.src_treeview.grid(row = 0, column = 0, sticky = E + W + N + S)
        self.src_treeview.grid_rowconfigure(0, weight=1)
        self.src_treeview.grid_columnconfigure(0, weight=1)
        # This scrollbar exists, but does nothing.
##        self.scrollbar = ttk.Scrollbar(self.frame_source, orient = HORIZONTAL)
##        self.scrollbar.grid(row = 1, column = 0, sticky = S)
##        self.src_treeview.config(xscrollcommand = self.scrollbar.set)
##        self.scrollbar.config(command = self.src_treeview.xview)
##        =============================================================================
            # The genTrees function will tag appended tree widgets with the tag 'recent' if their associated file has been
            #   modified in the past 24 hours, this makes the treeview display their text in green.
        self.src_treeview.tag_configure('recent', foreground = 'dark green')

        #Destination file viewer
        self.frame_destination = ttk.Frame(self.fileBrowser, relief = SUNKEN)
        self.frame_destination.grid(row = 0, column = 2, sticky = E + W + N + S)
        self.dst_treeview = ttk.Treeview(self.frame_destination, selectmode = 'none')
        self.dst_treeview.grid(row = 0, column = 0, sticky = E + W + N + S)
        self.dst_treeview.grid_rowconfigure(0, weight=1)
        self.dst_treeview.grid_columnconfigure(0, weight=1)

         # Directory choice buttons
        self.srcButton = ttk.Button(self.frame_content, image = self.src_img, text = 'Source Directory',
                                    compound = LEFT, command = lambda: self.src.set(choose(self.src_treeview, self.file_img, self.folder_img, self.currentTime, '')))
        self.srcButton.grid(row = 0, column = 0)
        self.dstButton = ttk.Button(self.frame_content, image = self.dst_img, text = 'Destination Directory',
                                    compound = LEFT, command = lambda: self.dst.set(choose(self.dst_treeview, self.file_img, self.folder_img, self.currentTime, '')))
        self.dstButton.grid(row = 0, column = 1)
        self.transferButton  = ttk.Button(self.frame_content, text = 'Transfer',
                                    command = lambda: transfer(self.src.get(), self.dst.get(), self.currentTime, self.localTime, self.conn))
        self.transferButton.grid(row = 2, column = 0)
        self.refreshButton = ttk.Button(self.frame_content, text = 'Refresh',
                                    command = lambda: choose(self.dst_treeview, self.file_img, self.folder_img, self.currentTime, self.dst.get()))
        self.refreshButton.grid(row = 2, column = 1)
        # Label to indicate time since last update
        self.updateLabel = ttk.Label(self.frame_content, justify = CENTER,
                                     text = ('Time since last file transfer: \n' + str(self.timeSince[0]) + ' Days, '
                                    + str(self.timeSince[1]) + ' Hours, '+ str(self.timeSince[2]) + ' Minutes, ' + str(self.timeSince[3]) + ' Seconds.'))
        self.updateLabel.grid(row = 3, column = 0, columnspan = 2)
#====== Choose ============================================================================================
# @args -
    # src_treeview - the treeview widget that is to have elements appended
    # file_img, folder_img - two .gifs which distinguish files from folders (Must be in same folder as main)
    # currentTime - a time.time() object, used to track how recently something was modified
    # existingDir - a string which was a previously choosen file-path, to allow for refresh functionality
# @returns - src : a string that represents the filepath used to reach the chosen directory
#
# Usage - allows user to choose a directory to be indexed, drops the current treeview, then populates a new
#           treeview based off the files and folders contained within the target directory.
# !!! Will ignore the .git folder !!!
#===========================================================================================================
def choose(src_treeview, file_img, folder_img, currentTime, existingDir):
    if existingDir == '':
        src = filedialog.askdirectory()
    else:
        src = existingDir
    src_treeview.delete(*src_treeview.get_children())
    #File Viewing utility:
    def genTrees(src_treeview, src, parent, file_img, folder_img, currentTime):
        i = 0
        children = os.listdir(src)
        for child in children:
            if child.endswith(".git"):
                continue
            try:
                test = os.listdir(src + "/" + child)
                src_treeview.insert(parent, 'end', parent + str(i), image = folder_img, text = child)
                genTrees(src_treeview, src + "/" + child,  parent + str(i), file_img, folder_img, currentTime)
            except (NotADirectoryError):
                recently_modified = ((currentTime - os.stat(src + "/" + child).st_mtime) <= 86400)
                if recently_modified:
                    src_treeview.insert(parent, 'end', parent + str(i), image = file_img, text = child, tags = 'recent')
                else:
                    src_treeview.insert(parent, 'end', parent + str(i), image = file_img, text = child)
            i += 1
    genTrees(src_treeview, src, '', file_img, folder_img, currentTime)
    return src

#==== Transfer Utility:=====================================================================================================
# @args -
    # src, dst - strings which represent the filepath where the directory is located.
    # currentTime - a time.time() object, used to track how recently something was modified
# @return - None
#
# Usage - Moves recently modified(past 24 hours) files from a src directory to a destination directory.
#
# Notes - This could probably have been merged with the "Choose" function, but due to subtle diffListerences in application,
#   I opted to instead have them as two separate functions. I could probably have included a boolean "move" flag to dictate
#   whether one behavior was intended or the other. However, that did not occur, and probably will never occur.
#============================================================================================================================
def transfer(src, dst, currentTime, localTime, conn):
        children = os.listdir(src)
        for child in children:
            if child.endswith(".git"):
                continue
            try:
                test = os.listdir(src + "/" + child)
                transfer(src + "/" + child, dst, currentTime)
            except (NotADirectoryError):
                recently_modified = ((currentTime - os.stat(src + "/" + child).st_mtime) <= 86400)
                if recently_modified:
                    shutil.copy2(src + "/" + child, dst) #move normally, copy for now
                else:
                    pass
        # This logs the time of tranfer to a db
        c = conn.cursor()
        c.execute("INSERT INTO timestamps(epochTime, localTime) VALUES(?, ?)", (currentTime, str(time.strftime('%Y-%m-%d %H:%M:%S'))))
        conn.commit()
        c.close()
        conn.close()
# Time conversion
def timeConvert(timeDiff, diffList):
    diffList[0] = timeDiff // 86400
    timeDiff = timeDiff % 86400
    diffList[1] = timeDiff // 3600
    timeDiff = timeDiff % 3600
    diffList[2] = timeDiff // 60
    diffList[3] = timeDiff % 60
    return diffList

#Clock widget
    
# main function execution            
def main():
    root = Tk()
    fileGUI = FileTransferGUI(root)
    root.mainloop()

# module handling
if __name__ == "__main__": main()
