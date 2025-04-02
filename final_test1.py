import time
import os
import multiprocessing
import logging
from random import randint

import RPi.GPIO as GPIO
from adafruit_servokit import ServoKit
from luma.core.interface.serial import i2c
from luma.oled.device import sh1106
from PIL import Image, ImageDraw, ImageFont
from board import SCL, SDA
import busio
import sys
sys.path.append("..")

# Setup GPIO pins for touch and vibration sensors
touch_pin = 17
vibration_pin = 22

GPIO.setmode(GPIO.BCM)
GPIO.setup(touch_pin, GPIO.IN)
GPIO.setup(vibration_pin, GPIO.IN)

# Raspberry Pi pin configuration for Servos
kit = ServoKit(channels=16)
servoR = kit.servo[0]  # Reference at 0
servoL = kit.servo[1]  # Reference at 180
servoB = kit.servo[4]  # Reference at 90

frame_count = {
    'blink': 39,
    'happy': 60,
    'sad': 47,
    'dizzy': 67,
    'excited': 24,
    'neutral': 61,
    'happy2': 20,
    'angry': 20,
    'happy3': 26,
    'bootup3': 124,
    'blink2': 20
}

emotion = ['angry', 'sad', 'excited']
normal = ['neutral', 'blink2']

q = multiprocessing.Queue()
event = multiprocessing.Event()

# Sensor Check Function
def check_sensor():
    previous_state = 1
    current_state = 0
    while True:
        if GPIO.input(touch_pin) == GPIO.HIGH:
            if previous_state != current_state:
                if q.qsize() == 0:
                    event.set()
                    q.put('happy')
                current_state = 1
            else:
                current_state = 0
        if GPIO.input(vibration_pin) == 1:
            print('vibration detected')
            if q.qsize() == 0:
                event.set()
                q.put(emotion[randint(0, 2)])
        time.sleep(0.05)

# Servo Functions
def servoMed():
    servoR.angle = 90
    servoL.angle = 90
    servoB.angle = 90

def servoDown():
    servoR.angle = 0
    servoL.angle = 180
    servoB.angle = 90

# Show on OLED Display (1.3 inch)
serial = i2c(port=1, address=0x3C)  # Update the port and address if needed
oled = sh1106(serial, rotate=0)

def show(emotion, count):
    for _ in range(count):
        try:
            for i in range(frame_count[emotion]):
                image = Image.open(f'/home/pi/Desktop/Emo/emotions/{emotion}/frame{i}.png').convert("1")
                oled.display(image)
        except IOError as e:
            logging.info(e)
        except KeyboardInterrupt:
            oled.clear()
            servoDown()
            logging.info("quit:")
            exit()

# Sound Function
def sound(emotion):
    os.system(f"aplay /home/pi/Desktop/Emo/sound/{emotion}.wav")

# Emotion Functions (Happy, Angry, Sad, etc.)
def happy():
    servoMed()
    for n in range(5):
        for i in range(0, 120):
            if i <= 30:
                servoR.angle = 90 + i
                servoL.angle = 90 - i
                servoB.angle = 90 - i
            if 30 < i <= 90:
                servoR.angle = 150 - i
                servoL.angle = i + 30
                servoB.angle = i + 30
            if i > 90:
                servoR.angle = i - 30
                servoL.angle = 210 - i
                servoB.angle = 210 - i
            time.sleep(0.004)

def angry():
    for i in range(5):
        baserotate(90, randint(0, 30), 0.01)

def sad():
    servoDown()
    for i in range(0, 60):
        if i <= 15:
            servoB.angle = 90 - i
        if 15 < i <= 45:
            servoB.angle = 60 + i
        if i > 45:
            servoB.angle = 150 - i
        time.sleep(0.09)

def excited():
    servoDown()
    for i in range(0, 120):
        if i <= 30:
            servoB.angle = 90 - i
        if 30 < i <= 90:
            servoB.angle = i + 30
        if i > 90:
            servoB.angle = 210 - i
        time.sleep(0.01)

def blink():
    servoR.angle = 0
    servoL.angle = 180
    servoB.angle = 90


def baserotate(reference,change,timedelay):
    for i in range(reference,reference+change,1):
        servoB.angle = i
        time.sleep(timedelay)
    for j in range(reference+change, reference-change,-1):
        servoB.angle = j
        time.sleep(timedelay)
    for k in range(reference-change, reference,1):
        servoB.angle = k
        time.sleep(timedelay)
def HandDownToUp(start,end,timedelay):
	for i,j in zip(range(0+start,end,1),range((180-start),(180-end),-1)):
		servoR.angle = i
		servoL.angle = j
		time.sleep(timedelay)

def HandUpToDown(start,end,timedelay):
	for i,j in zip(range(0+start,end,-1),range((180-start),(180-end),1)):
		servoR.angle = i
		servoL.angle = j
		time.sleep(timedelay)


def rotate(start,end,timedelay):
    if start<end:
        HandDownToUp(start,end,timedelay)
        HandUpToDown(end,start,timedelay)
    else:
        HandUpToDown(end,start,timedelay)
        HandDownToUp(start,end,timedelay)

def bootup():
    show('bootup3', 1)
    p2 = multiprocessing.Process(target=show, args=('blink2', 3))
    p3 = multiprocessing.Process(target=rotate, args=(0, 150, 0.005))
    p4 = multiprocessing.Process(target=baserotate, args=(90, 45, 0.01))
    p2.start()
    p3.start()
    p4.start()
    p4.join()
    p2.join()
    p3.join()

# Main Program
if __name__ == '__main__':
    p1 = multiprocessing.Process(target=check_sensor, name='p1')
    p1.start()
    bootup()
    while True:
        if event.is_set():
            p5.terminate()
            event.clear()
            emotion = q.get()
            q.empty()
            print(emotion)
            p2 = multiprocessing.Process(target=show, args=(emotion, 4))
            p3 = multiprocessing.Process(target=sound, args=(emotion,))
            if emotion == 'happy':
                p4 = multiprocessing.Process(target=happy)
            elif emotion == 'angry':
                p4 = multiprocessing.Process(target=angry)
            elif emotion == 'sad':
                p4 = multiprocessing.Process(target=sad)
            elif emotion == 'excited':
                p4 = multiprocessing.Process(target=excited)
            elif emotion == 'blink':
                p4 = multiprocessing.Process(target=blink)
            else:
                continue
            p2.start()
            p3.start()
            p4.start()
            p2.join()
            p3.join()
            p4.join()
        else:
            p = multiprocessing.active_children()
            for i in p:
                if i.name not in ['p1', 'p5', 'p6']:
                    i.terminate()
            neutral = normal[0]
            p5 = multiprocessing.Process(target=show, args=(neutral, 4), name='p5')
            p6 = multiprocessing.Process(target=baserotate, args=(90, 60, 0.02), name='p6')
            p5.start()
            p6.start()
            p6.join()
            p5.join()
