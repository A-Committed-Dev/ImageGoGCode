from PIL import Image
import svgutils.transform as sg
import sys
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM




def resize_img(img):
    index = img.split(".")
    if index[1] == "svg":
        fig = sg.fromfile(img)
        fig.set_size(('101','101'))
        fig.save(index[0] + "_resized" + '.svg')

        drawing = svg2rlg(index[0] + "_resized" + '.svg')
        renderPM.drawToFile(drawing, index[0] + "_resized" + '.png', fmt='PNG')
        return index[0] + "_resized" + '.png'
    else:
        image = Image.open(img)
        new_width  = 101
        new_height = 101
        image = image.resize((new_width, new_height))
        image.save(index[0] + "_resized" + '.png')
        return index[0] + "_resized" + '.png'


def greyscale(img):
    index = img.split(".")
    image = Image.open(img).convert("L")
    image.save(index[0] + "_greyscale" + ".png")


def translate_pixel_coordinates(x, y):
    if x < 50 and y < 50:
        y = 50 - y
        x -= 50
        return x, y
    elif x > 50 and y < 50:
        y = 50 - y
        x = x - 50
        return x, y
    elif x < 50 and y > 50:
        y = 50 - y
        x -= 50
        return x, y
    elif x > 50 and y > 50:
        y = 50 - y
        x = x - 50
        return x, y
    elif x == 50 and y == 50:
        x = x - x
        y = y - y
        return x, y
    elif x == 50 and y < 50:
        x = x - x
        y = 50 - y
        return x, y
    elif x == 50 and y > 50:
        x = x - x
        y = 50 - y
        return x, y
    elif x < 50 and y == 50:
        x = x - 50
        y = y - y
        return x, y
    elif x > 50 and y == 50:
        x = x - 50
        y = y - y
        return x, y



def black_white(img):
    index = img.split(".")
    image = Image.open(img, 'r').convert("RGB")
    width, height = image.size
    for x in range(width):
        for y in range(height):
            print(image.getpixel((x,y)))
            if image.getpixel((x,y))[1] >= 130:
                image.putpixel( (x,y), (255, 255, 255))
            if image.getpixel((x,y))[1] <= 130:
                image.putpixel( (x,y), (0, 0, 0))
    image.save(index[0] + "_black_white" + ".png")




def get_img_cordinates(img):
    image = Image.open(img, 'r').convert("L")
    width, height = image.size
    vectorlist = []
    templist = []
    for x in range(width):
        for y in range(height):
            if len(templist) >= 99:
                templist.append((x, y))
                if len(templist) > 0:
                    vectorlist.append(templist)
                    # print(vectorlist)
                templist = []

            elif image.getpixel((x, y)) == 0:
                templist.append((x, y))

            elif image.getpixel((x,y)) == 255:
                if len(templist) > 0:
                    vectorlist.append(templist)
                templist = []

    return vectorlist

def get_real_cordinates(vectorlist):
    vec_cordinates = []
    real_cordinates = []
    for list in vectorlist:
        vec_cordinates.append((list[0], list[len(list) - 1]))
    for list in vec_cordinates:
        real_cordinates.append(
            (translate_pixel_coordinates(list[0][0], list[0][1]), translate_pixel_coordinates(list[1][0], list[1][1])))
        # real_cordinates.append(translate_pixel_coordinates(list[0][0],list[0][1]))
        # real_cordinates.append(translate_pixel_coordinates(list[1][0], list[1][1]))
    return real_cordinates

def create_gcode(cordinate_list):
    n = 0
    f = open("print.gcode", "a")


    for cordinate_set in cordinate_list:
        # print(cordinate_set)
        f.write("N{n} G{g} X{x} Y{y} Z{z}\n".format(n=n, g=0, x=cordinate_set[0][0], y=cordinate_set[0][1], z=30))
        print("N{n} G{g} X{x} Y{y} Z{z}".format(n=n, g=0, x=cordinate_set[0][0], y=cordinate_set[0][1], z=30))
        n += 1
        f.write("N{n} G{g} X{x} Y{y} Z{z}\n".format(n=n, g=1, x=cordinate_set[0][0], y=cordinate_set[0][1], z=0.5))
        print("N{n} G{g} X{x} Y{y} Z{z}".format(n=n, g=1, x=cordinate_set[0][0], y=cordinate_set[0][1], z=0.5))
        n += 1
        f.write("N{n} G{g} X{x} Y{y} Z{z}\n".format(n=n, g=1, x=cordinate_set[1][0], y=cordinate_set[1][1], z=0.5))
        print("N{n} G{g} X{x} Y{y} Z{z}".format(n=n, g=1, x=cordinate_set[1][0], y=cordinate_set[1][1], z=0.5))
        n += 1
        f.write("N{n} G{g} X{x} Y{y} Z{z}\n".format(n=n, g=0, x=cordinate_set[1][0], y=cordinate_set[1][1], z=30))
        print("N{n} G{g} X{x} Y{y} Z{z}".format(n=n, g=0, x=cordinate_set[1][0], y=cordinate_set[1][1], z=30))
        n += 1
    f.close()
# black_white("duck_resized_greyscale.png")
create_gcode(get_real_cordinates(get_img_cordinates("1_resized_greyscale_black_white.png")))


# black_white("1_resized_greyscale.png")