"""
@@@ Name:   Samples classifier (Single sample)
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
roi_x,roi_y,roi_w,roi_h = 110,210,110,42

#Gaussian Smooth Filter (only effective after roi is enabled)
enable_gaus_smooth = True

#Flags to indicate detection results
positive = False
negative = False

#Blob detection (green chemicals)
chemicals_n_thresh = [(59, 100, 26, -48, -44, 49)]
chemicals_p_thresh = [(40, 90, -1, 90, -85, -22)]
blob_roi = (0,0,110,42)

#Remove fish eye effect
enable_lens_corr = True

#Output data
p_area,p_cx,p_cy = 0,0,0
n_area,n_cx,n_cy = 0,0,0

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


    #Blob detection (COVID Positive)
    for blob in img.find_blobs(chemicals_p_thresh, roi=blob_roi ,pixels_threshold=1, \
                               area_threshold=300, merge=True):
        blob_area = blob[4]
        blob_rect = blob.rect()
        blob_cx,blob_cy = blob.cx(), blob.cy()
        if((blob_area<1000)and(blob_area>300)):
            #Green for positive
            #print("Detection Result:")
            #print("Area:{} CX:{} CY:{} Result: Positive".format(blob_area,blob_cx,blob_cy))
            #img = img.draw_rectangle(blob_rect,color=(0,255,0))
            p_area,p_cx,p_cy = blob_area,blob_cx,blob_cy
            p_rect = blob_rect
            positive = True

    #Blob detection (COVID Negative)
    for blob in img.find_blobs(chemicals_n_thresh, roi=blob_roi ,pixels_threshold=20, \
                           area_threshold=80, merge=True):
        blob_area = blob[4]
        blob_rect = blob.rect()
        blob_cx,blob_cy = blob.cx(), blob.cy()
        if((blob_area<500)and(blob_area>80)):
            #Blue for negative
            #print("Detection Result:")
            #print("Area:{} CX:{} CY:{} Result: Negative".format(blob_area,blob_cx,blob_cy))
            #img = img.draw_rectangle(blob_rect,color=(0,0,255))
            n_area,n_cx,n_cy = blob_area,blob_cx,blob_cy
            n_rect = blob_rect
            negative = True

    #print("Positive:{} Negative:{}".format(positive,negative))
    #Visualization
    if(positive)and(not(negative)):
        #Consider positive testing sample (GREEN)
        print("Result: Positive")
        img.draw_string(p_cx+25,p_cy-20,"P")
        img = img.draw_rectangle(p_rect,color=(0,255,0))
    if(positive)and(negative):
        #Consider negative testing sample (BLUE)
        print("Result: Negative")
        img.draw_string(n_cx+25,n_cy-20,"N")
        img = img.draw_rectangle(n_rect,color=(0,0,255))




    #RESET
    positive,negative = False,False
    p_area,p_cx,p_cy = 0,0,0
    n_area,n_cx,n_cy = 0,0,0


    #print("=======================EOF=======================")
