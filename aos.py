import cv2
import numpy as np

def findCorners(omr0,resize = []):
    minOMRColor = 200
    omr0_gray = cv2.cvtColor(omr0,cv2.COLOR_BGR2GRAY)
    ret, omr0_threshold = cv2.threshold(omr0_gray,minOMRColor,255,0)
    omr0_canny = cv2.Canny(omr0_threshold,50,20)

    contours, hierarchy = cv2.findContours(omr0_threshold,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)

    max = 0
    for i in range(0,len(contours)):
        area = cv2.contourArea(contours[i])
        if area == (omr0.shape[0]-1)*(omr0.shape[1]-1):
            continue

        temp_peri = cv2.arcLength(contours[i],True)
        temp_approx = cv2.approxPolyDP(contours[i],0.02*temp_peri,True)

        if area > max and len(temp_approx) == 4:
            max = area
            maxContour = contours[i]
            maxContourIndex = i

    peri = cv2.arcLength(maxContour,True)
    approx = cv2.approxPolyDP(maxContour,0.02*peri,True)

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

    corners = mapp(approx)

    wscale = resize[0]
    hscale = resize[1]
    dst = np.array([
            [0, 0],
            [wscale - 1, 0],
            [wscale - 1, hscale - 1],
            [0, hscale - 1]], dtype = "float32")

    M = cv2.getPerspectiveTransform(corners,dst)
    wrapped = cv2.warpPerspective(omr0, M, (wscale, hscale))
    return wrapped

def scanOmr(image,actualSize = [],init = [],diff = [],resize = [],totalMCQs = 10,totalOptions = 4,showDots = False):
    i = 0
    answers = []
    #some parameters
    InkThreshold = 100
    red = [10,10,255]
    actualw = actualSize[0]
    actualh = actualSize[1]
    fx = init[0]
    fy = init[1]
    dx = diff[0]
    dy = diff[1]
    resizew = resize[0]
    resizeh = resize[1]

    dx = int((dx*resizew)/actualw)
    dy = int((dy*resizeh)/actualh)
    fx = int((fx*resizew)/actualw)
    fy = int((fy*resizeh)/actualh)

    for y in range(fy,fy+(dy*totalMCQs),dy):
        answerticked = 0
        for x in range(fx,fx+(dx*totalOptions),dx):
            if np.all(image[y,x] < InkThreshold):
                #print("Question : "+str(int(y/dy))+", Answered Ticked : " + str(int(x/dx)+1))
                answers.append(int(x/dx)+1)
                i += 1
                answerticked = 1
                if showDots:
                    cv2.circle(image,(x,y),int(0.1*dx),red,int(0.05*dx))
                continue
        if answerticked == 0:
            answers.append(0)

    return answers

def main():
    #orig = cv2.imread("images/RealLifeOMR2.jpg")
    omr = cv2.imread("images/croppedOMR7-ticked.jpg")#cv2.resize(orig,(720,1280))
    cv2.imshow("AOSv2 1",omr)
    
    #Keep the resize amount large for better and accurate scanning
    found_omr = findCorners(omr,[5000,5000])
    answers = scanOmr(found_omr,[278,503],[27,24],[32,24],[5000,5000],20,4,True)

    cv2.imshow("AOSv2 2",cv2.resize(found_omr,(500,500)))
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()