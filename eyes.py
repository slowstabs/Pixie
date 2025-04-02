from luma.core.interface.serial import i2c
from luma.oled.device import sh1106
from PIL import Image, ImageDraw
import time
import random

# I2C setup
serial = i2c(port=1, address=0x3C)

# OLED display setup (128x64 resolution)
WIDTH = 128
HEIGHT = 64
oled = sh1106(serial, width=WIDTH, height=HEIGHT)

# Clear the display
oled.clear()
oled.show()

# Create a blank image for drawing
image = Image.new("1", (WIDTH, HEIGHT))
draw = ImageDraw.Draw(image)

def draw_eyes(emotion):
    # Clear the image
    draw.rectangle((0, 0, WIDTH, HEIGHT), outline=0, fill=0)
    
    if emotion == "happy":
        # Happy eyes
        draw.arc((30, 25, 50, 45), start=0, end=180, fill=255)  # Left eye
        draw.arc((80, 25, 100, 45), start=0, end=180, fill=255)  # Right eye
    elif emotion == "angry":
        # Angry eyes
        draw.line((30, 25, 50, 35), fill=255)  # Left eye
        draw.line((80, 35, 100, 25), fill=255)  # Right eye
    elif emotion == "excited":
        # Excited eyes
        draw.ellipse((30, 25, 50, 45), outline=255, fill=255)  # Left eye
        draw.ellipse((80, 25, 100, 45), outline=255, fill=255)  # Right eye
    elif emotion == "sad":
        # Sad eyes
        draw.arc((30, 25, 50, 45), start=180, end=360, fill=255)  # Left eye
        draw.arc((80, 25, 100, 45), start=180, end=360, fill=255)  # Right eye

    # Display the eyes
    oled.display(image)

    # Random blinking animation
    if random.random() < 0.3:  # 30% chance to blink
        time.sleep(0.1)  # Pause before blinking
        draw.rectangle((30, 25, 50, 45), outline=0, fill=0)  # Close left eye
        draw.rectangle((80, 25, 100, 45), outline=0, fill=0)  # Close right eye
        oled.display(image)
        time.sleep(0.2)  # Blink duration
        draw_eyes(emotion)  # Redraw the eyes after blinking
if __name__ == "__main__":
    emotions = ["happy", "angry", "excited", "sad"]
    try:
        while True:
            # Randomly select an emotion
            emotion = random.choice(emotions)
            draw_eyes(emotion)
            time.sleep(2)  # Pause before changing emotion
    except KeyboardInterrupt:
        # Clear the display on exit
        oled.clear()
        oled.show()
        print("Program terminated.")
