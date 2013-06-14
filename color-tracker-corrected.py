import cv
import fido

def GetThresholdedImage(img):
  #returns thresholded image of the blue bottle
  imgHSV = cv.CreateImage(cv.GetSize(img), 8, 3)
  #converts a BGR image to HSV
  cv.CvtColor(img, imgHSV, cv.CV_BGR2HSV)
  imgThreshed = cv.CreateImage(cv.GetSize(img), 8, 1)
  #InRangeS takes source, lowerbound color, upperbound color and destination
  #It converts the pixel values lying within the range to 255 and stores it in
  #the destination
  cv.InRangeS(imgHSV, (30,30,180), (80, 170, 220), imgThreshed)
  return imgThreshed

posX = 0
posY = 0

def main():
  color_tracker_window = "output"
  thresh_window = "thresh"
  capture = cv.CaptureFromCAM(-1)
  cv.NamedWindow( color_tracker_window, 1 ) 
  cv.NamedWindow( thresh_window, 1 ) 
  imgScrible = None
  global posX
  global posY

  fido.init_servos()
  
  while True:
    frame = cv.QueryFrame(capture)
    cv.Smooth(frame, frame, cv.CV_BLUR, 3)
		
    if(imgScrible is None):
      imgScrible = cv.CreateImage(cv.GetSize(frame), 8, 3)
		
    imgThresh = GetThresholdedImage(frame)
		
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
    if(area > 100000): 
			
      #Calculating the coordinate postition of the centroid
      posX = int(moment10 / area)
      posY = int(moment01 / area)

      print 'x: ' + str(posX) + ' y: ' + str(posY) + ' area: ' + str(area)
      #drawing lines to track the movement of the blob
      if(lastX > 0 and lastY > 0 and posX > 0 and posY > 0):
        cv.Line(imgScrible, (posX, posY), (lastX, lastY), cv.Scalar(0, 255, 255), 5)
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