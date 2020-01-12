import Tkinter as tk
import tkMessageBox
import tkFileDialog
import aos
import cv2
import numpy as np
import os
import shutil
from PIL import Image, ImageTk

root = tk.Tk()

'''Window Customization'''
root.title('AOS v0.1')
root.geometry("900x500+100+100")

def filename(fp):
    fn = fp.split('/')
    return fn[len(fn)-1]

def cvtImg(img):
    #Rearrang the color channel
    b,g,r = cv2.split(img)
    img = cv2.merge((r,g,b))

    # Convert the Image object into a TkPhoto object
    im = Image.fromarray(img)
    imgtk = ImageTk.PhotoImage(image=im) 
    return imgtk


'''---------------- Menu bar Commands ----------------'''
def openfile():
    #Reading The File
    ftype = [('PNG','*.png'),('JPEG','*.jpg')]
    dlg = tkFileDialog.Open(filetypes = ftype)
    fp = dlg.show()     #Gives path of the open file
    fn = filename(fp)   #Returns File Name
    
    #Creating temp Folder For opencv access
    try:
        os.mkdir("temp")
    except OSError:
        print("Failed to make temp folder")

    #Copying Image to the temp folder
    destination = os.getcwd() + "/temp/" + fn
    dest = shutil.copyfile(fp,destination)

    #Final File Path
    image_path = "temp/"+str(fn)
    
    # Load an color image
    img = cv2.imread(image_path)
    
    try : 
        img_resized = cv2.resize(img,(500,500))
        img_fc = aos.findCorners(img_resized,[img.shape[1],img.shape[0]])

        
        ogomr_img = cvtImg(img)
        root.ogomr_img = ogomr_img
        #ogomr_l.configure(image = ogomr_img)
        #ogomr_l.image = ogomr_img
        ogCanvas.create_image(0,0,image=ogomr_img,anchor="nw")
        ogCanvas.config(scrollregion=(0,0,img.shape[1],img.shape[0]))

        domr_img = cvtImg(img_fc)
        root.domr_img = domr_img
        #domr_l.configure(image=domr_img)
        #domr_l.image = domr_img
        #doCanvas.create_image(0,0,image=domr_img)
        doCanvas.create_image(0,0,image=domr_img,anchor="nw")
        doCanvas.config(scrollregion=(0,0,img_fc.shape[1],img_fc.shape[0]))
        
        #root.update()
        #ogCanvas.update()
        print("Open function done!")

    except:
        tkMessageBox.showerror("Try again","No omr was detected in the image. Please try again with a different image.")


def deletetemp():
    try:
        shutil.rmtree("temp")
    except:
        print("Couldn't delete directory temp")
    root.quit()

'''---------------------------- Menu bars ----------------------------'''
menubar = tk.Menu(root)
#file menu
filemenu = tk.Menu(menubar,tearoff=0)
filemenu.add_command(label="Open",command=openfile)
filemenu.add_command(label="Exit",command=deletetemp)
menubar.add_cascade(label="File",menu=filemenu)
root.config(menu=menubar)

'''----------------------- Main GUI ------------------'''
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(0, weight=1)

'''---------- Image Processing -----------'''
#Original Image Frame
ogImgFrame = tk.LabelFrame(root,text="Original Image")
ogImgFrame.grid(row=0,column=0,sticky=tk.N+tk.S+tk.E+tk.W,padx=10,pady=5)

ogCanvas = tk.Canvas(ogImgFrame,height=200,width=200,scrollregion=(0,0,500,800))  #Canvas For Image
ogScrollbarY = tk.Scrollbar(ogCanvas,orient="vertical")    #Y-Scrollbar
ogScrollbarX = tk.Scrollbar(ogCanvas,orient="horizontal")   #X-Scrollbar
ogCanvas.config(yscrollcommand=ogScrollbarY.set)    #Config Canvas For Y
ogCanvas.config(xscrollcommand=ogScrollbarX.set)    #Config Canvas For X
ogScrollbarY.config(command=ogCanvas.yview)         #Config Command For Scroll Y
ogScrollbarX.config(command=ogCanvas.xview)         #Config Command For Scroll X
ogScrollbarY.pack(side=tk.RIGHT,fill=tk.Y)          #Packing Scroll Y
ogScrollbarX.pack(side=tk.BOTTOM,fill=tk.X)         #Packing Scroll X
ogCanvas.pack(expand=1,fill=tk.BOTH)                #Packing Canvas

#Detected OMR Frame
doImgFrame = tk.LabelFrame(root,text="Detected OMR")
doImgFrame.grid(row=0,column=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5)

doCanvas = tk.Canvas(doImgFrame,height=200,width=200,scrollregion=(0,0,500,800))    #Canvas For Detected OMR
doScrollbarY = tk.Scrollbar(doCanvas,orient="vertical")     #Y-Scrollbar
doScrollbarX = tk.Scrollbar(doCanvas,orient="horizontal")   #X-Scrollbar
doCanvas.config(yscrollcommand=doScrollbarY.set)        #Config Canvas For Y                
doCanvas.config(xscrollcommand=doScrollbarX.set)        #Config Canvas For X
doScrollbarY.config(command=doCanvas.yview)             #Config Command For Scroll Y
doScrollbarX.config(command=doCanvas.xview)             #Config Command For Scroll X
doScrollbarY.pack(side=tk.RIGHT,fill=tk.Y)              #Packing Scroll Y
doScrollbarX.pack(side=tk.BOTTOM,fill=tk.X)             #Packing Scroll X
doCanvas.pack(expand=1,fill=tk.BOTH)                    #Packing Canvas

#Settings Panel
settingsFrame = tk.LabelFrame(root,text="Settings")
settingsFrame.grid(row=0,column=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5)

testL = tk.Label(settingsFrame,text="Settings & Export Options Will Be Added Here")
testL.pack()

root.protocol('WM_DELETE_WINDOW', deletetemp)
root.mainloop()