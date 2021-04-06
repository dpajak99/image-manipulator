from tkinter import *
from PIL import Image, ImageTk
from numpy import asarray

import tkinter as tk
import numpy as np


def normalizePixel(pixel):
    if pixel < 0:
        pixel = 0
    elif pixel > 255:
        pixel = 255
    return pixel


def transformImage(image):
    imageArray = asarray(image).copy()
    imageArray.setflags(write=True)
    for i in range(image.size[1]):
        for j in range(image.size[0]):
            pixel = imageArray[i, j]
            PARAMETER = 40
            # PNG
            if image.mode == "RGBA":
                imageArray[i, j] = [
                    normalizePixel(pixel[0] + PARAMETER),
                    normalizePixel(pixel[1] + PARAMETER),
                    normalizePixel(pixel[2] + PARAMETER), 255]
            elif image.mode == "RGB":
                imageArray[i, j] = [255, 255, 255]
            # Bitmap
            elif image.mode == "L":
                imageArray[i, j] = normalizePixel(pixel + PARAMETER)

    transformedImage = Image.fromarray(imageArray, image.mode)
    return transformedImage


def getTestImage():
    return ImageTk.PhotoImage(Image.open('image.png'))


def removeFromArray(array, item):
    result = []
    for a in array:
        if a != item:
            result.append(a)
    return result


def detectObjects(image):
    print(image.mode)
    imageArray = asarray(image).copy()
    imageArray = imageArray.astype('uint8')
    imageArray.setflags(write=True)
    gluingTable = [0] * 255
    L = 1
    # TODO Morfilogiczne czyszczenie brzegu, binaryzacja dla obrazów nie-zero-jedynkowych
    for x in range(1, image.size[1] - 1):
        for y in range(1, image.size[0] - 1):
            # Pomijam wartości brzegowe, aby otoczenie zawsze istniało
            neighbors = [int(imageArray[x - 1, y - 1]), int(imageArray[x - 1, y]), int(imageArray[x - 1, y + 1]),
                         int(imageArray[x, y - 1])]
            neighborsSum = sum(neighbors)
            # print(neighbors)
            if imageArray[x, y] != 0:
                if neighborsSum > 0:
                    neighbors = removeFromArray(neighbors, 0)
                    neighborsMin = min(neighbors)
                    neighborsMax = max(neighbors)
                    imageArray[x, y] = neighborsMin
                    gluingTable[neighborsMax] = neighborsMin
                else:
                    imageArray[x, y] = L
                    gluingTable[L] = L
                    L = L + 1
    # Kolorowanie kształtów
    objectsIdentifiers = list(set(gluingTable))
    colorJump = int(200/len(objectsIdentifiers))
    for i in range(len(gluingTable)):
        gluingTable[i] = objectsIdentifiers.index(gluingTable[i]) * colorJump
    for x in range(image.size[1]):
        for y in range(image.size[0]):
            if imageArray[x, y] != 0:
                imageArray[x, y] = int(gluingTable[int(imageArray[x, y])])+50

    transformedImage = Image.fromarray(imageArray, "L")
    return transformedImage


def findCenter(image):
    print(image.mode)
    imageArray = asarray(image).copy()
    imageArray = imageArray.astype('uint8')
    imageArray.setflags(write=True)

    print(imageArray)
    m00 = 0
    m10 = 0
    m01 = 0
    for x in range(1, image.size[1] - 1):
        for y in range(1, image.size[0] - 1):
            m00 = m00 + imageArray[x, y]
            m10 = m10 + (x*imageArray[x, y])
            m01 = m01 + (y*imageArray[x, y])

    print(m00)
    print(m10)
    print(m01)

    i = int(m10/m00)
    j = int(m01/m00)

    print( i, j )

    imageArray[i, j] = 0
    imageArray[i, j+1] = 0
    imageArray[i, j-1] = 0
    imageArray[i, j + 2] = 0
    imageArray[i, j - 2] = 0
    imageArray[i+1, j] = 0
    imageArray[i-1, j] = 0
    imageArray[i+2, j] = 0
    imageArray[i-2, j] = 0

    for x in range(1, image.size[1] - 1):
        for y in range(1, image.size[0] - 1):
            if imageArray[x, y] == 1:
                imageArray[x, y] = 255

    transformedImage = Image.fromarray(imageArray, "L")
    return transformedImage


class MAIN(object):

    def __init__(self):
        self.master = tk.Tk()
        self.master.title('Total Seconds')
        self.master.grid()
        # orginalImage = Image.open('image.png')
        # self.orginalImage = Image.open('lena_gray.bmp')
        self.orginalImage = Image.open('indeks2.bmp')
        self.transformedImage = self.orginalImage

        self.componentOrginalImage = ImageTk.PhotoImage(self.orginalImage)
        self.componentParsedImage = ImageTk.PhotoImage(self.transformedImage)

        self.canvasOrginalImage = tk.Canvas(self.master, width=800, height=800)
        self.canvasOrginalImage.grid(row=1, column=0, sticky=W, pady=2)

        self.canvasParsedImage = tk.Canvas(self.master, width=800, height=800)
        self.canvasParsedImage.grid(row=1, column=1, sticky=W, pady=2)

        self.orginalImageOnCanvas = self.canvasOrginalImage.create_image(0, 0, anchor='nw',
                                                                         image=self.componentOrginalImage)
        self.parsedImageOnCanvas = self.canvasParsedImage.create_image(0, 0, anchor='nw',
                                                                       image=self.componentParsedImage)

        self.button = tk.Button(self.master, width=50, text='Transform', command=self.on_click)
        self.button.grid(row=2, column=0, sticky=W, pady=2)

        self.master.mainloop()

    def on_click(self):
        # self.transformedImage = findCenter(self.transformedImage)
        self.transformedImage = detectObjects(self.transformedImage)

        self.componentParsedImage = ImageTk.PhotoImage(self.transformedImage)
        self.canvasParsedImage.itemconfig(self.parsedImageOnCanvas, image=self.componentParsedImage)

    # --- main ---


MAIN()
