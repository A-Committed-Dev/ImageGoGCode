from PIL import Image
import svgutils.transform as sg
import sys
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM



#This function resizes the image to the cordiante scale we want to draw on
#this function can take both svg's and other image files like jpg, and png
def resize_img(img):
    index = img.split(".") #index splits the file from into two pices filename as index 0 and file type as index 1
    if index[1] == "svg": #check if fileytype is svg
        #here we use svgutilils to resize the file to a specified width and height
        fig = sg.fromfile(img)
        fig.set_size(('101','101'))
        fig.save(index[0] + "_resized" + '.svg')

        #here we use svg2rlg to convert the file to a reportlab file and use
        #reportlab to convert the svg files to a pdf file
        drawing = svg2rlg(index[0] + "_resized" + '.svg')
        renderPM.drawToFile(drawing, index[0] + "_resized" + '.png', fmt='PNG')
        return index[0] + "_resized" + '.png' #returns new file name
    else: # if file is not svg
        #here we use pillow as the image processing libary to resize and resave the image as a png.
        image = Image.open(img)
        new_width  = 101
        new_height = 101
        image = image.resize((new_width, new_height))
        image.save(index[0] + "_resized" + '.png')
        return index[0] + "_resized" + '.png' #returns new file name

#this function converts an image to greyscale with the help of pillow
def greyscale(img):
    index = img.split(".")
    image = Image.open(img).convert("L")
    image.save(index[0] + "_greyscale" + ".png")


#this function is used to translate an image cordinate system to a real cordinate system
#origon of an image cordiante system is in the upper left corner of the image
#we need to translate the cordiante posistion to match a standard cordiante system
#where origon is in 0,0 of a noraml x,y cordinate system.
def translate_pixel_coordinates(x, y):
    #this long if statement checks what a given pixel placment is
    #and how it should be translated to a normal cordiante system
    #by chechking which quadrant the pixel is loacated in we can determine
    #how it translates to the real cordinate system
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


#this function converts a greyscaled image to black and white using a specified index
def black_white(img, cIndex):
    index = img.split(".")  #index splits the file from into two pices filename as index 0 and file type as index 1
    image = Image.open(img, 'r').convert("RGB")

    #this for loop runs through every pixel anc checks if the color value of the pixel is higher or lower than the
    #specified color index, depending on if the pixelvalue is higher than the color index
    #the image would be black and if the pixelvalue is lower...
    width, height = image.size
    for x in range(width):
        for y in range(height):
            print(image.getpixel((x,y)))
            if image.getpixel((x,y))[1] >= cIndex:
                image.putpixel( (x,y), (255, 255, 255)) #replace pixel with white
            elif image.getpixel((x,y))[1] <= cIndex:
                image.putpixel( (x,y), (0, 0, 0)) #replace pixel with black
    image.save(index[0] + "_black_white" + ".png")



#this function gets the cordinates of the black pixel we want to draw.
def get_img_cordinates(img):
    image = Image.open(img, 'r').convert("L")

    width, height = image.size
    vectorlist = [] #stores lists of cordiantes for black pixel vectors
    templist = []
    #this for loop runs through every pixel
    for x in range(width):
        for y in range(height):
            if len(templist) >= 99: #here we check if templist is longer than the image height
                templist.append((x, y))
                if len(templist) > 0: #makes sure that templist isnt empty
                    vectorlist.append(templist) #adds the templist to the vectorlist
                    # print(vectorlist)
                templist = [] #creates new instance of templist

            elif image.getpixel((x, y)) == 0: #checks if pixel is black and adds the cordiantes to templist
                templist.append((x, y))

            elif image.getpixel((x,y)) == 255: #checks if pixel is white and adds templist to vectorlist if templist is bigger than 0
                if len(templist) > 0:
                    vectorlist.append(templist)
                templist = [] #creates new instance of templist

    return vectorlist


#this function takes a list of pixel vectors and converts the cordinates to real vectors
def get_real_cordinates(vectorlist):
    vec_cordinates = []
    real_cordinates = []
    for list in vectorlist:
        vec_cordinates.append((list[0], list[len(list) - 1])) #takes the first and last cordiante of the vector
    for list in vec_cordinates:
        #translates the start and end cordinate of the pixel vectors to a real vector and stores them in a list
        real_cordinates.append(
            (translate_pixel_coordinates(list[0][0], list[0][1]),
             translate_pixel_coordinates(list[1][0], list[1][1])))

    return real_cordinates


# this function can convert a list of cordinates into a gcode file
def create_gcode(cordinate_list):
    n = 0 # n refers to line number
    f = open("print.gcode", "a") #we start writing a gcode file


    for cordinate_set in cordinate_list:
        #here we write the start postion of the tool head and set it to start at this point with a vaule of z to 30
        #then lower it self to a value of z to .5
        f.write("N{n} G{g} X{x} Y{y} Z{z}\n".format(n=n, g=0, x=cordinate_set[0][0], y=cordinate_set[0][1], z=30))
        print("N{n} G{g} X{x} Y{y} Z{z}".format(n=n, g=0, x=cordinate_set[0][0], y=cordinate_set[0][1], z=30))
        n += 1 # we add 1 to the line number

        f.write("N{n} G{g} X{x} Y{y} Z{z}\n".format(n=n, g=1, x=cordinate_set[0][0], y=cordinate_set[0][1], z=0.5))
        print("N{n} G{g} X{x} Y{y} Z{z}".format(n=n, g=1, x=cordinate_set[0][0], y=cordinate_set[0][1], z=0.5))
        n += 1
        #here we set the end postion of the tool head and also the point it needs to move to, and raise the toolhead
        #from a value of z to .5 to z to 30.
        f.write("N{n} G{g} X{x} Y{y} Z{z}\n".format(n=n, g=1, x=cordinate_set[1][0], y=cordinate_set[1][1], z=0.5))
        print("N{n} G{g} X{x} Y{y} Z{z}".format(n=n, g=1, x=cordinate_set[1][0], y=cordinate_set[1][1], z=0.5))
        n += 1

        f.write("N{n} G{g} X{x} Y{y} Z{z}\n".format(n=n, g=0, x=cordinate_set[1][0], y=cordinate_set[1][1], z=30))
        print("N{n} G{g} X{x} Y{y} Z{z}".format(n=n, g=0, x=cordinate_set[1][0], y=cordinate_set[1][1], z=30))
        n += 1
    f.close() #we stop writing a gcode file


#--------- run functions under this comment. ----------#

# black_white("duck_resized_greyscale.png")
#create_gcode(get_real_cordinates(get_img_cordinates("1_resized_greyscale_black_white.png")))


# black_white("1_resized_greyscale.png")