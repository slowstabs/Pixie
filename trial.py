import time
from board import SCL, SDA
import busio
from adafruit_servokit import ServoKit
import multiprocessing

import RPi.GPIO as GPIO
import os
import sys
import logging
from PIL import Image, ImageDraw, ImageFont
from random import randint
from adafruit_ssd1306 import SSD1306_I2C

# GPIO pins
touch_pin = 17
vibration_pin = 22

# Set up pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(touch_pin, GPIO.IN)
GPIO.setup(vibration_pin, GPIO.IN)

# Servo setup
kit = ServoKit(channels=16)
servoR = kit.servo[0]  # Reference at 0
servoL = kit.servo[1]  # Reference at 180
servoB = kit.servo[4]  # Reference at 90

frame_count = {'blink': 39, 'happy': 60, 'sad': 47, 'dizzy': 67, 'excited': 24, 'neutral': 61, 'happy2': 20, 'angry': 20, 'happy3': 26, 'bootup3': 124, 'blink2': 20}

emotion = ['angry', 'sad', 'excited']
normal = ['neutral', 'blink2']

q = multiprocessing.Queue()
event = multiprocessing.Event()

# OLED setup
try:
    i2c = busio.I2C(SCL, SDA)
    oled_width = 128
    oled_height = 64
    oled = SSD1306_I2C(oled_width, oled_height, i2c)
except ValueError as e:
    logging.error(f"Error initializing OLED: {e}")
    sys.exit(1)
except RuntimeError as e:
    logging.error(f"I2C bus error: {e}")
    sys.exit(1)

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
            print('vib')
            if q.qsize() == 0:
                event.set()
                q.put(emotion[randint(0, 2)])
        time.sleep(0.05)

def servoMed():
    servoR.angle = 90
    servoL.angle = 90
    servoB.angle = 90

def servoDown():
    servoR.angle = 0
    servoL.angle = 180
    servoB.angle = 90

def show(emotion, count):
    for _ in range(count):
        try:
            for i in range(frame_count[emotion]):
                # Load the image
                image_path = f'/home/pi/Desktop/EmoBot/emotions/{emotion}/frame{i}.png'
                image = Image.open(image_path).convert("1")  # Convert to 1-bit for OLED
                oled.image(image)
                oled.show()
                time.sleep(0.1)
        except IOError as e:
            logging.info(e)
        except KeyboardInterrupt:
            oled.fill(0)
            oled.show()
            servoDown()
            logging.info("quit:")
            exit()

if __name__ == '__main__':
    p1 = multiprocessing.Process(target=check_sensor, name='p1')
    p1.start()
    while True:
        if event.is_set():
            event.clear()
            emotion = q.get()
            q.empty()
            print(emotion)
            p2 = multiprocessing.Process(target=show, args=(emotion, 4))
            p2.start()
            p2.join()
        else:
            neutral = normal[0]
            p5 = multiprocessing.Process(target=show, args=(neutral, 4), name='p5')
            p5.start()
            p5.join()
