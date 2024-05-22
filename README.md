for cv2.VideoCapture, you:
- Instantiate the VideoCapture object ```vc = VideoCapture(```*cam_id*```)```
- While looping, read frames ```ret, frame = vc.read()```
- Close it down at the end ```vc.release()```

With this thing, you:
- Instantiate a FLIR_cam object ```mycam = FLIR_cam()``` (can only handle one camera!)
- While looping, read frames ```frame = mycam.acquire_image()```
- Close it down at the end ```mycam.close_camera()```

Given a Teledyne/FLIR camera has a lot of config options, you can modify the function ```setup_acqusition()``` below the object as you need, but it worked fine as-is for me.
