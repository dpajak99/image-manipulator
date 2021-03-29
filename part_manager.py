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
    imageArray[0, 0] = 4
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


class MAIN(object):

    def __init__(self):
        self.master = tk.Tk()
        self.master.title('Total Seconds')
        # orginalImage = Image.open('image.png')
        self.orginalImage = Image.open('lena_gray.bmp')
        self.transformedImage = self.orginalImage

        self.componentOrginalImage = ImageTk.PhotoImage(self.orginalImage)
        self.componentParsedImage = ImageTk.PhotoImage(self.transformedImage)

        self.canvasOrginalImage = tk.Canvas(self.master, width=400, height=400)
        self.canvasOrginalImage.pack()

        self.canvasParsedImage = tk.Canvas(self.master, width=400, height=400)
        self.canvasParsedImage.pack()

        self.orginalImageOnCanvas = self.canvasOrginalImage.create_image(0, 0, anchor='nw',
                                                                         image=self.componentOrginalImage)
        self.parsedImageOnCanvas = self.canvasParsedImage.create_image(0, 0, anchor='nw',
                                                                       image=self.componentParsedImage)

        self.button = tk.Button(self.master, width=50, text='Transform', command=self.on_click)
        self.button.pack()

        self.master.mainloop()

    def on_click(self):
        self.transformedImage = transformImage(self.transformedImage)
        self.componentParsedImage = ImageTk.PhotoImage(self.transformedImage)
        self.canvasParsedImage.itemconfig(self.parsedImageOnCanvas, image=self.componentParsedImage)

    # --- main ---


MAIN()
