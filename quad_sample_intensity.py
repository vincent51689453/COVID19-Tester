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

#System wakeup GPIO
ready = pyb.Pin("P2",pyb.Pin.OUT_PP)
ready.high()

#Camera sensor setup
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time = 2000)

#FPS Clock
clock = time.clock()

#Digital Zoom Areas
area1_xmin, area1_ymin, area1_h, area1_w = 33,95,20,38
area2_xmin, area2_ymin, area2_h, area2_w = 106,area1_ymin,area1_h,area1_w
area3_xmin, area3_ymin, area3_h, area3_w = 184,area1_ymin,area1_h,area1_w
area4_xmin, area4_ymin, area4_h, area4_w = 257,area1_ymin,area1_h,area1_w

#System Control Variables
enable_roi = True         # ON/OFF Digital Zoom
#enable_roi = False         # ON/OFF Digital Zoom
area_counter = 1          # Area Indicator
max_FPS = 19              # FPS for this program
delay = 0                 # Delay counter
max_area_num = 4          # Total number of digital zoom areas
message_index = 0         # UART Message index
uart_msg_start = "A"      # UART Message header
uart_msg_tail = "B"       # UART Message tailer
intensity_config = 4     # Multiple of average intensity

#UART
#OPENMV PO (UART1 RX) <-> Arduino MEGA 11 (TX)
#OPENMV P1 (UART1 TX) <-> Arduino MEGA 10 (RX)
#UART LED -> BLUE
uart = UART(1,115200)
uart_led = pyb.LED(3)
uart_led_status = False
uart_package_index = 1


area1_num = 0          #Sample size of area 1
total_intensity_1 = 0  #Cummulative intensity
area2_num = 0          #Sample size of area 2
total_intensity_2 = 0  #Cummulative intensity
area3_num = 0          #Sample size of area 3
total_intensity_3 = 0  #Cummulative intensity
area4_num = 0          #Sample size of area 4
total_intensity_4 = 0  #Cummulative intensity

#UART Message Packet Control
def uart_package_manager(system_msg):
    global uart_package_index
    print("debug:",system_msg)
    head,tail = system_msg[0],system_msg[-1]
    data_index = '0'
    sample_1 = '0000'
    sample_2 = '0000'

    if(uart_package_index == 1):
        # Only send sample 1 & 2
        data_index = str(uart_package_index)
        sample_1 = system_msg[1:5]
        sample_2 = system_msg[5:9]
        uart_package_index = 2
    else:
        # Only send sample 3 & 4
        data_index = str(uart_package_index)
        sample_1 = system_msg[9:13]
        sample_2 = system_msg[13:17]
        uart_package_index = 1


    msg = head + data_index + sample_1 + sample_2 + tail
    return msg


#UART LED Control
def uart_led_control(led,enable=True):
    if(enable):
        global uart_led_status
        if(uart_led_status):
            led.on()
        else:
            led.off()
        uart_led_status = not(uart_led_status)

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
    ready.low()

    #Image capture
    img = sensor.snapshot()

    #Image Rotation
    img = img.replace(img,vflip=False,hmirror=False,transpose=False)

    #Frames for each area (2 is shortest)
    f = int(max_FPS/1)
    f = 3


    if enable_roi:
        #Zoom to different defined area
        if(area_counter == 1):

            #Area 1
            img = img.crop(roi=(area1_xmin, area1_ymin,area1_w,area1_h))


            #RGB TO YUV Conversion
            intensity = 0
            Y = None
            for x in range(0,(area1_w*area1_h)):
                Y = image.rgb_to_yuv(img[x])
                intensity += Y[0]

            #Normalization
            norm_intensity = (intensity/(area1_w*area1_h))*intensity_config

            #Save all intensity among different frames
            total_intensity_1 += norm_intensity

            area1_num += 1

            if(delay == (f-1)):
                intensity_1 = message_padding(int(total_intensity_1/area1_num),4)
                print("Intensity 1:",intensity_1)
                uart_msg_start  += intensity_1
                #Visualize detection result
                img = img.draw_string(1,1,"1",color=(255,0,0))
                total_intensity_1 = 0
                area1_num = 0



        if(area_counter == 2):
            #Area 2
            img = img.crop(roi=(area2_xmin, area2_ymin,area2_w,area2_h))

            #RGB TO YUV Conversion
            intensity = 0
            Y = None
            for x in range(0,(area2_w*area2_h)):
                Y = image.rgb_to_yuv(img[x])
                intensity += Y[0]

            #Normalization
            norm_intensity = (intensity/(area2_w*area2_h))*intensity_config

            #Save all intensity among different frames
            total_intensity_2 += norm_intensity


            area2_num += 1

            if(delay == (f-1)):
                intensity_2 = message_padding(int(total_intensity_2/area2_num),4)
                print("Intensity 2:",intensity_2)
                uart_msg_start  += intensity_2
                #Visualize detection result
                img = img.draw_string(1,1,"2",color=(255,0,0))
                total_intensity_2 = 0
                area2_num = 0



        if(area_counter == 3):
            #Area 3
            img = img.crop(roi=(area3_xmin, area3_ymin,area3_w,area1_h))
            #RGB TO YUV Conversion
            intensity = 0
            Y = None
            for x in range(0,(area3_w*area3_h)):
                Y = image.rgb_to_yuv(img[x])
                intensity += Y[0]

            #Normalization
            norm_intensity = (intensity/(area3_w*area3_h))*intensity_config

            #Save all intensity among different frames
            total_intensity_3 += norm_intensity

            area3_num += 1

            if(delay == (f-1)):
                intensity_3 = message_padding(int(total_intensity_3/area3_num),4)
                print("Intensity 3:",intensity_3)
                uart_msg_start  += intensity_3
                #Visualize detection result
                img = img.draw_string(1,1,"3",color=(255,0,0))
                total_intensity_3 = 0
                area3_num = 0

        if(area_counter == 4):
            #Area 4
            img = img.crop(roi=(area4_xmin, area4_ymin,area4_w,area4_h))
            #RGB TO YUV Conversion
            intensity = 0
            Y = None
            for x in range(0,(area4_w*area4_h)):
                Y = image.rgb_to_yuv(img[x])
                intensity += Y[0]

            #Normalization
            norm_intensity = (intensity/(area4_w*area4_h))*intensity_config

            #Save all intensity among different frames
            total_intensity_4 += norm_intensity

            area4_num += 1

            if(delay == (f-1)):
                intensity_4 = message_padding(int(total_intensity_4/area4_num),4)
                print("Intensity 4:",intensity_4)
                uart_msg_start  += intensity_4
                #Visualize detection result
                img = img.draw_string(1,1,"4",color=(255,0,0))
                total_intensity_4 = 0
                area4_num = 0

        if(area_counter == (max_area_num+1)):
            #Reset
            area_counter = 1

            # Send UART message
            uart_msg_start = uart_msg_start + 'B'
            print("#{} Message->: {}".format(message_index,uart_msg_start))
            uart_message = uart_package_manager(uart_msg_start)
            print("#{} Sent through UART->: {}\r\n".format(message_index,uart_message))
            uart.write(uart_message)
            uart_led_control(uart_led)
            uart_msg_start = "A"
            message_index += 1

        #Frame Delay
        if(delay == f):
            delay = 0
            area_counter += 1

    delay += 1

