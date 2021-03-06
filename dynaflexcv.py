# -*- coding: utf-8 -*-


   
def click_event(event, x, y, flags, param):
    '''
    get current mouse cordinates by left-clicking
    from http://www.acgeospatial.co.uk/interaction-opencv-python/
    '''
    if event == cv2.EVENT_LBUTTONDOWN:
        print ('X-coordinate:', x, ' Y-coordinate:', y)
        


def findNextPoint(sX, sY, sAngle, dist, thresholding, dAngleInc, limAngle, width, height):
    '''
    This function searches for white pixels at defined distances and if found return the position
    
    Input:
    
    sX - X coordinate of starting point
    sY - Y coordinate of starting point
    sAngle - Angle (in degree) to start searching 
    dist - distance (in pixels) at which search is being conducted    
    thresholding - Input image
    dAngleInc - angle increment (in degrees)
    limAngle - limit of search angle (in degrees)
    width - width of each frame (in px)
    height - height of each frame (in px)
        
    Output:
    
    fP - reports if white pixel is found (= 1)  
    eX - X coordinate of white pixel found
    eY - Y coordinate of white pixel found
    eAngle - angle at which the white pixel was found 
    l - absolute length to white pixel found
        
    '''
    i = 0
    dAngle = 0

    while dAngle <= limAngle and dAngle >= -limAngle :          #modify this for more/less accuracy 
        if i != 0 and i % 2 == 0 :
            dAngle = dAngle + dAngleInc
        #switch from negative to positive at each iteration:
        if i % 2 == 0 :
            absdAngle = -dAngle
        else :
            absdAngle = dAngle
        out = 0 #indicates wether the resulting vector is out of bounds (=1)        
        eAngleRad = (sAngle + absdAngle)* np.pi / 180  #convert to radiant
        #calculate (and round) the dist in px in x,Y direction:
        dX = np.sin(eAngleRad) * dist 
        dY = np.cos(eAngleRad) * dist
        dX = np.around(dX) #round x
        dY = np.around(dY) #round y
        
        l = np.sqrt(dX*dX + dY*dY)                  #calcluate the absolute l
        chkX = int(sX - dX)
        chkY = int(sY - dY)
        eAngle = eAngleRad * 180 / np.pi            #transform into degrees    
        #Check here if out of bounds:
        if chkX > width or chkX < 0:
            print ('chkX: ',chkX, ' Width: ', width, 'Out of bounds')
            out = 1
            break
        if chkY > height or chkX < 0:
            print ('chkY: ',chkY, ' Height: ', height, 'Out of bounds')
            out = 1
            break
        if out == 0:
            if thresholding[chkY, chkX] == 255:
                eX = chkX
                eY = chkY
                fP = 1
                return fP, eX, eY, eAngle, l
        fP = 0
        i = i + 1
    fP = 0
    eX = 0
    eY = 0
    eAngle = 0
    l = 0
    return fP, eX, eY, eAngle, l


def pendulum(startX, startY, startAngle, distance, deltaAngleInc, limitedAngle, maximumIter):
    '''

    '''    
    #Initial values (modify if needed, see documentation of findNextPoint.py for further details):
    sX = startX
    sY = startY
    sAngle = startAngle
    dist = distance # in Pixels        
    dAngleInc = deltaAngleInc
    limAngle = limitedAngle
    maxIter = maximumIter        
   
    distInc = 0
    x = [] #create an empty list where x values will be saved
    y = []
    
    #loop over one plant leaf
    while distInc <= maxIter:
        #print ('New starting point!')
        #print (distInc)
        fP, eX, eY, eAngle, l = findNextPoint(sX, sY, sAngle, dist, binary, dAngleInc, limAngle, width, height)
        
        if fP == 1:     #if point found set new starting values
            cv2.line(frame, (sX,sY),(eX,eY), (0,255,0), 2) #print line    
            sX = eX
            sY = eY
            sAngle = eAngle         
            x.append(sX)
            y.append(sY)
                
        if fP == 0:         #if no point found increase distance by 1
            dist += 1 
            distInc +=1
        
        if distInc == maxIter:     #if maximum iterations reached: save data to container
            xCollector.append(x)
            yCollector.append(y)

    
    if showOrigTrack == 1:
        cv2.imshow('Original video with tracking',frame)
        cv2.setMouseCallback('Original video with tracking', click_event) #new left-click




def writeresults(xCollector, yCollector):
    '''
    write results to files: x.dat & y.dat. Each row is one frame
    '''    
    
    np.savetxt('x.tmp', xCollector, delimiter=",", fmt='%s')
    np.savetxt('y.tmp', yCollector, delimiter=",", fmt='%s')
    
    #do some formatting for nice Matlab readability:
    i = 0
    with open('x.tmp') as f:
        lines = f.readlines()
    
    
    while i < len(lines):
        #read line 1:
            s = lines[i]
            #truncate:
            s = s[1:-2]
            s += '\n'
            with open('x.dat','a') as g:          #this appends text
                g.write(s)
                i=i+1
                
    #replace brackets in Y
    i = 0

    with open('y.tmp') as f:
        lines = f.readlines()
    
    
    while i < len(lines):
        #read line 1:
            s = lines[i]
            #truncate:
            s = s[1:-2]
            s += '\n'
            with open('y.dat','a') as g:          #this appends text
                g.write(s)
                i=i+1
    
    #delete temporary files:
    os.remove('x.tmp')
    os.remove('y.tmp')

    print('Writing results complete')    




"""++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
DynaFlexCV 
Exploring the DYNAmics of a FLEXible structure using Computer Vision
by Moritz Thom 2018
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"""

import numpy as np
import cv2
import os

#Variables (modify if needed):
inVid = 'example-low-res.mp4' # Name of video file to be analysed


''' Sets value for threshold methods
Using the example video, the following values are a good starting point:
Convert to binary using the most simple threshold use as Thresh1 = 140, Thresh2 is unused
Adaptive Gauss, use e.g. as Thresh1 = 3 & Thresh2 = 9 
Adaptive Mean, use e.g. as Thresh1 = 17 & Thresh2 = 18
Canny edge detection, use e.g. as Thresh1 = 100 & Thresh2 = 255 
'''
Thresh1 = 17 
Thresh2 = 18

#Variables for pendulum segmentation algorithm (modify if needed):
startX = 545 # X coordinate of starting point
startY = 371 #Y coordinate of starting point
startAngle = 0 # Angle (in degree) to start searching (0 is vertically upward)
distance = 10 # Distance (in pixels) at which search is being conducted, will be increased by 1 if no point found        
maximumIter = 11 #maximum nr. of iterations where distance is being increased by 1
deltaAngleInc = 0.1 # Angle increment (in degrees)
limitedAngle = 90 # Limit of search angle (in degrees)


# Display options(modify if needed):
showthresholdMov = 1 # Display thresholded binary video (optional)
showOrigTrack = 1 # Display original video with processed line segmentation visualized (optional) 

# Other variables (do not modify):
xCollector = []                                 #contains data from final segmentation
yCollector = []                                 #contains data from final segmentation 


cap = cv2.VideoCapture(inVid)
width = cap.get(3)              #width of video in pixel
height = cap.get(4)         #height of video in pixel
totalf = cap.get(cv2.CAP_PROP_FRAME_COUNT) #total number of frames
fnr = 0   

while(cap.isOpened()):  
    ret, frame = cap.read() # Capture frame-by-frame
    fnr += 1 
    print ("\r Frame: ".format(fnr)+str(fnr), ' /', int(totalf), ' ', end="") # Print progress in one updating line
    #print ('framenr.', fnr, 'of', totalf, end='\r')  #new
    if ret:
        ''' This is the first step where all the magic happens. 
        1. The color video is being converted to grayscale '''
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # Convert to Grayscale
        
        ''' This is the second step where all the magic happens. 
        2. The grayscale video is converted to a binary (black/white) video using the most simple algorithm (Thresh_binary) or others (uncomment to view results)
        You may want to add here some more sophisticated algorithms and also filter algorithms 
        to filter the "noise". '''
        
        #ret,binary = cv2.threshold(gray, Thresh1, 255, cv2.THRESH_BINARY_INV) #Convert to binary using the most simple threshold use as Thresh1 =
        #binary = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,Thresh1,Thresh2) #Adaptive Gauss, use e.g. as Thresh1 = 3 & Thresh2 = 9 
        binary = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY_INV,Thresh1,Thresh2) # Adaptive Mean, use e.g. as Thresh1 = 3 & Thresh2 = 20
        #binary = cv2.Canny(gray, Thresh1, Thresh2) #Canny edge detection, use e.g. as Thresh1 = 100 & Thresh2 = 255 
                
        if showthresholdMov == 1:   # Display thresholded video if wanted
            cv2.imshow('Thresholded video',binary)
            cv2.setMouseCallback('Thresholded video', click_event) # Mouse button left-click to display coordinates
        
        ''' This is the third step where more magic happens. 
        1. The binary video is being converted into a single line with the functions 'pendulum' and 'findnextpoint' 
        You may want to add here other algorithms which in your case perform better. '''
        pendulum(startX, startY, startAngle, distance, deltaAngleInc, limitedAngle, maximumIter) #Algorithm to do line sgmentation
              
    if cv2.waitKey(1) & 0xFF == ord('q') or fnr>=totalf: # Quit by hitting 'q' in movie
        break

writeresults(xCollector, yCollector) # Write results to files: x.dat & y.dat


cap.release() # When everything is done release the capture
cv2.destroyAllWindows()




        

