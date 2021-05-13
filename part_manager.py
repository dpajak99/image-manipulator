from tkinter import *
from PIL import Image, ImageTk
from numpy import asarray

from skimage.measure import label
from skimage import filters
from skimage import io


import tkinter as tk
import tkinter.ttk as ttk
import numpy as np
import math

# TODO - Rozdzielić na pliki
# TODO - Dopracować layout
# TODO - Lista dostępnych obrazków / Importowanie własnego?
# TODO - Optymaliiiiiiizacja
# TODO - Opis

class FullImage:
    def __init__(self, path):
        self.path = path
        self.image = Image.open(path)
        # self.image = self.image.resize((128,128), Image.ANTIALIAS)
        self.imageComponent = ImageTk.PhotoImage(self.image)
        self.imageArray = self.getImageArray()
        self.detectedObjects = []

    def getImageArray(self):
        _imageArray = asarray(self.image).copy()
        _imageArray = _imageArray.astype('uint8')
        _imageArray.setflags(write=True)
        return _imageArray

    def refreshImageState(self, image):
        self.image = image.image
        self.imageArray = image.imageArray
        self.detectedObjects = image.detectedObjects
        self.imageComponent = ImageTk.PhotoImage(image.image)

    def labelObjects(self):
        self.imageArray = label(self.imageArray)
        self.imageArray = self.imageArray.astype('uint8')

    def getImageColors(self):
        _allColors = []

        for x in range(1, self.image.size[1] - 1):
            for y in range(1, self.image.size[0] - 1):
                _pixel = self.imageArray[x, y]
                if _pixel != 0 and _pixel not in _allColors:
                    _allColors.append(_pixel)
        return _allColors

    def prettyColors(self):
        _allColors = self.getImageColors()

        _jump = int(200 / len(_allColors))
        for x in range(1, self.image.size[1] - 1):
            for y in range(1, self.image.size[0] - 1):
                if (self.imageArray[x, y] * _jump) > 255:
                    print("Error: Poza zakresem")
                if self.imageArray[x, y] != 0:
                    self.imageArray[x, y] = self.imageArray[x, y] * _jump + 50


def getSmallerImages(image):
    image.labelObjects()
    image.prettyColors()
    image.detectedObjects = getImageObjects(image)
    image.image = Image.fromarray(image.imageArray, "L")
    return image

class ImageL:
    def __init__(self, image, lv, lh, lmax):
        self.image = image
        self.lv = lv
        self.lh = lh
        self.lmax = lmax

def getImageObjects(image):
    _allColors = image.getImageColors()
    _objectArray = []

    for color in _allColors:
        _widthStart = 0
        _widthEnd = 0
        _heightStart = 0
        _heightEnd = 0

        for x in range(1, image.image.size[1] - 1):
            if color in image.imageArray[x]:
                if _heightStart == 0 or x < _heightStart:
                    _heightStart = x
                _heightEnd = x
                for y in range(1, image.image.size[0] - 1):
                    if (_widthStart == 0 or y < _widthStart) and image.imageArray[x, y] == color:
                        _widthStart = y
                    if image.imageArray[x, y] == color and y > _widthEnd:
                        _widthEnd = y

        _object = []
        for x in range(_heightStart - 5, _heightEnd + 5):
            _row = []
            for y in range(_widthStart - 5, _widthEnd + 5):
                if image.imageArray[x, y] == color:
                    _row.append(255)
                else:
                    _row.append(0)
            _object.append(_row)

        _lv = _widthEnd - _widthStart
        _lh = _heightEnd - _heightStart
        _lmax = _lv if _lv > _lh else _lh

        imageL = ImageL(_object, _lv, _lh, _lmax)
        _objectArray.append(imageL)

    return _objectArray


# Wykrywa środek ciężkości
def findCenter(image):
    imageArray = asarray(image).copy()
    imageArray = imageArray.astype('uint8')
    imageArray.setflags(write=True)

    # Inicjalizacja zmiennych
    m00 = 0
    m10 = 0
    m01 = 0

    # Obliczanie momentów geometrycznych
    for x in range(1, image.size[1] - 1):
        for y in range(1, image.size[0] - 1):
            _pixel = 0
            if imageArray[x, y] != 0:
                _pixel = 1
            m00 = m00 + _pixel
            m10 = m10 + (x * _pixel)
            m01 = m01 + (y * _pixel)

    # print(m00)
    # print(m10)
    # print(m01)

    # Wyznaczanie koordynatów środka ciężkości coords[i,j]
    i = int(m10 / m00)
    j = int(m01 / m00)

    # Rysuje plusa w środku ciężkości
    # TODO - Make it better
    imageArray[i, j] = 0
    imageArray[i, j + 1] = 0
    imageArray[i, j - 1] = 0
    imageArray[i, j + 2] = 0
    imageArray[i, j - 2] = 0
    imageArray[i + 1, j] = 0
    imageArray[i - 1, j] = 0
    imageArray[i + 2, j] = 0
    imageArray[i - 2, j] = 0

    # Parsuje 1 na 255 żeby obraz był widoczny
    for x in range(1, image.size[1] - 1):
        for y in range(1, image.size[0] - 1):
            if imageArray[x, y] == 1:
                imageArray[x, y] = 255

    # TODO Poprawić jakoś tą "L" żeby było bardziej unikalne
    transformedImage = Image.fromarray(imageArray, "L")
    return transformedImage, [i, j], [m00, m01, m10]


def prettyWhite(array):
    array = array.astype('uint8')
    for x in range(1, len(array) - 1):
        for y in range(1, len(array[0]) - 1):
            if array[x, y] != 0:
                array[x, y] = 255
    return array


class ImageObject:
    def __init__(self, image, imageEdge, size, surfaceArea, circuit, center, lobject, mParameters):
        self.image = image
        self.imageEdges = imageEdge
        self.size = size
        self.surfaceArea = surfaceArea
        self.circuit = circuit
        self.center = center
        self.lobject = lobject
        self.mParameters = mParameters

        self.w3 = (circuit / (2 * math.sqrt(math.pi * surfaceArea))) - 1
        self.w8 = lobject.lmax / circuit
        self.w9 = (2 * math.sqrt(math.pi * surfaceArea))/circuit
        self.w10 = lobject.lh / lobject.lv



class ListViewRow(tk.Frame):
    def __init__(self, parent, imageObject):
        super().__init__(parent)
        self.grid()

        LABEL_ANCHOR = "w"

        self.columnconfigure(0, minsize=120)
        self.columnconfigure(1, minsize=120)
        self.columnconfigure(2, minsize=200, weight=3)
        self.columnconfigure(3, minsize=250, weight=3)

        self.canvas = Canvas(self, width=imageObject.size[0], height=imageObject.size[1])
        self.canvas.grid(row=1, column=0, rowspan=3,sticky=W)
        self.canvas.create_image(0, 0, anchor=NW, image=imageObject.image)

        self.canvasEdges = Canvas(self, width=imageObject.size[0], height=imageObject.size[1])
        self.canvasEdges.grid(row=1, column=1, rowspan=3,sticky=W)
        self.canvasEdges.create_image(0, 0, anchor=NW, image=imageObject.imageEdges)

        textSurface = "Pole powierzchni: " + str(imageObject.surfaceArea)
        self.surfaceLabel = Label(self, text=textSurface, anchor=LABEL_ANCHOR)
        self.surfaceLabel.grid(row=1, column=2, sticky=W)

        textCircuit = "Obwód: " + str(imageObject.circuit)
        self.circuitLabel = Label(self, text=textCircuit, anchor=LABEL_ANCHOR)
        self.circuitLabel.grid(row=2, column=2,sticky=W)

        textLh = "Lh = " + str(imageObject.lobject.lh)
        self.lhLabel = Label(self, text=textLh, anchor=LABEL_ANCHOR)
        self.lhLabel.grid(row=3, column=2,sticky=W)

        textLv = "Lv = " + str(imageObject.lobject.lv)
        self.lvLabel = Label(self, text=textLv, anchor=LABEL_ANCHOR)
        self.lvLabel.grid(row=4, column=2,sticky=W)

        textLmax = "Lmax = " + str(imageObject.lobject.lmax)
        self.lmaxLabel = Label(self, text=textLmax, anchor=LABEL_ANCHOR)
        self.lmaxLabel.grid(row=5, column=2,sticky=W)

        self.separator = ttk.Separator(self, orient='horizontal')
        self.separator.grid(row=6, column=0, columnspan=6, sticky=EW, pady=10)
        # -------------------------------------------
        textm00 = "m00 = " + str(imageObject.mParameters[0])
        self.m00Label = Label(self, text=textm00)
        self.m00Label.grid(row=1, column=3, sticky=W)

        textm01 = "m01 = " + str(imageObject.mParameters[1])
        self.m01Label = Label(self, text=textm01)
        self.m01Label.grid(row=2, column=3, sticky=W)

        textm10 = "m10 = " + str(imageObject.mParameters[2])
        self.m10Label = Label(self, text=textm10)
        self.m10Label.grid(row=3, column=3, sticky=W)

        textCenter = "Środek ciężkości: (x " + str(imageObject.center[0]) + ", y " + str(imageObject.center[1]) + ")"
        self.centerLabel = Label(self, text=textCenter, anchor=LABEL_ANCHOR)
        self.centerLabel.grid(row=4, column=3,sticky=W)

        #-------------------------------------------
        textW3 = "W3 = " + str(round(imageObject.w3, 2))
        self.w3Label = Label(self, text=textW3)
        self.w3Label.grid(row=1, column=4,sticky=W)

        textW8 = "W8 = " + str(round(imageObject.w8, 2))
        self.w8Label = Label(self, text=textW8)
        self.w8Label.grid(row=2, column=4,sticky=W)

        textW9 = "W9 = " + str(round(imageObject.w9, 2))
        self.w9Label = Label(self, text=textW9)
        self.w9Label.grid(row=3, column=4,sticky=W)

        textW10 = "W10 = " + str(round(imageObject.w10, 2))
        self.w10Label = Label(self, text=textW10)
        self.w10Label.grid(row=4, column=4)


def calcObjectSurface(imageArray):
    surface = 0
    for x in range(1, len(imageArray) - 1):
        for y in range(1, len(imageArray[0]) - 1):
            if imageArray[x, y] != 0:
                surface += 1
    return surface


IMAGE_ARRAY = []
IMAGE_EDGE_ARRAY = []


class ListView(tk.Frame):
    def __init__(self, parent, detectedObjects):
        super().__init__(parent)
        counter = 0

        for lobject in detectedObjects:
            _array = np.array(lobject.image, dtype=np.uint8)
            _edgeArray = filters.roberts(_array)
            _edgeArray = prettyWhite(_edgeArray)

            _image = Image.fromarray(_array, "L")
            _imageEdge = Image.fromarray(_edgeArray, "L")

            _imageSize = _image.size
            _surfaceArea = calcObjectSurface(_array)
            _circuit = calcObjectSurface(_edgeArray)
            # _LArray = getL(_array)

            centerObject = findCenter(_image)
            _image = centerObject[0]
            _centerCoords = centerObject[1]
            _mParameters = centerObject[2]

            _imageComponent = ImageTk.PhotoImage(_image)
            _imageEdgeComponent = ImageTk.PhotoImage(_imageEdge)

            IMAGE_ARRAY.append(_imageComponent)
            IMAGE_EDGE_ARRAY.append(_imageEdgeComponent)

            imageObject = ImageObject(
                image=IMAGE_ARRAY[counter],
                imageEdge=IMAGE_EDGE_ARRAY[counter],
                size=_imageSize,
                surfaceArea=_surfaceArea,
                circuit=_circuit,
                center=_centerCoords,
                lobject=lobject,
                mParameters=_mParameters)
            self.row = ListViewRow(self, imageObject)

            counter += 1

# TODO Obsługa RGB, RGBA itd...
class Window(object):

    def __init__(self):
        self.master = tk.Tk()
        self.master.title('Tytuł aplikacji')
        self.master.maxsize(1500,1000)

        # self.master.geometry("1500x1000")

        # Podział
        self.left_frame = Frame(self.master, width=190, height=800, bg='grey')
        self.left_frame.grid(rowspan=2, column=0, padx=10, pady=5, sticky=N)

        self.center_frame = Frame(self.master, width=800, height= 200, bg='grey')
        self.center_frame.grid(row=0, column=1, padx=150, pady=10, sticky=N)

        self.elements_frame = Frame(self.master, width=800, height= 780, bg='grey')
        self.elements_frame.grid(row=1, column=1, pady=10, sticky=N)

        # self.right_frame = Frame(self.master, width=190, height=800, bg='grey')
        # self.right_frame.grid(rowspan=2, column=2, padx=10, pady=5, sticky=N)

        # Inicjalizacja obrazków z których chcemy korzystać
        # self.listImage1 = FullImage('ksztalty.bmp')
        self.listImage1 = FullImage('indeks1.bmp')
        self.listImage2 = FullImage('indeks2.bmp')
        self.listImage3 = FullImage('center.bmp')
        self.listImage4 = FullImage('center2.bmp')
        self.listImage5 = FullImage('center3.bmp')
        # self.listImage5 = FullImage('center4.bmp')

        self.orginalImage = self.listImage1
        self.transformedImage = self.listImage1

        # Lista obrazków do wyboru

        ttk.Button(self.left_frame, image=self.listImage1.imageComponent, command=self.on_click_image1).grid(column = 0, row = 0, sticky=N + W, pady=5)
        ttk.Button(self.left_frame, image=self.listImage2.imageComponent, command=self.on_click_image2).grid(column = 0, row = 1, sticky=N + W, pady=5)
        ttk.Button(self.left_frame, image=self.listImage3.imageComponent, command=self.on_click_image3).grid(column = 0, row = 2, sticky=N + W, pady=5)
        ttk.Button(self.left_frame, image=self.listImage4.imageComponent, command=self.on_click_image4).grid(column = 0, row = 3, sticky=N + W, pady=5)
        ttk.Button(self.left_frame, image=self.listImage5.imageComponent, command=self.on_click_image5).grid(column = 0, row = 4, sticky=N + W, pady=5)


        # Orginalny obrazek - lewy górny róg
        self.canvasOrginalImage = tk.Canvas(self.center_frame, width=128, height=128)
        self.canvasOrginalImage.grid(row=0, column=0, sticky=W, pady=2)
        self.orginalImageOnCanvas = self.canvasOrginalImage.create_image(0, 0, anchor='nw',
                                                                         image=self.orginalImage.imageComponent)

        # Zmodyfikowany obrazek - prawy górny róg
        self.canvasParsedImage = tk.Canvas(self.center_frame, width=128, height=128)
        self.canvasParsedImage.grid(row=0, column=2, sticky=W, pady=2)
        self.parsedImageOnCanvas = self.canvasParsedImage.create_image(0, 0, anchor='nw',
                                                                       image=self.transformedImage.imageComponent)

        # Button - Wykonaj akcje - lewy dolny róg
        self.listView = ListView(self.elements_frame, self.transformedImage.detectedObjects)
        self.listView.grid(row=0, column=0, sticky=N, pady=10)

        # Button - Wykonaj akcje - lewy dolny róg
        self.button = tk.Button(self.center_frame, width=30, text='Transform', command=self.on_click)
        self.button.grid(row=0, column=1, padx=10)

        # idk
        self.master.mainloop()

    def refresh(self):
        self.listView.destroy()

        self.listView = ListView(self.master, self.transformedImage.detectedObjects)
        self.listView.grid(row=1, column=1, pady=10, sticky=N)

    def on_click(self):
        # Rozjaśnia obrazek
        # self.transformedImage = transformImage(self.transformedImage)

        # Znajduje środek obrazka
        # self.transformedImage = findCenter(self.transformedImage)

        # Wykrywa obiekty na rysunku
        # _image = detectObjects(self.transformedImage.image)
        _image = getSmallerImages(self.transformedImage)

        self.transformedImage.refreshImageState(_image)
        self.canvasParsedImage.itemconfig(self.parsedImageOnCanvas, image=self.transformedImage.imageComponent)
        self.refresh()

    # def on_click_image(self):

    #     self.orginalImage = self.listImage1
    #     self.transformedImage = self.listImage1

    #     self.orginalImageOnCanvas = self.canvasOrginalImage.create_image(0, 0, anchor='nw',
    #                                                                      image=self.listImage1.imageComponent)
    #     self.parsedImageOnCanvas = self.canvasParsedImage.create_image(0, 0, anchor='nw',
    #                                                                    image=self.transformedImage.imageComponent)

    def on_click_image1(self):
        self.orginalImage = self.listImage1
        self.transformedImage = self.listImage1

        self.orginalImageOnCanvas = self.canvasOrginalImage.create_image(0, 0, anchor='nw',
                                                                         image=self.listImage1.imageComponent)
        self.parsedImageOnCanvas = self.canvasParsedImage.create_image(0, 0, anchor='nw',
                                                                       image=self.transformedImage.imageComponent)
        # self.canvasOrginalImage.itemconfig(self.orginalImageOnCanvas,image=self.listImage1.imageComponent)
        # self.canvasParsedImage.itemconfig(self.parsedImageOnCanvas,image=self.listImage1.imageComponent)

    def on_click_image2(self):
        self.orginalImage = self.listImage2
        self.transformedImage = self.listImage2

        self.orginalImageOnCanvas = self.canvasOrginalImage.create_image(0, 0, anchor='nw',
                                                                         image=self.listImage2.imageComponent)
        self.parsedImageOnCanvas = self.canvasParsedImage.create_image(0, 0, anchor='nw',
                                                                       image=self.transformedImage.imageComponent)
        # self.orginalImageOnCanvas = self.canvasOrginalImage.itemconfig(self.orginalImageOnCanvas,image=self.listImage2.imageComponent)
        # self.parsedImageOnCanvas = self.canvasParsedImage.itemconfig(self.parsedImageOnCanvas,image=self.listImage2.imageComponent)

    def on_click_image3(self):
        self.orginalImage = self.listImage3
        self.transformedImage = self.listImage3

        self.orginalImageOnCanvas = self.canvasOrginalImage.create_image(0, 0, anchor='nw',
                                                                         image=self.listImage3.imageComponent)
        self.parsedImageOnCanvas = self.canvasParsedImage.create_image(0, 0, anchor='nw',
                                                                       image=self.transformedImage.imageComponent)
        # self.orginalImageOnCanvas = self.canvasOrginalImage.itemconfig(self.orginalImageOnCanvas,image=self.orginalImage.imageComponent)
        # self.parsedImageOnCanvas = self.canvasParsedImage.itemconfig(self.parsedImageOnCanvas,image=self.transformedImage.imageComponent)

    def on_click_image4(self):
        self.orginalImage = self.listImage4
        self.transformedImage = self.listImage4

        self.orginalImageOnCanvas = self.canvasOrginalImage.create_image(0, 0, anchor='nw',
                                                                         image=self.listImage4.imageComponent)
        self.parsedImageOnCanvas = self.canvasParsedImage.create_image(0, 0, anchor='nw',
                                                                       image=self.transformedImage.imageComponent)
        # self.orginalImageOnCanvas = self.canvasOrginalImage.itemconfig(self.orginalImageOnCanvas,image=self.orginalImage.imageComponent)
        # self.parsedImageOnCanvas = self.canvasParsedImage.itemconfig(self.parsedImageOnCanvas,image=self.transformedImage.imageComponent)


    def on_click_image5(self):
        self.orginalImage = self.listImage5
        self.transformedImage = self.listImage5

        self.orginalImageOnCanvas = self.canvasOrginalImage.create_image(0, 0, anchor='nw',
                                                                         image=self.listImage5.imageComponent)
        self.parsedImageOnCanvas = self.canvasParsedImage.create_image(0, 0, anchor='nw',
                                                                       image=self.transformedImage.imageComponent)
        # self.orginalImageOnCanvas = self.canvasOrginalImage.itemconfig(self.orginalImageOnCanvas,image=self.orginalImage.imageComponent)
        # self.parsedImageOnCanvas = self.canvasParsedImage.itemconfig(self.parsedImageOnCanvas,image=self.transformedImage.imageComponent)


Window()
