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


def getImageObjects(image):
    _allColors = image.getImageColors()
    _objectArray = []
    _LArray = []

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
        _objectArray.append(_object)
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
            m00 = m00 + imageArray[x, y]
            m10 = m10 + (x * imageArray[x, y])
            m01 = m01 + (y * imageArray[x, y])

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
    return transformedImage, [i, j]


def prettyWhite(array):
    array = array.astype('uint8')
    for x in range(1, len(array) - 1):
        for y in range(1, len(array[0]) - 1):
            if array[x, y] != 0:
                array[x, y] = 255
    return array


class ImageObject:
    def __init__(self, image, imageEdge, size, surfaceArea, circuit, center):
        self.image = image
        self.imageEdges = imageEdge
        self.size = size
        self.surfaceArea = surfaceArea
        self.circuit = circuit
        self.center = center

        self.w3 = (circuit / (2 * math.sqrt(math.pi * surfaceArea))) - 1
        self.w9 = (2 * math.sqrt(math.pi * surfaceArea))/circuit


class ListViewRow(tk.Frame):
    def __init__(self, parent, imageObject):
        super().__init__(parent)
        self.grid()

        self.columnconfigure(0, minsize=120)
        self.columnconfigure(1, minsize=120)

        self.canvas = Canvas(self, width=imageObject.size[0], height=imageObject.size[1])
        self.canvas.grid(row=1, column=0, rowspan=3)
        self.canvas.create_image(0, 0, anchor=NW, image=imageObject.image)

        self.canvasEdges = Canvas(self, width=imageObject.size[0], height=imageObject.size[1])
        self.canvasEdges.grid(row=1, column=1, rowspan=3)
        self.canvasEdges.create_image(0, 0, anchor=NW, image=imageObject.imageEdges)

        textSurface = "Pole powierzchni: " + str(imageObject.surfaceArea)
        self.surfaceLabel = Label(self, text=textSurface)
        self.surfaceLabel.grid(row=1, column=2)

        textCircuit = "Obwód: " + str(imageObject.circuit)
        self.circuitLabel = Label(self, text=textCircuit)
        self.circuitLabel.grid(row=2, column=2)

        textCenter = "Środek ciężkości: (x " + str(imageObject.center[0]) + ", y " + str(imageObject.center[1]) + ")"
        self.centerLabel = Label(self, text=textCenter)
        self.centerLabel.grid(row=3, column=2)

        #-------------------------------------------
        textW3 = "W3 = " + str(round(imageObject.w3, 2))
        self.w3Label = Label(self, text=textW3)
        self.w3Label.grid(row=1, column=3)

        textW9 = "W9 = " + str(round(imageObject.w9, 2))
        self.w9Label = Label(self, text=textW9)
        self.w9Label.grid(row=2, column=3)


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

        for imageArray in detectedObjects:
            _array = np.array(imageArray, dtype=np.uint8)
            _edgeArray = filters.roberts(_array)
            _edgeArray = prettyWhite(_edgeArray)

            _image = Image.fromarray(_array, "L")
            _imageEdge = Image.fromarray(_edgeArray, "L")

            _imageSize = _image.size
            _surfaceArea = calcObjectSurface(_array)
            _circuit = calcObjectSurface(_edgeArray)

            centerObject = findCenter(_image)
            _image = centerObject[0]
            _centerCoords = centerObject[1]

            _imageComponent = ImageTk.PhotoImage(_image)
            _imageEdgeComponent = ImageTk.PhotoImage(_imageEdge)

            IMAGE_ARRAY.append(_imageComponent)
            IMAGE_EDGE_ARRAY.append(_imageEdgeComponent)

            imageObject = ImageObject(IMAGE_ARRAY[counter], IMAGE_EDGE_ARRAY[counter], _imageSize, _surfaceArea,
                                      _circuit, _centerCoords)
            self.row = ListViewRow(self, imageObject)

            counter += 1


# TODO Obsługa RGB, RGBA itd...
class Window(object):

    def __init__(self):
        self.master = tk.Tk()
        self.master.title('Tytuł aplikacji')
        self.master.grid()

        IMAGE_PATH = 'indeks2.bmp'

        # Inicjalizacja obrazka z którego chcemy korzystać
        self.orginalImage = FullImage(IMAGE_PATH)
        self.transformedImage = FullImage(IMAGE_PATH)

        # Orginalny obrazek - lewy górny róg
        self.canvasOrginalImage = tk.Canvas(self.master, width=200, height=200)
        self.canvasOrginalImage.grid(row=1, column=0, sticky=W, pady=2)
        self.orginalImageOnCanvas = self.canvasOrginalImage.create_image(0, 0, anchor='nw',
                                                                         image=self.orginalImage.imageComponent)

        # Zmodyfikowany obrazek - prawy górny róg
        self.canvasParsedImage = tk.Canvas(self.master, width=200, height=200)
        self.canvasParsedImage.grid(row=1, column=1, sticky=W, pady=2)
        self.parsedImageOnCanvas = self.canvasParsedImage.create_image(0, 0, anchor='nw',
                                                                       image=self.transformedImage.imageComponent)

        # Button - Wykonaj akcje - lewy dolny róg
        self.listView = ListView(self.master, self.transformedImage.detectedObjects)
        self.listView.grid(row=2, column=0, sticky=W, pady=2)

        # Button - Wykonaj akcje - lewy dolny róg
        self.button = tk.Button(self.master, width=50, text='Transform', command=self.on_click)
        self.button.grid(row=3, column=0, sticky=N + W, pady=20)

        # idk
        self.master.mainloop()

    def refresh(self):
        self.listView.destroy()

        self.listView = ListView(self.master, self.transformedImage.detectedObjects)
        self.listView.grid(row=2, column=0, sticky=W, pady=2)

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


Window()
