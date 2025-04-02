from luma.core.interface.serial import i2c
from luma.oled.device import sh1106
from PIL import Image, ImageDraw, ImageFont
import time

# I2C setup
serial = i2c(port=1, address=0x3C)  # Adjust the address if necessary
oled = sh1106(serial, width=128, height=64)

# Create a blank image for drawing
image = Image.new("1", (oled.width, oled.height))
draw = ImageDraw.Draw(image)

# Load default font
font = ImageFont.load_default()

# Animation loop
for x in range(oled.width):
    # Clear the image
    draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
    
    # Draw moving text
    draw.text((x, 25), "Hello, I am BAYMAX", font=font, fill=255)
    
    # Display the image on the OLED
    oled.display(image)
    
    # Small delay for animation effect
    time.sleep(0.05)
