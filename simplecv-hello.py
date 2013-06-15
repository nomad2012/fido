import SimpleCV as scv
cam = scv.Camera()

while (1):
        i = cam.getImage()
        i.show()