import cv2
import numpy
# First Pixel : 93,284
# X Diff : 22
# Y Diff : 17
# Image Size : 827 x 1169
imgX = 827
imgY = 1169
omr = cv2.imread("OMRSheet1Filled.png")
omr = cv2.resize(omr,(imgX,imgY+2))
firstX = X = 93
firstY = Y = 284
Yplaces = [284,450,617,784,950]
Xdiff = 20
Ydiff = 17
downscale = 2
resizeX = imgX / downscale
resizeY = imgY / downscale
question = 1
for k in range(5):
    Y = Yplaces[k]
    for i in range(10):
        X = firstX
        for j in range(4):
            if numpy.all(omr[Y,X] <= [150,150,150]):
                cv2.circle(omr,(X,Y),1,(50,50,250),3)
                print("Question : " + str(question)+", Answer Ticked : " + str(j+1))
            X += Xdiff
        Y += Ydiff
        question += 1

cv2.imshow("OMR Sheet",omr)
resizedImg = cv2.resize(omr,(int(resizeX),int(resizeY)))
cv2.imshow("Downscaled Image",resizedImg)
cv2.waitKey(0)
cv2.destroyAllWindows