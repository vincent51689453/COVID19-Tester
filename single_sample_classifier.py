"""
@@@ Name:   Samples classifier
@@@ Author: VincentChan
@@@ Date:   12/21/2020
"""
import sensor, image, time

sensor.reset()                      # Reset and initialize the sensor.
sensor.set_pixformat(sensor.RGB565) # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.QVGA)   # Set frame size to QVGA (320x240)
sensor.skip_frames(time = 2000)     # Wait for settings take effect.
clock = time.clock()                # Create a clock object to track the FPS.

#Region of Interest control
enable_roi = True
roi_x,roi_y,roi_w,roi_h = 93,231,60,44

#Gaussian Smooth Filter (only effective after roi is enabled)
enable_gaus_smooth = True

#Blob detection (green chemicals)
chemicals_thresh = [(53,100,-8,-62,-65,24)]
blob_roi = (0,0,139,40)

#Remove fish eye effect
enable_lens_corr = True

while(True):

    clock.tick()
    img = sensor.snapshot()
    """
    Image rotation:
    - vflip=False, hmirror=False, transpose=False -> 0 degree rotation
    - vflip=True, hmirror=False, transpose=True -> 90 degree rotation
    - vflip=True, hmirror=True, transpose=False -> 180 degree rotation
    - vflip=False, hmirror=True, transpose=True -> 270 degree rotation
    """
    img = img.replace(img,vflip=False,hmirror=True,transpose=True)

    if enable_roi:
        img = img.crop((roi_x,roi_y,roi_w,roi_h))
        if enable_gaus_smooth:
          #Apply a 3x3 gaussian filter
          img = img.gaussian(1)

    #Unfisy-eye
    if enable_lens_corr: img.lens_corr(2.2)


    #Blob detection (chemicals)
    for blob in img.find_blobs(chemicals_thresh, roi=blob_roi ,pixels_threshold=20, \
                               area_threshold=20, merge=False):
        blob_area = blob[4]
        blob_rect = blob.rect()
        blob_cx,blob_cy = blob.cx(), blob.cy()
        # Visualization
        if(blob_area>100):
            #Green for positive
            print("Detection Result:")
            print("Area:{} CX:{} CY:{} Result: Positive".format(blob_area,blob_cx,blob_cy))
            img = img.draw_rectangle(blob_rect,color=(0,255,0))

        else:
            #Blue for negative
            print("Detection Result:")
            print("Area:{} CX:{} CY:{} Result: Negative".format(blob_area,blob_cx,blob_cy))
            img = img.draw_rectangle(blob_rect,color=(0,0,255))


    min_x = 999

    #print("=======================EOF=======================")
