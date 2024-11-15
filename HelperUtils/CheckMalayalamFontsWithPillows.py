from PIL import Image, ImageDraw, ImageFont

# Example of loading the Meera font
font_path = "C:\\ExtraFonts\\noto-sans-malayalam\\NotoSansMalayalam-VariableFont_wdth,wght.ttf"  # Update the path to where your font is located
font_size = 50
font_color = "white"

image = Image.new('RGB', (500, 300), color='black')
draw = ImageDraw.Draw(image)

font = ImageFont.truetype(font_path, font_size)
text = "സ്വർഗ്ഗസ്ഥനായ ഞങ്ങളുടെ പിതാവേ, അങ്ങയുടെ നാമം പൂജിതമാകണമേ, അങ്ങയുടെ രാജ്യം വരേണമേ,"  # Malayalam text

draw.text((100, 100), text, font=font, fill=font_color)
image.show()  # Or save the image
# image.save('output.png')  # Uncomment to save the image
