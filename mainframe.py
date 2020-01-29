import Tkinter as tk
import tkMessageBox
import tkFileDialog
import aos
import cv2
import os
import numpy as np
import ast
import shutil
import presets
from PIL import Image, ImageTk

#Some Global Variables
direction = []
zoomFactor = 1.3
actualSize = []
batches = []
titleWithPreset = "AOS v1.0"
method = 0

'''---------------- Functions ----------------'''
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
     
def onLeftDrag(event):
    direction.insert(0,[event.x,event.y])
    dragVectorX = direction[1][0] - direction[0][0]
    dragVectorY = direction[1][1] - direction[0][1]
    event.widget.xview_scroll(dragVectorX,tk.UNITS)
    event.widget.yview_scroll(dragVectorY,tk.UNITS)
    direction.pop()
    
def MouseClick(event):
    try:
        direction.pop()
    except:
        pass
    finally:
        direction.insert(0,[event.x,event.y])
    event.widget.bind('<B1-Motion>', onLeftDrag)

def ImgZoomIn(canvas):
    try:
        newSize = [int(canvas.sizeX*zoomFactor),int(canvas.sizeY*zoomFactor)]
        displayImage(canvas.original,canvas,newSize)
    except:
        print("Failed to zoom in.")

def ImgZoomOut(canvas):
    try:
        newSize = [int(canvas.sizeX/zoomFactor),int(canvas.sizeY/zoomFactor)]
        displayImage(canvas.original,canvas,newSize)
    except:
        print("Failed to zoom Out.")

def bindZooms(canvas):
    zoomIn = tk.Button(canvas,text="+",width=2,command= lambda: ImgZoomIn(canvas)) #Building Zoom in Button
    zoomIn.pack(side=tk.TOP,anchor=tk.N+tk.E)

    zoomOut = tk.Button(canvas,text="-",width=2,command = lambda: ImgZoomOut(canvas))     #Builfing Zoom Out Button
    zoomOut.pack(side=tk.TOP,anchor=tk.N+tk.E)
    

'''---------------- Menu bar Commands ----------------'''
def openfile():
    #Reading The File
    ftype = [('JPEG','*.jpg'),('PNG','*.png')]
    dlg = tkFileDialog.Open(filetypes = ftype)
    fp = dlg.show()     #Gives path of the open file
    fn = filename(fp)   #Returns File Name
    root.title(titleWithPreset + " - " + str(fn))
    
    #Creating temp Folder For opencv access
    try:
        os.mkdir(".temp")
    except OSError:
        print("Failed to make temp folder")

    #Copying Image to the temp folder
    destination = os.getcwd() + "/.temp/" + fn
    dest = shutil.copyfile(fp,destination)

    #Final File Path
    image_path = ".temp/"+str(fn)

    # Load an color image
    img = cv2.imread(image_path)
    displayImage(img,ogCanvas,[img.shape[1],img.shape[0]])
    try:
        img_fc = aos.findCorners(img,cp1=presetCE1,cp2=presetCE2,bp=presetBlur)
        displayImage(img_fc,doCanvas,[img_fc.shape[1],img_fc.shape[0]])
        handleScanning(img_fc)
    except Exception as e:
        tkMessageBox.showerror("Try again","No omr was detected in the image. Please try again with a different image.")
        print(e)

def displayImage(img,canvas,size=[]):   #Displays Image On A Specific Canvas
    canvas.original = img
    resize_img = cv2.resize(img,(size[0],size[1]))
    canvas.sizeX = size[0]
    canvas.sizeY = size[1]
    canvas_img = cvtImg(resize_img)
    canvas.canvas_img = canvas_img
    canvas.create_image(0,0,image=canvas_img,anchor="nw")
    canvas.config(scrollregion=(0,0,canvas.sizeX,canvas.sizeY))

    root.update()
    print("Displayed!")
        
def handleScanning(img):
    global doCanvas
    scannedImage = img
    for batch in batches:
        print("Batch in scan : " + str(batch))
        print("Fx : " + str(batch[2]))
        scannedImage = aos.scanOmr(scannedImage,actualSize=actualSize,init=[batch[2],batch[3]],diff=[batch[4],batch[5]],resize=[5000,5000]
        ,totalMCQs=batch[1],totalOptions=batch[0],showDots=True,method=method)
    
    displayImage(scannedImage,doCanvas,[scannedImage.shape[1],scannedImage.shape[0]])

def deletetemp():
    global root
    try:
        shutil.rmtree(".temp")
    except:
        print("Couldn't delete directory temp")
    root.destroy()

def bindScrollbar(Canvas):
    ScrollbarY = tk.Scrollbar(Canvas,orient="vertical")    #Y-Scrollbar
    ScrollbarX = tk.Scrollbar(Canvas,orient="horizontal")   #X-Scrollbar
    Canvas.config(yscrollcommand=ScrollbarY.set,xscrollcommand=ScrollbarX.set,yscrollincrement='1',xscrollincrement='1')    #Config Canvas For Y & X
    ScrollbarY.config(command=Canvas.yview)         #Config Command For Scroll Y
    ScrollbarX.config(command=Canvas.xview)         #Config Command For Scroll X
    ScrollbarY.pack(side=tk.RIGHT,fill=tk.Y)          #Packing Scroll Y
    ScrollbarX.pack(side=tk.BOTTOM,fill=tk.X)         #Packing Scroll X

def main():
    #global variables
    global ogImgFrame,doImgFrame,ogCanvas,doCanvas,root,titleWithPreset

    root = tk.Tk()
    '''--------- Window Customization --------'''
    newTitle = "AOS v1.0 - preset : " + titleWithPreset
    titleWithPreset = newTitle
    root.title(titleWithPreset)
    root.geometry("1000x600+50+50")
    root.focus_force()

    '''-------------------- Menu bars --------------------'''
    menubar = tk.Menu(root)
    #file menu
    filemenu = tk.Menu(menubar,tearoff=0)
    filemenu.add_command(label="Open",command=openfile)
    filemenu.add_separator()
    filemenu.add_command(label="Exit",command=deletetemp)
    menubar.add_cascade(label="File",menu=filemenu)
    root.config(menu=menubar)

    '''-----------######------------------- Main GUI -----------------######-----------'''
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)
    root.grid_rowconfigure(0, weight=1)

    '''--------------------- Frames --------------------'''

    #--------------- Original Image Frame
    ogImgFrame = tk.LabelFrame(root,text="Original Image")
    ogImgFrame.grid(row=0,column=0,sticky=tk.N+tk.S+tk.E+tk.W,padx=10,pady=5)

    ogCanvas = tk.Canvas(ogImgFrame,height=200,width=200,scrollregion=(0,0,500,800))  #Canvas For Image
    bindScrollbar(ogCanvas)
    ogCanvas.pack(expand=1,fill=tk.BOTH)                #Packing Canvas

    #--------------- Detected OMR Frame
    doImgFrame = tk.LabelFrame(root,text="Detected OMR")
    doImgFrame.grid(row=0,column=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5)

    doCanvas = tk.Canvas(doImgFrame,height=200,width=200,scrollregion=(0,0,500,800))    #Canvas For Detected OMR
    bindScrollbar(doCanvas)
    doCanvas.pack(expand=1,fill=tk.BOTH)                    #Packing Canvas


    #Zoom in and zoom out buttons
    bindZooms(ogCanvas)
    bindZooms(doCanvas)

    #--------------- Settings Panel
    settingsFrame = tk.LabelFrame(root,text="Settings")
    settingsFrame.grid(row=0,column=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5)

    testL = tk.Label(settingsFrame,text="Settings & Export Options Will Be Added Here")
    testL.pack()

    #-------------- Binding Functionality
    ogCanvas.bind("<Button-1>", MouseClick)
    doCanvas.bind("<Button-1>", MouseClick)

    '''---------------------------- Exit Commands ----------------------------'''
    root.protocol('WM_DELETE_WINDOW', deletetemp)
    root.mainloop()

def presetProcessor(presetString,scanningMethod):
    global batches,presetName,presetDescription,presetCE1,presetCE2,presetBlur,actualSize,root,titleWithPreset,method
    method = scanningMethod
    batches = []
    print("Method Chosen : " + str(method))
    try:
        presetData = presetString.split("$")
        presetName = presetData[0]
        presetDescription = presetData[1]
        actualSize = ast.literal_eval(presetData[2])
        presetCE1 = int(presetData[3])
        presetCE2 = int(presetData[4])
        presetBlur = int(presetData[5])
        presetTotalBatches = int(presetData[6])
        for batchIndex in range(7,7+presetTotalBatches,1):
            batches.append(ast.literal_eval(presetData[batchIndex]))
        print(batches)
        titleWithPreset = presetName
        main()
        presets.main()

    except Exception as e:
        tkMessageBox.showerror("Corrupted Preset","The preset you are trying to use is corrupted. Re-make the preset or use another one.")
        print(e)

if __name__ == "__main__":
    main()