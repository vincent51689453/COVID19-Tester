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

#Camera sensor setup
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time = 2000)

#FPS Clock
clock = time.clock()

#Digital Zoom Areas
area1_xmin, area1_ymin, area1_xmax, area1_ymax = 7,19,64,88
area2_xmin, area2_ymin, area2_xmax, area2_ymax = 90,24,151,77
area3_xmin, area3_ymin, area3_xmax, area3_ymax = 172,17,243,73
area4_xmin, area4_ymin, area4_xmax, area4_ymax = 250,7,315,74

#System Control Variables
enable_roi = True         # ON/OFF Digital Zoom
area_counter = 1          # Area Indicator
max_FPS = 19              # FPS for this program
delay = 0                 # Delay counter
max_area_num = 4          # Total number of digital zoom areas
message_index = 0         # UART Message index
uart_msg_start = "A"      # UART Message header
uart_msg_tail = "B"       # UART Message tailer

#UART
#OPENMV PO (UART1 RX) <-> Arduino MEGA 11 (TX)
#OPENMV P1 (UART1 TX) <-> Arduino MEGA 10 (RX)
#UART LED -> BLUE
uart = UART(1,115200)
uart_led = pyb.LED(3)
uart_led_status = False

#UART LED Control
def uart_led_control(led,enable=True):
    if(enable):
        global uart_led_status
        if(uart_led_status):
            led.on()
        else:
            led.off()
        uart_led_status = not(uart_led_status)

#Blob Detection
chemical_thresh = [(38, 94, 20, -95, -21, 67)]  #Blob Detection Threshold
area_thresh_n = 300                             #Detection area threshold for negative samples
area_thresh_p = 10                              #Detection area threshold for positive samples

area1_total_n = 0                               #Area1 Total area for negative samples
area1_total_p = 0                               #Area1 Total area for positive samples
area1_num = 0                                   #Sample size

#Function to ensure a integer value is padded to constant length string
def message_padding(int_msg,fixed_length):
    x = 0
    pad_msg = "0"
    zero = "0"

    #Find number of zeros needed
    l = len(str(int_msg))
    zeros = fixed_length - l

    #Padding
    while(x<(zeros-1)):
        pad_msg += zero
        x += 1

    #Add original msg after padding
    if(zeros>0):
        pad_msg += str(int_msg)
    else:
        pad_msg = str(int_msg)
    return pad_msg


#Capture and Loop
while(True):

    #FPS Counter
    clock.tick()

    #Send GPIO signal (System Ready)
    ready.high()

    #Image capture
    img = sensor.snapshot()

    #Image Rotation
    img = img.replace(img,vflip=True,hmirror=True,transpose=False)

    #Frames for each area
    f = int(max_FPS/1)

    if enable_roi:
        #Zoom to different defined area
        if(area_counter == 1):

            #Area 1
            h = area1_ymax-area1_ymin
            w = area1_xmax-area1_xmin
            img = img.crop(roi=(area1_xmin, area1_ymin,w,h))

            #Blob Detection Core
            areas_in_blob_n = []
            areas_in_blob_p = []

            for blob in img.find_blobs(chemical_thresh,pixels_threshold=1, \
                                       area_threshold=1, merge=True):
                blob_area = blob[4]
                blob_rect = blob.rect()
                blob_cx,blob_cy = blob.cx(), blob.cy()
                #print("Area:{} CX:{} CY:{}".format(blob_area,blob_cx,blob_cy))
                if(blob_area >= area_thresh_n):
                    #Negative
                    img = img.draw_rectangle(blob_rect,color=(255,0,0))
                    img = img.draw_string(blob_cx,blob_cy,"N",color=(255,0,0))
                    areas_in_blob_n.append(blob_area)

                if((blob_area >=  area_thresh_p)and(blob_area < area_thresh_n)):
                    #Positive
                    img = img.draw_rectangle(blob_rect,color=(0,0,255))
                    img = img.draw_string(blob_cx,blob_cy,"P",color=(0,0,255))
                    areas_in_blob_p.append(blob_area)

            #Finding average for negative/positive
            if(len(areas_in_blob_n)>0):
                area1_total_n += max(areas_in_blob_n)
            else:
                area1_total_p += max(areas_in_blob_p)
            area1_num += 1

            if(delay == (f-1)):
                #Only send once before the end of this period
                print("<--- Start COVID Detection --->")
                #Take average for negative/positive
                if(area1_total_n == 0):
                    area1 = message_padding(int(area1_total_p/area1_num),4)
                else:
                    area1 = message_padding(int(area1_total_n/area1_num),4)

                print("Area1:",area1)
                uart_msg_start  += area1
                area1_total_p = 0
                area1_total_n = 0
                area1_num = 0

        if(area_counter == 2):
            #Area 2
            h = area2_ymax-area2_ymin
            w = area2_xmax-area2_xmin
            img = img.crop(roi=(area2_xmin, area2_ymin,w,h))
            #TO-DO: Detection Core with average
            if(delay == (f-1)):
                #Only send once before the end of this period
                print("Area2")
                area2 = message_padding(20,4)
                uart_msg_start  += area2

        if(area_counter == 3):
            #Area 3
            h = area3_ymax-area3_ymin
            w = area3_xmax-area3_xmin
            img = img.crop(roi=(area3_xmin, area3_ymin,w,h))
            #TO-DO: Detection Core with average
            if(delay == (f-1)):
                #Only send once before the end of this period
                print("Area3")
                area3 = message_padding(30,4)
                uart_msg_start  += area3

        if(area_counter == 4):
            #Area 4
            h = area4_ymax-area4_ymin
            w = area4_xmax-area4_xmin
            img = img.crop(roi=(area4_xmin, area4_ymin,w,h))
            #TO-DO: Detection Core with average
            if(delay == (f-1)):
                #Only send once before the end of this period
                print("Area4")
                area4 = message_padding(40,4)
                uart_msg_start  += area4
                uart_msg_start  += uart_msg_tail

        if(area_counter == (max_area_num+1)):
            #Reset
            area_counter = 1

            # Send UART message
            print("#{} Message->: {}\r\n".format(message_index,uart_msg_start))
            uart.write(uart_msg_start)
            uart_led_control(uart_led)
            uart_msg_start = "A"
            message_index += 1

        #Frame Delay
        if(delay == f):
            delay = 0
            #area_counter += 1
            area_counter = 1
    delay += 1

