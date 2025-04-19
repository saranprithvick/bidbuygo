from PIL import Image, ImageDraw, ImageFont
import os

# Create a 400x400 white image
img = Image.new('RGB', (400, 400), color='white')
draw = ImageDraw.Draw(img)

# Add text
text = "No Image"
text_color = 'gray'

# Try to use a system font
try:
    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
except:
    font = ImageFont.load_default()

# Get text size
text_bbox = draw.textbbox((0, 0), text, font=font)
text_width = text_bbox[2] - text_bbox[0]
text_height = text_bbox[3] - text_bbox[1]

# Calculate position to center text
x = (400 - text_width) / 2
y = (400 - text_height) / 2

# Draw text
draw.text((x, y), text, font=font, fill=text_color)

# Save the image
os.makedirs('bidbuygo/static/images', exist_ok=True)
img.save('bidbuygo/static/images/no-image.jpg')

if __name__ == '__main__':
    create_placeholder_image() 