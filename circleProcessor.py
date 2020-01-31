'''
best circle detection parameters found yet :
cv2.HoughCircles(smallImage_blur_gray, cv2.HOUGH_GRADIENT, 1.5, hcDistant,param1=100,param2=20)
'''
import cv2
import numpy as np
import math
show = 0

def cropImage(image,refX,refY):
    limitX = int((image.shape[1] * 0.05))
    limitY = int((image.shape[0] * 0.05))
    rightX = 0
    leftX = 0
    upY = 0
    downY = 0

    while (rightX + refX < image.shape[1]) and (rightX < limitX):
        rightX += 1
    
    while (refX - leftX > 0) and (leftX < limitX):
        leftX += 1
    
    while (refY + downY < image.shape[0]) and (downY < limitY):
        downY += 1
    
    while (refY - upY > 0) and (upY < limitY):
        upY += 1
    
    croppedImage = image[(refY-upY):(refY+downY),(refX-leftX):(refX+rightX)]
    return croppedImage

def distants(x1,x2,y1,y2):
    dis = math.sqrt((x2-x1)*(x2-x1) + (y2-y1)*(y2-y1))
    return dis

def findClosestCircle(image,refX,refY,hcDistant):
    minInit = 0
    smallImage = cropImage(image,refX,refY)
    #smallImage_blur = cv2.GaussianBlur(smallImage,(1,1),1)
    smallImage_blur_gray = cv2.cvtColor(smallImage,cv2.COLOR_BGR2GRAY)
    
    newX = int(smallImage.shape[1]/2)
    newY = int(smallImage.shape[0]/2)
    diffX = refX - newX
    diffY = refY - newY

    circles = cv2.HoughCircles(smallImage_blur_gray, cv2.HOUGH_GRADIENT, 1.5, hcDistant,param1=100,param2=20)

    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")

        minDistantXY = [circles[0][0],circles[0][1]]
        for (x, y, r) in circles:
            if show:  #Debugging
                cv2.circle(smallImage,(x,y),1,(0,0,255),2) 

            if distants(x,newX,y,newY) <= distants(minDistantXY[0],newX,minDistantXY[1],newY):
                minDistantXY = [x,y]
        
        newX = minDistantXY[0]
        newY = minDistantXY[1]

    finalX = newX + diffX
    finalY = newY + diffY

    '''For Debugging '''
    if show:
        cv2.circle(smallImage,(newX,newY),2,(0,255,0),3)
        cv2.imshow("Lo",smallImage)
        cv2.waitKey(0)

    return [finalX,finalY]

if __name__ == "__main__":
    image = cv2.imread("images/croppedOMR7-ticked.jpg")
    show = 1
    findClosestCircle(image,401,714,1)