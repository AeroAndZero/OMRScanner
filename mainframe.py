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
answerKeyFilepath = 0
gDetected = 0

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
    global resultFrame,gDetected
    #Reading The File
    ftype = [('JPEG','*.jpg'),('PNG','*.png')]
    dlg = tkFileDialog.Open(filetypes = ftype)
    fp = dlg.show()     #Gives path of the open file
    if fp == '':
        return
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
        gDetected = img_fc
        displayImage(img_fc,doCanvas,[img_fc.shape[1],img_fc.shape[0]])
        handleScanning(img_fc)
    except Exception as e:
        tkMessageBox.showerror("Error","No OMR was detected or scanning algorithm didn't work. Try again...")
        print(e)

def openAnswerKey():
    global answerKeyFilepath,resultFrame
    ftype = [('TXT','*.txt')]
    dlg = tkFileDialog.Open(filetypes = ftype)
    fp = dlg.show()     #Gives path of the open file
    fn = filename(fp)   #Returns File Name
    if fp != '':
        answerKeyFilepath = fp
        resultFrame.currentAnswerKey.config(text=str(fn))
        resultFrame.scanButton.config(state="normal")
        print(fp)

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
    global doCanvas,resultFrame

    scannedImage = img
    answers = []
    finalRawResult = []
    simplifiedResult = []
    totalQuestions = 0
    try:
        inkThreshold = abs(int(resultFrame.inkThreshold.get()))
    except:
        tkMessageBox.showerror("Error","Only enter integer value in InkThreshold")
        inkThreshold = 120
    
    # 0 : Total Scanned, 1 : Correct MCQs, 2 : Wrong MCQs, 3 : Total Marks
    marks = [0,0,0,0]

    #Points for right and wrong
    pointForCorrect = 1
    pointForWrong = 0

    #Finding Out Total Questions In The WHOLE omr
    for batch in batches:
        totalQuestions += batch[1]

    print(totalQuestions)

    #Loading Answers
    try:
        with open(answerKeyFilepath,'a+') as f:
            for line in f:
                answers.append(int(line[0]))
        print("Read Answers And Appended")
        
        if len(answers) != totalQuestions:
            print("File doesn't have answers to every mcq. Appending with 0s")
            tkMessageBox.showwarning("Warning","Answer key that is attached doesn't have answer to every question.")
        
        while(len(answers) < totalQuestions):
            answers.append(0)
        
        safeToScan = True
    
    except Exception as e:
        safeToScan = False
        print("\nFile Corrupted.")
        print(str(e) + "\n")

    #Scanning Batches
    for batch in batches:
        print("Batch in scan : " + str(batch))
        print("Fx : " + str(batch[2]))
        
        scannedImage, batchResult = aos.scanOmr(scannedImage,actualSize=actualSize,init=[batch[2],batch[3]],diff=[batch[4],batch[5]],resize=[5000,5000]
        ,totalMCQs=batch[1],totalOptions=batch[0],showDots=True,method=method,InkThreshold = inkThreshold) 
        
        finalRawResult.append(batchResult)

    displayImage(scannedImage,doCanvas,[scannedImage.shape[1],scannedImage.shape[0]])

    print("final result : " + str(finalRawResult))

    #Simplifying answers into simple array
    for batchResult in finalRawResult:
        for option in batchResult:
            simplifiedResult.append(option)

    print("Simplified result : " + str(simplifiedResult))
    print("Answers From File : " + str(answers))

    #Result Calculations
    try:
        pointForCorrect = abs(float(resultFrame.pointForCorrect.get()))
        pointForWrong = abs(float(resultFrame.pointForWrong.get()))
    except:
        tkMessageBox.showerror("Error","Please Enter only numbers in Point for correct & wrong input fields.")

    if safeToScan:
        for question in range(len(simplifiedResult)):
            marks[0] += 1
            if simplifiedResult[question] == answers[question]:
                marks[1] += 1
                marks[3] += pointForCorrect
            else:
                marks[2] += 1
                marks[3] -= pointForWrong
        
        resultFrame.totalScannedMCQs.config(text=str(marks[0]))
        resultFrame.correctMCQs.config(text=str(marks[1]))
        resultFrame.wrongMCQs.config(text=str(marks[2]))
        resultFrame.totalMarks.config(text=str(marks[3]) + "/" + str(marks[0] * pointForCorrect))
        precentage = float(marks[3]) / float(marks[0] * pointForCorrect) * float(100)
        resultFrame.totalPercentage.config(text=str(precentage) + " %")

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
    global ogImgFrame,doImgFrame,ogCanvas,doCanvas,root,titleWithPreset,resultFrame

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
    resultFrame = tk.LabelFrame(root,text="Result")
    resultFrame.grid(row=0,column=2,sticky=tk.N+tk.S+tk.E+tk.W,padx=5,pady=5)

    resultFrame.grid_columnconfigure(0,weight=1)
    resultFrame.grid_columnconfigure(1,weight=1)
    resultFrame.grid_columnconfigure(2,weight=1)
    resultFrame.grid_columnconfigure(3,weight=1)

    #Showing Attached Answer Key
    answerKeyLabel = tk.Label(resultFrame,text="Answer Key : ")
    answerKeyLabel.grid(row=0,column=0,sticky="e")

    resultFrame.currentAnswerKey = tk.Label(resultFrame,text="No Answer Key Attached [!]")
    resultFrame.currentAnswerKey.grid(row=0,column=1,columnspan=3,sticky="w")

    openAnswerKeyButton = tk.Button(resultFrame,text="Open\nAnswer Key",command = openAnswerKey)
    openAnswerKeyButton.grid(row=1,column=0,columnspan=2,pady=5,padx=5,sticky="nwes")

    resultFrame.scanButton = tk.Button(resultFrame,text="Re-Scan",command = lambda : handleScanning(gDetected))
    resultFrame.scanButton.config(state="disabled")
    resultFrame.scanButton.grid(row=1,column=2,columnspan=2,pady=5,padx=5,sticky="nwes")

    #Empty Label for separation
    emptyLabel = tk.Label(resultFrame,text="").grid(row=2,column=0,columnspan=4)
    emptyLabel = tk.Label(resultFrame,text="").grid(row=3,column=0,columnspan=4)

    #Taking Input for correct and incorrect mcq points
    
        #For Correct
    point4CorrectLabel = tk.Label(resultFrame,text="Point For Correct Answer :",wraplength=100)
    point4CorrectLabel.grid(row=4,column=0,columnspan=2,sticky="e",padx=5)

    resultFrame.pointForCorrect = tk.Entry(resultFrame)
    resultFrame.pointForCorrect.insert(tk.END, 1)
    resultFrame.pointForCorrect.grid(row=4,column=2,columnspan=2,padx=5,pady=5)

        #For Incorrect
    point4WrongLabel = tk.Label(resultFrame,text="Point For Wrong Answer : ",wraplength=100)
    point4WrongLabel.grid(row=5,column=0,columnspan=2,sticky="e",padx=5)

    resultFrame.pointForWrong = tk.Entry(resultFrame)
    resultFrame.pointForWrong.insert(tk.END, 0)
    resultFrame.pointForWrong.grid(row=5,column=2,columnspan=2,padx=5,pady=5)

    #Empty Label..... Again
    emptyLabel = tk.Label(resultFrame,text="").grid(row=6,column=0,columnspan=4)

    #For Showing Total Scanned MCQs
    totalMCQsScannedLabel = tk.Label(resultFrame,text="Total MCQs\nScanned : ")
    totalMCQsScannedLabel.grid(row=7,column=0,columnspan=2,sticky="e")

    resultFrame.totalScannedMCQs = tk.Label(resultFrame,text="0")
    resultFrame.totalScannedMCQs.grid(row=7,column=2,columnspan=2)

    #Showing Correct MCQS
    correctMCQsLabel = tk.Label(resultFrame,text="Correct MCQs : ")
    correctMCQsLabel.grid(row=8,column=0,columnspan=2,sticky="e")

    resultFrame.correctMCQs = tk.Label(resultFrame,text="0")
    resultFrame.correctMCQs.grid(row=8,column=2,columnspan=2)

    #Showing Wrong MCQs
    wrongMCQsLabel = tk.Label(resultFrame,text="Wrong MCQs : ")
    wrongMCQsLabel.grid(row=9,column=0,columnspan=2,sticky="e")

    resultFrame.wrongMCQs = tk.Label(resultFrame,text="0")
    resultFrame.wrongMCQs.grid(row=9,column=2,columnspan=2)

    #Separator
    separatorLabel = tk.Label(resultFrame,text="----------------------------")
    separatorLabel.grid(row=10,column=0,columnspan=4)

    #Showing Total Marks
    totalMarksLabel = tk.Label(resultFrame,text="Total Marks : ")
    totalMarksLabel.grid(row=11,column=0,columnspan=2,sticky="e")

    resultFrame.totalMarks = tk.Label(resultFrame,text="0")
    resultFrame.totalMarks.grid(row=11,column=2,columnspan=2)

    #Showing Percentage
    percentageLabel = tk.Label(resultFrame,text="Percentage : ")
    percentageLabel.grid(row=12,column=0,columnspan=2,sticky="e")

    resultFrame.totalPercentage = tk.Label(resultFrame,text="0 %")
    resultFrame.totalPercentage.grid(row=12,column=2,columnspan=2)

    #For InkThreshold
    inkThresholdlabel = tk.Label(resultFrame,text="Ink Threshold\n(Between 0 to 255) : ")
    inkThresholdlabel.grid(row=13,column=0,columnspan=2,sticky="e",pady=15)

    resultFrame.inkThreshold = tk.Entry(resultFrame)
    resultFrame.inkThreshold.insert(tk.END, 120)
    resultFrame.inkThreshold.grid(row=13,column=2,columnspan=2,sticky="w",pady=15)

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