import Tkinter as tk
import tkMessageBox
import tkFileDialog
import cv2
import os
import aos
import presets
import numpy as np
import shutil
from PIL import Image, ImageTk
import circleProcessor

direction = []
zoomFactor = 1.3
batchCount = 0
batches = []
batchSizeY = 0
batchHeight = 0
lastMouseClick = [0,0]
currentBatch = 0
currentParameterIndex = 0
gImage = 0
gImageDetected = 0

def cvtImg(img):
    #Rearrang the color channel
    b,g,r = cv2.split(img)
    img = cv2.merge((r,g,b))

    # Convert the Image object into a TkPhoto object
    im = Image.fromarray(img)
    imgtk = ImageTk.PhotoImage(image=im) 
    return imgtk 

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

def deletetemp():
    global batches
    confirm = tkMessageBox.askyesno("Confrim","If You Didn't Save Your Preset Then All of Your Settings will be lost. Are you sure you want to exit ?")
    if confirm:
        try:
            shutil.rmtree(".temp")
        except:
            print("Couldn't delete directory temp")

        batches = []
        root.destroy()
        presets.main()

def bindScrollbar(Canvas):
    ScrollbarY = tk.Scrollbar(Canvas,orient="vertical")    #Y-Scrollbar
    ScrollbarX = tk.Scrollbar(Canvas,orient="horizontal")   #X-Scrollbar
    Canvas.config(yscrollcommand=ScrollbarY.set,xscrollcommand=ScrollbarX.set,yscrollincrement='1',xscrollincrement='1')    #Config Canvas For Y & X
    ScrollbarY.config(command=Canvas.yview)         #Config Command For Scroll Y
    ScrollbarX.config(command=Canvas.xview)         #Config Command For Scroll X
    ScrollbarY.pack(side=tk.RIGHT,fill=tk.Y)          #Packing Scroll Y
    ScrollbarX.pack(side=tk.BOTTOM,fill=tk.X)         #Packing Scroll X

def handleDetection(img,doCanvas,ce1Value=70,ce2Value=20,blurValue=17):
    global gImageDetected
    try:
        img_detected = aos.findCorners(img,cp1=ce1Value,cp2=ce2Value,bp=blurValue)
        gImageDetected = img_detected
        displayImage(img_detected,doCanvas,[img_detected.shape[1],img_detected.shape[0]])
    except Exception as e:
        tkMessageBox.showerror("Try again","No OMR was detected in the image. Please try changing the settings or open a different image.")
        print(e)

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
    canvas.zoomIn = tk.Button(canvas,text="+",width=2,command= lambda: ImgZoomIn(canvas)) #Building Zoom in Button
    canvas.zoomIn.pack(side=tk.TOP,anchor=tk.N+tk.E)

    canvas.zoomOut = tk.Button(canvas,text="-",width=2,command = lambda: ImgZoomOut(canvas))     #Builfing Zoom Out Button
    canvas.zoomOut.pack(side=tk.TOP,anchor=tk.N+tk.E)

def showPreview(event):
    #Event is a garbage variable. Event is import because of the keybind to Entry widget
    try:
        scannedImage = doCanvas.original
        actualSize = [scannedImage.shape[1],scannedImage.shape[0]]
        for batch in batches:
            fx = batch.firstQuestionXY[0]
            fy = batch.firstQuestionXY[1]
            dx = batch.secondOptionXY[0] - fx
            dy = batch.secondQuestionXY[1] - fy
            totalOptions = abs(int(batch.totalOptionEntry.get()))
            totalMCQs = abs(int(batch.totalMCQEntry.get()))

            scannedImage, batchResult = aos.scanOmr(scannedImage,actualSize=actualSize,init=[fx,fy],diff=[dx,dy],resize=[5000,5000]
            ,totalMCQs=totalMCQs,totalOptions=totalOptions,showDots=True,method=0)
        
        displayImage(scannedImage,doCanvas,size=actualSize)

    except Exception as e:
        print(e)

def showPicks():
    try:
        gImageDetectedCopy = np.copy(gImageDetected)
        for batch in batches:
            cv2.circle(gImageDetectedCopy,tuple(batch.firstQuestionXY),2,[0,0,255],3)
            cv2.circle(gImageDetectedCopy,tuple(batch.secondOptionXY),2,[0,255,0],3)
            cv2.circle(gImageDetectedCopy,tuple(batch.secondQuestionXY),2,[255,0,0],3)
        displayImage(gImageDetectedCopy,doCanvas,[gImageDetectedCopy.shape[1],gImageDetectedCopy.shape[0]])
    except Exception as e:
        print(e)

    showPreview(0)

def applySettings(ce1Value,ce2Value,blurValue,showCanny,img):
    if blurValue % 2 == 0:
        blurValue -= 1

    new_blur = cv2.GaussianBlur(img,(blurValue,blurValue),0)
    new_canny = cv2.Canny(new_blur,ce1Value,ce2Value)
    new_bgr = cv2.cvtColor(new_canny,cv2.COLOR_GRAY2BGR)
    if showCanny == 1:
        displayImage(new_bgr,ogCanvas,[ogCanvas.sizeX,ogCanvas.sizeY])
    else:
        displayImage(img,ogCanvas,[ogCanvas.sizeX,ogCanvas.sizeY])
    handleDetection(img,doCanvas,ce1Value=ce1Value,ce2Value=ce2Value,blurValue=blurValue)
    
    showPicks()

def getPoint(event):
    global doCanvas

    #------------- Setting Up Parameters
    if currentParameterIndex == 0 :
        currentBatch.firstQuestionXY = [int(doCanvas.xview()[0]*doCanvas.original.shape[1] + event.x) - 2,
        int(doCanvas.yview()[0]*doCanvas.original.shape[0] + event.y) - 2]
    elif currentParameterIndex == 1:
        currentBatch.secondOptionXY = [int(doCanvas.xview()[0]*doCanvas.original.shape[1] + event.x) - 2,
        int(doCanvas.yview()[0]*doCanvas.original.shape[0] + event.y) - 2]
    elif currentParameterIndex == 2:
        currentBatch.secondQuestionXY = [int(doCanvas.xview()[0]*doCanvas.original.shape[1] + event.x) - 2,
        int(doCanvas.yview()[0]*doCanvas.original.shape[0] + event.y) - 2]
    else:
        print("Invalid Parameter Index")

    #Showing Point Beside Pick Button
    currentBatch.firstQuestionInfo.config(text="("+str(currentBatch.firstQuestionXY[0])+","+str(currentBatch.firstQuestionXY[1])+")")
    currentBatch.secondOptionInfo.config(text="("+str(currentBatch.secondOptionXY[0])+","+str(currentBatch.secondOptionXY[1])+")")
    currentBatch.secondQuestionInfo.config(text="("+str(currentBatch.secondQuestionXY[0])+","+str(currentBatch.secondQuestionXY[1])+")")

    #Rebinding Everything
    doCanvas.zoomIn.config(state="normal")
    doCanvas.zoomOut.config(state="normal")
    doCanvas.bind("<Button-1>",MouseClick)

    #Changing Mouse Cursor to normal
    doCanvas.config(cursor="arrow")

    #Showing The Pixel They Picked
    showPicks()

def pickPixel(frame,parameterIndex):
    global doCanvas,currentBatch,currentParameterIndex
    
    #Setting CurrentBatch and Current Parameter Index
    currentBatch = frame
    currentParameterIndex = parameterIndex
    displayImage(doCanvas.original,doCanvas,[doCanvas.original.shape[1],doCanvas.original.shape[0]])
    doCanvas.yview_moveto(0)
    doCanvas.xview_moveto(0)
    #Disabling zoom-in and zoom-out for precise pixel choosing
    doCanvas.zoomIn.config(state="disable")
    doCanvas.zoomOut.config(state="disable")

    #Changin Mouse Cursor
    doCanvas.config(cursor="target")

    #unbinding all button functionality
    doCanvas.unbind("<Button-1>")
    doCanvas.unbind("<B1-Motion>")

    #rebinding Mouseclick-1 to another function
    doCanvas.bind("<Button-1>",getPoint)

def addBatch(canvas):
    global batchCount,batchSizeY,root,batchHeight
    canvas.yview_moveto(1)  #Important for New Batch Position
    batchCount += 1         #Keeps count of Total batches

    batchLabelFrame = tk.LabelFrame(canvas,text="Batch " + str(batchCount))
    canvas.create_window((0,batchSizeY),window=batchLabelFrame,anchor="nw",width=300)

        #Configuring Grid
    batchLabelFrame.grid_columnconfigure(0,weight=1)
    batchLabelFrame.grid_columnconfigure(1,weight=1)

        #First MCQ Circle
    firstMCQCircleLabel = tk.Label(batchLabelFrame,text="First Option of First Question : ",wraplength=100)
    firstMCQCircleLabel.grid(row=0,column=0,sticky="e")

    firstMCQPickButton = tk.Button(batchLabelFrame,text="Pick",padx=10,pady=5,command=lambda: pickPixel(batchLabelFrame,0))
    firstMCQPickButton.grid(row=0,column=1,pady=5)

        #Second Option Circle
    secondOptionLabel = tk.Label(batchLabelFrame,text="Second Option of First Question : ",wraplength=100)
    secondOptionLabel.grid(row=1,column=0,sticky="e")

    secondOptionPickButton = tk.Button(batchLabelFrame,text="Pick",padx=10,pady=5,command=lambda: pickPixel(batchLabelFrame,1))
    secondOptionPickButton.grid(row=1,column=1,pady=5)

        #Second Question 1st Circle
    secondQuestionLabel = tk.Label(batchLabelFrame,text="First Option Of Second Question : ",wraplength=100)
    secondQuestionLabel.grid(row=2,column=0,sticky="e")

    secondQuestionButton = tk.Button(batchLabelFrame,text="Pick",padx=10,pady=5,command=lambda: pickPixel(batchLabelFrame,2))
    secondQuestionButton.grid(row=2,column=1,pady=5)

        #Total Options Entry
    totalOptionLabel = tk.Label(batchLabelFrame,text="Total Options : ")
    totalOptionLabel.grid(row=3,column=0,sticky="e")

    batchLabelFrame.totalOptionEntry = tk.Entry(batchLabelFrame)
    batchLabelFrame.totalOptionEntry.bind('<KeyRelease>', showPreview)
    batchLabelFrame.totalOptionEntry.grid(row=3,column=1,columnspan=2)

        #Total MCQ Entry
    totalMCQLabel = tk.Label(batchLabelFrame,text="Total MCQs On Same Y-Axis : ",wraplength=100)
    totalMCQLabel.grid(row=4,column=0,sticky="e")

    batchLabelFrame.totalMCQEntry = tk.Entry(batchLabelFrame)
    batchLabelFrame.totalMCQEntry.bind('<KeyRelease>', showPreview)
    batchLabelFrame.totalMCQEntry.grid(row=4,column=1,columnspan=2)

    #Variable Initialization
    batchLabelFrame.firstQuestionXY = [0,0]
    batchLabelFrame.secondOptionXY = [0,0]
    batchLabelFrame.secondQuestionXY = [0,0]

        #Variable Label Info
    batchLabelFrame.firstQuestionInfo = tk.Label(batchLabelFrame,
    text="("+str(batchLabelFrame.firstQuestionXY[0])+","+str(batchLabelFrame.firstQuestionXY[1])+")")
    batchLabelFrame.firstQuestionInfo.grid(row=0,column=2,sticky="w")
    
    batchLabelFrame.secondOptionInfo = tk.Label(batchLabelFrame,
    text="("+str(batchLabelFrame.secondOptionXY[0])+","+str(batchLabelFrame.secondOptionXY[1])+")")
    batchLabelFrame.secondOptionInfo.grid(row=1,column=2,sticky="w")

    batchLabelFrame.secondQuestionInfo = tk.Label(batchLabelFrame,
    text="("+str(batchLabelFrame.secondQuestionXY[0])+","+str(batchLabelFrame.secondQuestionXY[1])+")")
    batchLabelFrame.secondQuestionInfo.grid(row=2,column=2,sticky="w")

    #Updating Scrollbar,ScrollRegion and Root
    root.update_idletasks()
    if batchHeight <= 0:
        batchHeight = batchLabelFrame.winfo_height()
    batchSizeY += batchHeight
    canvas.config(scrollregion=(0,0,0,0))
    canvas.config(scrollregion=canvas.bbox("all"))
    canvas.yview_moveto(1)

    batches.append(batchLabelFrame)

def deleteBatch(canvas):
    global batchCount,batchSizeY,root,batchHeight
    if (len(batches) > 0):
        canvas.config(scrollregion=(0,0,0,0))
        canvas.config(scrollregion=canvas.bbox("all"))
        batchSizeY -= batchHeight
        batches[len(batches)-1].destroy()
        batches.pop()
        batchCount -= 1
        #Showing Picked Up pixels
        showPicks()

def savePresetToFile(presetNameEntry,presetDescriptionEntry,savePresetWindow):
    name = presetNameEntry.get()
    description = presetDescriptionEntry.get()
    global ce1Slider,ce2Slider,blurSlider,doCanvas
    if(name.find('$') >= 0) or (description.find('$') >= 0):
        tkMessageBox.showerror("No Symbols","Please do not use '$' symbols in Preset Name or Description.")
        savePresetWindow.destroy()
    elif (len(batches) <= 0):
        tkMessageBox.showerror("No Batches","Preset must have atleast 1 batch.")
        savePresetWindow.destroy()
    elif(len(name) <= 0):
        tkMessageBox.showerror("No Name","Preset must have a name.")
        savePresetWindow.destroy()
    else:
        buffer = ""
        buffer += str(name) + "$" + str(description) + "$"  #Saving Name & Description
        buffer += "[" + str(doCanvas.original.shape[1]) + "," + str(doCanvas.original.shape[0]) + "]" + "$" #Saving Actual OMR Size
        buffer += str(ce1Slider.get()) + "$"    #CE Parameter 1
        buffer += str(ce2Slider.get()) + "$"    #CE Parameter 2
        buffer += str(blurSlider.get()) + "$"   #Blur Parameter
        buffer += str(len(batches)) + "$"       #Total Number of Batches

        try:
            for batch in batches:
                fx = batch.firstQuestionXY[0]
                fy = batch.firstQuestionXY[1]
                dx = batch.secondOptionXY[0] - fx
                dy = batch.secondQuestionXY[1] - fy
                buffer += "["
                buffer += str(abs(int(batch.totalOptionEntry.get()))) + ","  #Total Options
                buffer += str(abs(int(batch.totalMCQEntry.get()))) + ","     #Total MCQS In Single Batch
                buffer += str(fx) + "," + str(fy) + ","                 #First-X and First-Y
                buffer += str(dx) + "," + str(dy) + "]$"                #X Difference and Y Difference

            with open(".presets","a+") as f:
                f.write(buffer + "\n")
            savePresetWindow.destroy()
            tkMessageBox.showinfo("Success","Preset Saved Successfuly And Ready to use")
        except Exception as e:
            savePresetWindow.destroy()
            tkMessageBox.showerror("Error","Invalid datatype entered in some input box. Please check input fields and only enter integer value")
            print(e)

def savePreset(event):
    def cancelSaving():
        savePresetWindow.destroy()
    
    savePresetWindow = tk.Tk()
    savePresetWindow.title("Save Preset")
    savePresetWindow.geometry("300x100+150+150")
    savePresetWindow.grid_rowconfigure(0,weight=1)
    savePresetWindow.grid_rowconfigure(1,weight=1)
    savePresetWindow.grid_columnconfigure(0,weight=1)
    savePresetWindow.grid_columnconfigure(1,weight=1)
    savePresetWindow.resizable(False,False)

    presetNameLabel = tk.Label(savePresetWindow,text="Name : ")
    presetNameLabel.grid(row=0,column=0,padx=5,pady=5,sticky="w")

    presetNameEntry = tk.Entry(savePresetWindow)
    presetNameEntry.grid(row=0,column=1,padx=5,pady=5,sticky="nwes")

    presetDescriptionLabel = tk.Label(savePresetWindow,text="Description : ")
    presetDescriptionLabel.grid(row=1,column=0,padx=5,pady=5,sticky="w")

    presetDescriptionEntry = tk.Entry(savePresetWindow)
    presetDescriptionEntry.grid(row=1,column=1,padx=5,pady=5,sticky="nwes")

    #Save Button
    savePresetButton = tk.Button(savePresetWindow,text="Save",command=lambda : savePresetToFile(presetNameEntry,presetDescriptionEntry,savePresetWindow))
    savePresetButton.grid(row=2,column=0,sticky="nwes",padx=5,pady=5)

    #Cancel Button
    cancelPresetButton = tk.Button(savePresetWindow,text="Cancel",command=cancelSaving)
    cancelPresetButton.grid(row=2,column=1,sticky="nwes",padx=5,pady=5)

    savePresetWindow.focus_force()
    savePresetWindow.mainloop()

def resetPreset():
    global ce1Slider,ce2Slider,blurSlider,batchesCanvas
    ce1Slider.set(70)
    ce2Slider.set(20)
    blurSlider.set(17)

    applySettings(ce1Slider.get(),ce2Slider.get(),blurSlider.get(),0,gImage)
    while(len(batches) > 0):
        deleteBatch(batchesCanvas)

def main(img):
    global root,ogCanvas,doCanvas,gImage,ce1Slider,ce2Slider,blurSlider,batchesCanvas
    gImage = img
    root = tk.Tk()
    root.title("Preset Builder")
    root.geometry("1200x600+50+50")
    root.focus_force()

    root.grid_columnconfigure(0,weight=2)
    root.grid_columnconfigure(1,weight=6)
    root.grid_columnconfigure(2,weight=6)
    root.grid_rowconfigure(0,weight=1)

    #------------------------ Preset Menu Bar
    menubar = tk.Menu(root)
    #file menu
    presetMenu = tk.Menu(menubar,tearoff=0)
    presetMenu.add_command(label="Save Preset",command=lambda : savePreset(1))
    presetMenu.add_command(label="Reset To Default",command=resetPreset)
    menubar.add_cascade(label="Preset",menu=presetMenu)
    root.config(menu=menubar)

    #--------------- Setting Tab
    settingFrame = tk.LabelFrame(root,text="Settings",padx=5,pady=5)
    settingFrame.grid(row=0,column=0,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5)
        #UI Configuration
    settingFrame.grid_columnconfigure(0,weight=1)
    settingFrame.grid_columnconfigure(1,weight=1)
    settingFrame.grid_columnconfigure(2,weight=1)
    settingFrame.grid_columnconfigure(3,weight=1)
        #----- Setting Tab UI
    edgeDetectionLabel = tk.Label(settingFrame,text="Edge Detection Parameters :")
    edgeDetectionLabel.grid(row=0,column=0,columnspan=4,sticky="nw")

        #Canny Edge Value 1 Label+Slider
    ce1Label = tk.Label(settingFrame,text="Parameter 1") 
    ce1Label.grid(row=1,column=0,sticky="nwes")           

    ce1SliderValue = tk.IntVar()
    ce1Slider = tk.Scale(settingFrame,from_=0,to=120,orient=tk.HORIZONTAL,variable=ce1SliderValue,showvalue=0)
    ce1Slider.set(70)
    ce1Slider.grid(row=1,column=1,columnspan=2,sticky="nwes")

    ce1SliderValueLabel = tk.Label(settingFrame,textvariable=ce1SliderValue)
    ce1SliderValueLabel.grid(row=1,column=3)

        #Canny Edge Value 2 Label+Slider
    ce2Label = tk.Label(settingFrame,text="Parameter 2") 
    ce2Label.grid(row=2,column=0,sticky="nwes")           

    ce2SliderValue = tk.IntVar()
    ce2Slider = tk.Scale(settingFrame,from_=0,to=120,orient=tk.HORIZONTAL,variable=ce2SliderValue,showvalue=0)
    ce2Slider.set(20)
    ce2Slider.grid(row=2,column=1,columnspan=2,sticky="nwes")

    ce2SliderValueLabel = tk.Label(settingFrame,textvariable=ce2SliderValue)
    ce2SliderValueLabel.grid(row=2,column=3)

        #Blur Label+Slider
    blurLabel = tk.Label(settingFrame,text="Blur") 
    blurLabel.grid(row=3,column=0,sticky="nwes")           

    blurSliderValue = tk.IntVar()
    blurSlider = tk.Scale(settingFrame,from_=1,to=50,orient=tk.HORIZONTAL,variable=blurSliderValue,showvalue=0)
    blurSlider.set(17)
    blurSlider.grid(row=3,column=1,columnspan=2,sticky="nwes")

    blurSliderValueLabel = tk.Label(settingFrame,textvariable=blurSliderValue)
    blurSliderValueLabel.grid(row=3,column=3)

        #Apply button
    applyButton = tk.Button(settingFrame,text="Apply")
    applyButton.grid(row=4,column=0,columnspan=2,sticky="nwes")

        #Check Box For Preview
    previewValue = tk.IntVar()
    previewCheckbox = tk.Checkbutton(settingFrame,text="Preview",variable=previewValue,onvalue=1,offvalue=0)
    previewCheckbox.grid(row=4,column=2,columnspan=2,sticky="nwes")

        #Apply Button Command
    applyButton.configure(command= lambda : applySettings(ce1SliderValue.get(),ce2SliderValue.get(),blurSliderValue.get(),previewValue.get(),img))

    empty = tk.Label(settingFrame,text="_____________________________________________")      #For Empty Row Insert
    empty.grid(row=5,column=0,columnspan=4)

        #----- Batches
    mainBatchLabel = tk.Label(settingFrame,text="Batches : ")
    mainBatchLabel.grid(row=6,column=0,columnspan=2)

    addBatchButton = tk.Button(settingFrame,text="Add")
    addBatchButton.grid(row=6,column=2,sticky="nwes",padx=5,pady=5)

    deleteBatchButton = tk.Button(settingFrame,text="Delete")
    deleteBatchButton.grid(row=6,column=3,sticky="nwes",padx=5,pady=5)

        #Batches canvas
    settingFrame.grid_rowconfigure(7,weight=1)  #Configure
    
    batchesCanvas = tk.Canvas(settingFrame)
    batchesCanvas.grid(row=7,column=0,columnspan=4,sticky="nwes")

    bindScrollbar(batchesCanvas)    #Binding Scrollbars

    addBatchButton.configure(command=lambda:addBatch(batchesCanvas))
    deleteBatchButton.configure(command=lambda:deleteBatch(batchesCanvas))

    #--------------- Detected OMR Frame
    doImgFrame = tk.LabelFrame(root,text="Detected OMR")
    doImgFrame.grid(row=0,column=1,sticky=tk.N+tk.S+tk.E+tk.W,padx=3,pady=5)
        #building doCanvas
    doCanvas = tk.Canvas(doImgFrame,height=200,width=200,scrollregion=(0,0,500,800))    #Canvas For Detected OMR
    bindScrollbar(doCanvas)                                 #Binding Scrollbars
    doCanvas.pack(expand=1,fill=tk.BOTH)                    #Packing Canvas

    #--------------- Original Image Frame
    ogImgFrame = tk.LabelFrame(root,text="Original Image")
    ogImgFrame.grid(row=0,column=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=3,pady=5)
        #building ogCanvas
    ogCanvas = tk.Canvas(ogImgFrame,height=200,width=200,scrollregion=(0,0,500,800))  #Canvas For Image
    bindScrollbar(ogCanvas)                             #Binding Scrollbars
    ogCanvas.pack(expand=1,fill=tk.BOTH)                #Packing Canvas


    #Main Image Processing
    displayImage(img,ogCanvas,[img.shape[1],img.shape[0]])
    handleDetection(img,doCanvas)

    #Binding Zooms
    bindZooms(ogCanvas)
    bindZooms(doCanvas)

    #Binding Functionality
    ogCanvas.bind("<Button-1>", MouseClick)
    doCanvas.bind("<Button-1>", MouseClick)
    root.bind("<Control-s>",savePreset)
    
    #Casual Stuff
    root.protocol('WM_DELETE_WINDOW', deletetemp)
    root.mainloop()

if __name__ == "__main__":
    main()