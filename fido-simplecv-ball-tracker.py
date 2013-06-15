import SimpleCV as scv
import fido

def GetThresholdedImage(img):
  '''Answer a thresholded image based on the color of a green tennis ball'''
  imgHSV = img.toHSV()
  dist = img.hueDistance((38,60,212), 50, 180)
  return img - dist

posX = 0
posY = 0

MAX_X = 640.0
MAX_Y = 480.0

CENTER_X = MAX_X / 2.0
CENTER_Y = MAX_Y / 2.0

HEAD_CENTER = 106
HEAD_RIGHT = HEAD_CENTER + 40
HEAD_LEFT = HEAD_CENTER - 40

NECK_UP = 230
NECK_DOWN = 100
NECK_CENTER = (NECK_UP + NECK_DOWN) / 2


def main():

  display = scv.Display()
  cam = scv.Camera()
  global posX
  global posY

  fido.init_servos()
  fido.set_servo(fido.NECK, NECK_DOWN)
  head_x = fido.get_servo_position(fido.HEAD)
  neck_y = fido.get_servo_position(fido.NECK)
  jaw_pos = fido.get_servo_position(fido.JAW)
   
  while display.isNotDone():
    img = cam.getImage()
    img.blur()
    
    #imgScrible = cv.CreateImage(cv.GetSize(frame), 8, 3)
		
    imgThresh = GetThresholdedImage(img)

    blobs = imgThresh.findBlobs()
    circles = None
    
    if blobs:
      print ' found blobs: ', len(blobs)
      circles = blobs.filter([b.isCircle(0.35) for b in blobs])
      if circles:
        print ' found circles: ', len(circles)
        max_radius = 0
        x = 0
        y = 0
        for c in circles:
          if c.radius > max_radius:
            x = c.x
            y = c.y
            max_radius = c.radius()
            area = c.area()
            
        imgThresh.drawCircle((x, y), max_radius, scv.Color.WHITE, min(3,max_radius))
		
    lastX = posX
    lastY = posY
    
    if circles: 
      posX = x
      posY = y

      print 'x: ' + str(posX) + ' y: ' + str(posY) + ' area: ' + str(area) + ' head_x: ' + str(head_x) + ' neck_y: ' + str(neck_y) + ' jaw_pos: ' + str(jaw_pos)
      #drawing lines to track the movement of the blob
      if(lastX > 0 and lastY > 0 and posX > 0 and posY > 0):
        #cv.Circle( imgThresh, (posX, posY), maxRadius, cv.Scalar(0,0,255), 3, 8, 0 );        
        #cv.Line(imgScrible, (posX, posY), (lastX, lastY), cv.Scalar(0, 0, 255), 5)
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

    imgThresh.show()


if __name__ == "__main__":
  main()
