import cv
import fido
import numpy as np

def GetThresholdedImage(img):
  #returns thresholded image of the blue bottle
  imgHSV = cv.CreateImage(cv.GetSize(img), 8, 3)
  #converts a BGR image to HSV
  cv.CvtColor(img, imgHSV, cv.CV_BGR2HSV)
  imgThreshed = cv.CreateImage(cv.GetSize(img), 8, 1)
  #InRangeS takes source, lowerbound color, upperbound color and destination
  #It converts the pixel values lying within the range to 255 and stores it in
  #the destination
  cv.InRangeS(imgHSV, (30,100,90), (50, 130, 220), imgThreshed)
  return imgThreshed

posX = 0
posY = 0

MAX_X = 640.0
MAX_Y = 480.0

CENTER_X = MAX_X / 2.0
CENTER_Y = MAX_Y / 2.0

HEAD_CENTER = 106
HEAD_RIGHT = HEAD_CENTER + 40
HEAD_LEFT = HEAD_CENTER - 40

NECK_UP = 210
NECK_DOWN = 100
NECK_CENTER = (NECK_UP + NECK_DOWN) / 2


def main():
  color_tracker_window = "output"
  thresh_window = "thresh"
  capture = cv.CaptureFromCAM(-1)
  cv.NamedWindow( color_tracker_window, 1 )
  cv.MoveWindow(color_tracker_window, 0, 0)
  cv.NamedWindow( thresh_window, 1 )
  cv.MoveWindow(thresh_window, 700, 0)
  imgScrible = None
  storage = None
  global posX
  global posY

  fido.init_servos()
  head_x = fido.get_servo_position(fido.HEAD)
  neck_y = fido.get_servo_position(fido.NECK)
  jaw_pos = fido.get_servo_position(fido.JAW)
  
  while True:
    frame = cv.QueryFrame(capture)
    #cv.Smooth(frame, frame, cv.CV_BLUR, 3)
    cv.Smooth(frame, frame, cv.CV_GAUSSIAN, 9, 9)
    
    imgScrible = cv.CreateImage(cv.GetSize(frame), 8, 3)
		
    imgThresh = GetThresholdedImage(frame)
    
    # pre-smoothing improves Hough detector


    #if storage is None:
    #  storage = cv.CreateMat(imgThresh.width, 1, cv.CV_32FC3)
    #try:
    #  cv.HoughCircles(imgThresh, storage, cv.CV_HOUGH_GRADIENT, 1, imgThresh.height/4, 50, 20, 10, 240)
    #  circles = np.asarray(storage)
    #except Error, e:
    #  print e
    #  circles = None
    
    # find largest circle
    #maxRadius = 0
    #x = 0
    #y = 0
    #found = False
    #if circles is not None:
    #  for i in range(len(circles)):
    #    circle = circles[i]
    #    if circle[2] > maxRadius:
    #      found = True
    #      maxRadius = circle[2]
    #      x = circle[0]
    #      y = circle[1]

    #cvShowImage( 'Camera', frame) 
    #if found:
    #  posX = x
    #  posY = y
    #  print 'ball detected at position: ',x, ',', y, ' with radius: ', maxRadius
    #else:
    #  print 'no ball'
      
    mat = cv.GetMat(imgThresh)
    #Calculating the moments
    moments = cv.Moments(mat, 0) 
    area = cv.GetCentralMoment(moments, 0, 0)
    moment10 = cv.GetSpatialMoment(moments, 1, 0)
    moment01 = cv.GetSpatialMoment(moments, 0, 1)
		
    #lastX and lastY stores the previous positions
    lastX = posX
    lastY = posY
    #Finding a big enough blob
    if area > 20000: 
			
      #Calculating the coordinate postition of the centroid
      posX = int(moment10 / area)
      posY = int(moment01 / area)

      print 'x: ' + str(posX) + ' y: ' + str(posY) + ' area: ' + str(area) + ' head_x: ' + str(head_x) + ' neck_y: ' + str(neck_y) + ' jaw_pos: ' + str(jaw_pos)
      #drawing lines to track the movement of the blob
      if(lastX > 0 and lastY > 0 and posX > 0 and posY > 0):
        #cv.Circle( imgThresh, (posX, posY), maxRadius, cv.Scalar(0,0,255), 3, 8, 0 );        
        cv.Line(imgScrible, (posX, posY), (lastX, lastY), cv.Scalar(0, 255, 255), 5)
        if posX < CENTER_X - 10:
          error_x = (posX - CENTER_X) / MAX_X * (HEAD_RIGHT - HEAD_LEFT)
          desired_x = int(error_x) / 4 + head_x
          head_x = desired_x
          if head_x < HEAD_LEFT:
            head_x = HEAD_LEFT
          fido.set_servo(fido.HEAD, head_x)
        elif posX > CENTER_X + 10:
          new_x = (posX - CENTER_X) / MAX_X * (HEAD_RIGHT - HEAD_LEFT)
          head_x = int(new_x) / 4 + head_x
          if head_x > HEAD_RIGHT:
            head_x = HEAD_RIGHT
          fido.set_servo(fido.HEAD, head_x)

        if posY < CENTER_Y - 10:
          new_y = (posY - CENTER_Y) / MAX_Y * (NECK_UP - NECK_DOWN)
          neck_y = neck_y - (int(new_y) / 8)
          if neck_y > NECK_UP:
            neck_y = NECK_UP
          fido.set_servo(fido.NECK, neck_y)
        elif posY > CENTER_Y + 10:
          new_y = (posY - CENTER_Y) / MAX_Y * (NECK_UP - NECK_DOWN)
          neck_y = neck_y - (int(new_y) / 8)
          if neck_y < NECK_DOWN:
            neck_y = NECK_DOWN
          fido.set_servo(fido.NECK, neck_y)

        jaw_pos =int((float(area) - 60000.0) / 1000000.0 * (fido.JAW_OPEN - fido.JAW_CLOSED_EMPTY) + fido.JAW_CLOSED_EMPTY)
        jaw_pos = max(min(jaw_pos, fido.JAW_OPEN), fido.JAW_CLOSED_EMPTY)
        fido.set_servo(fido.JAW, jaw_pos)
      #Adds the three layers and stores it in the frame
      #frame -> it has the camera stream
      #imgScrible -> it has the line tracking the movement of the blob
      cv.Add(frame, imgScrible, frame)

    cv.ShowImage(thresh_window, imgThresh)
    cv.ShowImage(color_tracker_window, frame)
    c = cv.WaitKey(10)
    if(c!=-1):
      break


if __name__ == "__main__":
  main()