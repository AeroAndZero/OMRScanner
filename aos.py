import cv2
import numpy as np

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

def findCorners(omr0,resize = []):
    copy = np.copy(omr0)
    blank = np.zeros((omr0.shape[0],omr0.shape[1],3), np.uint8)
    
    omr0_blur = cv2.GaussianBlur(omr0,(17,17),0)

    omr0_canny = cv2.Canny(omr0_blur,70,20)
    cv2.imshow("Canny",omr0_canny)

    contours, hierarchy = cv2.findContours(omr0_canny,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)

    cv2.drawContours(omr0, contours, -1, (0,255,0), 3)
    max = 0
    maxContour = contours[0]
    perimulti = 0.01
    for i in range(0,len(contours)):
        area = cv2.contourArea(contours[i])
        if area == (omr0.shape[0]-1)*(omr0.shape[1]-1):
            continue

        temp_peri = cv2.arcLength(contours[i],True)
        temp_approx = cv2.approxPolyDP(contours[i],perimulti*temp_peri,True)

        if area > max and len(temp_approx) == 4:
            max = area
            maxContour = contours[i]
            maxContourIndex = i

    peri = cv2.arcLength(maxContour,True)
    approx = cv2.approxPolyDP(maxContour,perimulti*peri,True)

    corners = mapp(approx)
    for corner in corners:
        cv2.circle(omr0,(corner[0],corner[1]),2,(0,0,255),7)

    wscale = resize[0]
    hscale = resize[1]
    dst = np.array([
            [0, 0],
            [wscale - 1, 0],
            [wscale - 1, hscale - 1],
            [0, hscale - 1]], dtype = "float32")

    M = cv2.getPerspectiveTransform(corners,dst)
    wrapped = cv2.warpPerspective(copy, M, (wscale, hscale))
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
    omr = cv2.imread("images/img_2.jpg")#cv2.resize(orig,(720,1280))
    omr = cv2.resize(omr,(500,500))#(int(omr.shape[1]/2),int(omr.shape[0]/2)))
    #Keep the resize amount large for better and accurate scanning
    try:
        found_omr = findCorners(omr,[5000,5000])
        #answers = scanOmr(found_omr,[278,503],[27,24],[32,24],[5000,5000],20,4,True)
        cv2.imshow("Detected",cv2.resize(found_omr,(500,500)))
    except:
        print("Something went wrong")
    cv2.imshow("AOSv2 1",omr)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
