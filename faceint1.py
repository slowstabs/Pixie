import time
import os
import multiprocessing
import logging
from random import randint

import RPi.GPIO as GPIO
from adafruit_servokit import ServoKit
from luma.core.interface.serial import i2c
from luma.oled.device import sh1106
from PIL import Image, ImageDraw
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

# Servo setup
kit = ServoKit(channels=16)
servoR = kit.servo[0]
servoL = kit.servo[1]
servoB = kit.servo[4]

# OLED setup
WIDTH = 128
HEIGHT = 64
serial = i2c(port=1, address=0x3C)
oled = sh1106(serial, width=WIDTH, height=HEIGHT)
oled.clear()
oled.show()
image = Image.new("1", (WIDTH, HEIGHT))
draw = ImageDraw.Draw(image)

def draw_eyes(emotion):
    draw.rectangle((0, 0, WIDTH, HEIGHT), outline=0, fill=0)
    if emotion == "happy":
        draw.arc((30, 25, 50, 45), start=0, end=180, fill=255)
        draw.arc((80, 25, 100, 45), start=0, end=180, fill=255)
    elif emotion == "angry":
        draw.line((30, 25, 50, 35), fill=255)
        draw.line((80, 35, 100, 25), fill=255)
    elif emotion == "excited":
        draw.ellipse((30, 25, 50, 45), outline=255, fill=255)
        draw.ellipse((80, 25, 100, 45), outline=255, fill=255)
    elif emotion == "sad":
        draw.arc((30, 25, 50, 45), start=180, end=360, fill=255)
        draw.arc((80, 25, 100, 45), start=180, end=360, fill=255)
    oled.display(image)

# Servo functions
def servoMed():
    servoR.angle = 90
    servoL.angle = 90
    servoB.angle = 90

def servoDown():
    servoR.angle = 0
    servoL.angle = 180
    servoB.angle = 90

def happy():
    servoMed()
    for n in range(5):
        for i in range(0, 120):
            if i <= 30:
                servoR.angle = 90 + i
                servoL.angle = 90 - i
                servoB.angle = 90 - i
            elif 30 < i <= 90:
                servoR.angle = 150 - i
                servoL.angle = i + 30
                servoB.angle = i + 30
            else:
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
        elif 15 < i <= 45:
            servoB.angle = 60 + i
        else:
            servoB.angle = 150 - i
        time.sleep(0.09)

def excited():
    servoDown()
    for i in range(0, 120):
        if i <= 30:
            servoB.angle = 90 - i
        elif 30 < i <= 90:
            servoB.angle = i + 30
        else:
            servoB.angle = 210 - i
        time.sleep(0.01)

def blink():
    servoR.angle = 0
    servoL.angle = 180
    servoB.angle = 90

def baserotate(reference, change, timedelay):
    for i in range(reference, reference + change):
        servoB.angle = i
        time.sleep(timedelay)
    for j in range(reference + change, reference - change, -1):
        servoB.angle = j
        time.sleep(timedelay)
    for k in range(reference - change, reference):
        servoB.angle = k
        time.sleep(timedelay)

# Sensor detection
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
            if q.qsize() == 0:
                event.set()
                q.put(emotion[randint(0, 2)])
        time.sleep(0.05)

# Sound (optional, skipped if unavailable)
def sound(emotion):
    os.system(f"aplay /home/pi/Desktop/Emo/sound/{emotion}.wav")

emotion = ['angry', 'sad', 'excited']
normal = ['neutral', 'blink2']
q = multiprocessing.Queue()
event = multiprocessing.Event()

# Bootup sequence
def bootup():
    draw_eyes('happy')
    p_rotate = multiprocessing.Process(target=baserotate, args=(90, 45, 0.01))
    p_rotate.start()
    p_rotate.join()

if __name__ == '__main__':
    p1 = multiprocessing.Process(target=check_sensor, name='p1')
    p1.start()
    bootup()
    while True:
        if event.is_set():
            event.clear()
            emo = q.get()
            q.empty()
            p2 = multiprocessing.Process(target=draw_eyes, args=(emo,))
            p3 = multiprocessing.Process(target=sound, args=(emo,))
            if emo == 'happy':
                p4 = multiprocessing.Process(target=happy)
            elif emo == 'angry':
                p4 = multiprocessing.Process(target=angry)
            elif emo == 'sad':
                p4 = multiprocessing.Process(target=sad)
            elif emo == 'excited':
                p4 = multiprocessing.Process(target=excited)
            else:
                continue
            p2.start()
            p3.start()
            p4.start()
            p2.join()
            p3.join()
            p4.join()
        else:
            draw_eyes('neutral')
            time.sleep(2)
