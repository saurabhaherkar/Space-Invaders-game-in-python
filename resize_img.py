from PIL import Image
img = Image.open('yellow_laser.png')
change_img = img.resize((10, 25))
change_img.save('yellow_laser.png')
print(change_img)