"""
@@@ Name  : Quad COVID-19 Samples Classifier
@@@ Author: VincentChan
@@@ Date  : 22/2/2021
"""

"""
Image rotation:
- vflip=False, hmirror=False, transpose=False -> 0 degree rotation
- vflip=True, hmirror=False, transpose=True -> 90 degree rotation
- vflip=True, hmirror=True, transpose=False -> 180 degree rotation
- vflip=False, hmirror=True, transpose=True -> 270 degree rotation
"""

import sensor, image, time

#Camera sensor setup
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time = 2000)

#FPS Clock
clock = time.clock()

#Digital Zoom Areas
area1_xmin, area1_ymin, area1_xmax, area1_ymax = 6,29,46,62
area2_xmin, area2_ymin, area2_xmax, area2_ymax = 145,23,202,67
area3_xmin, area3_ymin, area3_xmax, area3_ymax = 6,108,84,143
area4_xmin, area4_ymin, area4_xmax, area4_ymax = 9,261,225,315

#System Control Variables
enable_roi = True    # ON/OFF Digital Zoom
area_counter = 1     # Area Indicator
max_FPS = 30         # FPS for this program
delay = 0            # Delay counter
max_area_num = 4     # Total number of digital zoom areas

#Capture and Loop
while(True):

    #FPS Counter
    clock.tick()

    #Image capture (not capturing if wrong area_counter)
    if(area_counter < (max_area_num+1)):
        img = sensor.snapshot()

    #Image Rotation
    img = img.replace(img,vflip=True,hmirror=False,transpose=True)

    if enable_roi:
        #Zoom to different defined area
        if(area_counter == 1):
            #Area 1
            h = area1_ymax-area1_ymin
            w = area1_xmax-area1_xmin
            img = img.crop((area1_xmin, area1_ymin,w,h))

        if(area_counter == 2):
            #Area 2
            h = area2_ymax-area2_ymin
            w = area2_xmax-area2_xmin
            img = img.crop((area2_xmin, area2_ymin,w,h))

        if(area_counter == 3):
            #Area 3
            h = area3_ymax-area3_ymin
            w = area3_xmax-area3_xmin
            img = img.crop((area3_xmin, area3_ymin,w,h))

        if(area_counter == 4):
            #Area 4
            h = area4_ymax-area4_ymin
            w = area4_xmax-area4_xmin
            img = img.crop((area4_xmin, area4_ymin,w,h))

        if(area_counter == (max_area_num+1)):
            #Reset
            area_counter = 1

        #Frame Delay
        if(delay % max_FPS == 0):
            area_counter += 1

    delay += 1

