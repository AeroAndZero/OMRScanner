import cv2
import numpy as np
import circleProcessor
import random
red = [10,10,255]
blue = [255,10,10]
green = [10,255,10]
yellow = [0,255,255]
answerKeyTextFile = 0

def mapp(h):
        h = h.reshape((4,2))
        hnew = np.zeros((4,2),dtype = np.float32)

        add = h.sum(1)
        hnew[0] = h[np.argmin(add)]
        hnew[2] = h[np.argmax(add)]

        diff = np.diff(h,axis = 1)
        hnew[1] = h[np.argmin(diff)]
        hnew[3] = h[np.argmax(diff)]

        return hnew

def findCorners(omr0,cp1=70,cp2=20,bp=17):
    h = omr0.shape[0]
    w = omr0.shape[1]
    xdownscale = float(500)/float(w)
    ydownscale = float(500)/float(h)

    copy = np.copy(omr0)
    omr0 = cv2.resize(omr0,(int(w*xdownscale),int(h*ydownscale)))
    
    omr0_blur = cv2.GaussianBlur(omr0,(bp,bp),0)

    omr0_canny = cv2.Canny(omr0_blur,cp1,cp2)

    contours, hierarchy = cv2.findContours(omr0_canny,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)

    cv2.drawContours(omr0, contours, -1, (0,255,0), 3)
    maxArea = 0
    maxContour = contours[0]
    perimulti = 0.01
    for i in range(0,len(contours)):
        area = cv2.contourArea(contours[i])
        if area == (omr0.shape[0]-1)*(omr0.shape[1]-1):
            continue

        temp_peri = cv2.arcLength(contours[i],True)
        temp_approx = cv2.approxPolyDP(contours[i],perimulti*temp_peri,True)

        if area > maxArea and len(temp_approx) == 4:
            maxArea = area
            maxContour = contours[i]
            maxContourIndex = i

    peri = cv2.arcLength(maxContour,True)
    approx = cv2.approxPolyDP(maxContour,perimulti*peri,True)

    corners = mapp(approx)
    for corner in corners:
        corner[0] = int(w*corner[0]/500)
        corner[1] = int(h*corner[1]/500)
        #cv2.circle(copy,(corner[0],corner[1]),2,(0,0,255),7)
    

    wscale = abs(max(corners[0][0] - corners[1][0],corners[2][0] - corners[3][0]))
    hscale = abs(max(corners[0][1] - corners[2][1],corners[1][1] - corners[3][1]))
    
    dst = np.array([
            [0, 0],
            [wscale - 1, 0],
            [wscale - 1, hscale - 1],
            [0, hscale - 1]], dtype = "float32")

    M = cv2.getPerspectiveTransform(corners,dst)
    wrapped = cv2.warpPerspective(copy, M, (wscale, hscale))
    return wrapped

def scanOmr(image,actualSize = [],init = [],diff = [],resize = [],totalMCQs = 10,totalOptions = 4,showDots = False, method=0,InkThreshold = 120):
    #Debug
    print(InkThreshold+10)
    #some parameters
    safeToScan = False
    actualw = actualSize[0]
    actualh = actualSize[1]
    fx = init[0]
    fy = init[1]
    dx = diff[0]
    dy = diff[1]

    # 0: total scanned, 1: correct MCQs, 2 : wrong mcqs
    optionTicked = []

    if (method == 0):   #----------------- Simple Scanning Algorithm
        resizew = resize[0]
        resizeh = resize[1]

        dx = int((dx*resizew)/actualw)
        dy = int((dy*resizeh)/actualh)
        fx = int((fx*resizew)/actualw)
        fy = int((fy*resizeh)/actualh)

        image= cv2.resize(image,(resizew,resizeh))

        for y in range(fy,fy+(dy*totalMCQs),dy):
            
            optionTicked.append(0)
            for x in range(fx,fx+(dx*totalOptions),dx):
                
                if (image[y,x][0] < InkThreshold) and (image[y,x][1] < InkThreshold) and (image[y,x][2] < InkThreshold):
                    print("Low inkThreshold found")
                    
                    #Question Number : int(y/dy)
                    #Option Number : int(x/dx)+1

                    cv2.circle(image,(x,y),15,yellow,50)

                    if optionTicked[len(optionTicked)-1] == 0:
                        optionTicked[len(optionTicked)-1] += int(x/dx)+1
                    else :
                        optionTicked[len(optionTicked)-1] += 69

                else:
                    cv2.circle(image,(x,y),15,blue,50)

                
        
        image = cv2.resize(image,(actualSize[0],actualSize[1]))
        return image, optionTicked

    elif (method == 1): #----------------- Circle Detection and Dynamic Difference Algorithm
        image = cv2.resize(image,(actualSize[0],actualSize[1]))
        fx,fy = circleProcessor.findClosestCircle(image,fx,fy,int(dx/2))
        PointHistoryX = [fx]
        PointHistoryY = [fy]
        
        try:
            for mcq in range(totalMCQs):
                y = circleProcessor.findClosestCircle(image,PointHistoryX[0],PointHistoryY[0]+dy,int(dy/2))[1]
                
                PointHistoryX = [fx]

                optionTicked.append(0)
                
                for option in range(totalOptions):
                    x = circleProcessor.findClosestCircle(image,PointHistoryX[0]+dx,PointHistoryY[0],int(dx/2))[0]
                    #Scanning Here
                    xForScan = PointHistoryX[0]
                    yForScan = PointHistoryY[0]

                    #----------- Scanning
                    if (image[yForScan,xForScan][0] < InkThreshold) and (image[yForScan,xForScan][1] < InkThreshold) and (image[yForScan,xForScan][2] < InkThreshold):
                        print("Low inkThreshold found")
                    
                        #Question Number : int(y/dy)
                        #Option Number : int(x/dx)+1

                        cv2.circle(image,(xForScan,yForScan),1,yellow,2)

                        if optionTicked[len(optionTicked)-1] == 0:
                            optionTicked[len(optionTicked)-1] += option+1
                        else :
                            optionTicked[len(optionTicked)-1] += 69

                    else:
                        cv2.circle(image,(xForScan,yForScan),1,blue,2)

                    #Keeping Data Short
                    PointHistoryX.insert(0,x)
                    dx = abs(PointHistoryX[0] - PointHistoryX[1])    #Dynamic Difference
                    PointHistoryX.pop()

                PointHistoryY.insert(0,y)
                dy = abs(PointHistoryY[0] - PointHistoryY[1])
                PointHistoryY.pop()
             
        except Exception as e:
            print(e)
        
        return image, optionTicked

    else:
        print("Invalid Method Provided.")
        return 0


def main():
    omr = cv2.imread("images/img_3.jpg")
    found_omr = findCorners(omr)
    answers = scanOmr(found_omr,[278,503],[27,24],[32,24],[278,503],20,4,True)
    cv2.imshow("AOSv2 1",omr)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
