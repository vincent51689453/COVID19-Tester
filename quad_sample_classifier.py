"""
@@@ Name  : Quad COVID-19 Samples Classifier
@@@ Author: VincentChan
@@@ Date  : 22/2/2021
@@@ MCU   : STM32H743
"""

"""
Remark:
1. Message of four samples (string) will be sent every 500ms.
2. Message header = "A" and Message tail = "B"
3. Each sample will be represented by a constant of four digits length.
"""

"""
Image rotation:
- vflip=False, hmirror=False, transpose=False -> 0 degree rotation
- vflip=True, hmirror=False, transpose=True -> 90 degree rotation
- vflip=True, hmirror=True, transpose=False -> 180 degree rotation
- vflip=False, hmirror=True, transpose=True -> 270 degree rotation
"""

import sensor, image, time
import pyb
from pyb import UART
import ustruct

#System wakeup GIPO
ready = pyb.Pin("P2",pyb.Pin.OUT_PP)
ready.low()
test_led = pyb.LED(3)
test_led.on()

#Camera sensor setup
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time = 2000)

#FPS Clock
clock = time.clock()

#Digital Zoom Areas
area1_xmin, area1_ymin, area1_xmax, area1_ymax = 6,29,46,62
area2_xmin, area2_ymin, area2_xmax, area2_ymax = 196,7,234,69
area3_xmin, area3_ymin, area3_xmax, area3_ymax = 6,108,84,143
area4_xmin, area4_ymin, area4_xmax, area4_ymax = 9,261,225,315

#System Control Variables
enable_roi = True    # ON/OFF Digital Zoom
area_counter = 1     # Area Indicator
max_FPS = 77         # FPS for this program
delay = 0            # Delay counter
max_area_num = 4     # Total number of digital zoom areas
message_index = 0    # UART Message index

#UART
#OPENMV PO (UART1 RX) <-> Arduino MEGA 11 (TX)
#OPENMV P1 (UART1 TX) <-> Arduino MEGA 10 (RX)
uart = UART(1,115200)

#Capture and Loop
while(True):

    #FPS Counter
    clock.tick()

    #Send GPIO signal (System Ready)
    ready.high()

    #Image capture
    img = sensor.snapshot()

    #Image Rotation
    img = img.replace(img,vflip=True,hmirror=False,transpose=True)

    if enable_roi:
        #Zoom to different defined area
        if(area_counter == 1):
            #Area 1
            h = area1_ymax-area1_ymin
            w = area1_xmax-area1_xmin
            img = img.crop(roi=(area1_xmin, area1_ymin,w,h))
            if(delay == (int(max_FPS/8)-1)):
                #Only send once before the end of this period
                print("Area1")

        if(area_counter == 2):
            #Area 2
            h = area2_ymax-area2_ymin
            w = area2_xmax-area2_xmin
            img = img.crop(roi=(area2_xmin, area2_ymin,w,h))
            if(delay == (int(max_FPS/8)-1)):
                #Only send once before the end of this period
                print("Area2")
        if(area_counter == 3):
            #Area 3
            h = area3_ymax-area3_ymin
            w = area3_xmax-area3_xmin
            img = img.crop(roi=(area3_xmin, area3_ymin,w,h))
            if(delay == (int(max_FPS/8)-1)):
                #Only send once before the end of this period
                print("Area3")

        if(area_counter == 4):
            #Area 4
            h = area4_ymax-area4_ymin
            w = area4_xmax-area4_xmin
            img = img.crop(roi=(area4_xmin, area4_ymin,w,h))
            if(delay == (int(max_FPS/8)-1)):
                #Only send once before the end of this period
                print("Area4")

        if(area_counter == (max_area_num+1)):
            #Reset
            area_counter = 1
            # Send message
            print("#{} Message->: {}".format(message_index,"000"))
            message_index += 1

        #Frame Delay: 500ms -> max_FPS/2,then (max_FPS/2)/4 for each area
        if(delay == int(max_FPS/8)):
            delay = 0
            area_counter += 1


    delay += 1

