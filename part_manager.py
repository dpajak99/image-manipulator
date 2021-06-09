from tkinter import *

import PIL
from PIL import Image, ImageTk
from numpy import asarray

from skimage.measure import label, regionprops
import copy
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
    def __init__(self, path=0, img=0):
        if path != 0:
            self.path = path
            self.image = Image.open(path)
            # self.image = self.image.resize((128,128), Image.ANTIALIAS)
            self.imageComponent = ImageTk.PhotoImage(self.image)
            self.imageArray = self.getImageArray()
            self.detectedObjects = []
        elif img != 0:
            self.path = img.path
            self.image = img.image
            # self.image = self.image.resize((128,128), Image.ANTIALIAS)
            self.imageComponent = img.imageComponent
            self.imageArray = img.imageArray.copy()
            self.detectedObjects = img.detectedObjects.copy()

    def getImageArray(self):
        _imageArray = asarray(self.image).copy()
        _imageArray = _imageArray.astype('uint8')
        _imageArray.setflags(write=True)
        return _imageArray

    def refreshImageState(self, image):
        self.image = image.image
        self.imageArray = image.imageArray
        self.detectedObjects = image.detectedObjects
        self.imageComponent = image.imageComponent

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
    image.imageComponent = ImageTk.PhotoImage(image.image)
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

        if len(_object) < len(_object[0]):
            blankRow = [0] * len(_object[0])
            status = True
            while len(_object) < len(_object[0]):
                if status:
                    _object.insert(0, blankRow)
                    status = False
                else:
                    _object.insert(len(_object) - 1, blankRow)
                    status = True

        if len(_object) > len(_object[0]):
            status = True
            while len(_object) > len(_object[0]):
                if status:
                    status = False
                else:
                    status = True

                for row in _object:
                    if status:
                        row.insert(0, 0)
                    else:
                        row.append(0)

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
    def __init__(self, image, imageArray, edgeArray, imageEdge, size, surfaceArea, circuit, center, centerToPrint, lobject, mParameters):
        self.image = image
        self.imageArray = imageArray
        self.edgeArray = edgeArray
        self.imageEdges = imageEdge
        self.size = size
        self.surfaceArea = surfaceArea
        self.circuit = circuit
        self.center = center
        self.centerToPrint = centerToPrint
        self.lobject = lobject
        self.mParameters = mParameters
        self.rmin = round(findSizeToCircuit(edgeArray, center[0], center[1])["min"], 2)
        self.rmax = round(findSizeToCircuit(edgeArray, center[0], center[1])["max"], 2)
        self.w1 = 2 * math.sqrt((surfaceArea / math.pi))
        self.w2 = circuit / math.pi
        self.w3 = (circuit / (2 * math.sqrt(math.pi * surfaceArea))) - 1

        w4sum = 0
        for x in range(1, len(edgeArray) - 1):
            for y in range(1, len(edgeArray[0]) - 1):
                if edgeArray[x][y] != 0:
                    w4sum += (pow(x - center[0], 2) + pow(y - center[1], 2))

        self.w4 = surfaceArea / math.sqrt(2 * math.pi*w4sum)

        w5sum = 1
        # for x in range(1, len(imageArray) - 1):
        #     for y in range(1, len(imageArray[0]) - 1):
        #         if imageArray[x][y] != 0:
        #             w5sum += findSizeToCircuit(edgeArray, x, y)["min"]

        # self.w5 = pow(surfaceArea, 3) / pow(w5sum, 2)
        self.w5 = 0

        w6sum1 = 0
        w6sum2 = 0
        for x in range(1, len(imageArray) - 1):
            for y in range(1, len(imageArray[0]) - 1):
                if imageArray[x][y] != 0:
                    w6sum1 += math.sqrt(pow(x - center[0], 2) + pow(y - center[1], 2))
                    w6sum2 += (pow(x - center[0], 2) + pow(y - center[1], 2))

        self.w6 = math.sqrt(pow(w6sum1,2) / ((circuit * w6sum2) -1))
        self.w7 = self.rmin / self.rmax
        self.w8 = lobject.lmax / circuit
        self.w9 = (2 * math.sqrt(math.pi * surfaceArea)) / circuit
        self.w10 = lobject.lh / lobject.lv


class ListViewRow(tk.Frame):
    def __init__(self, parent, imageObject, index):
        super().__init__(parent)
        self.grid()
        self.configure(bg='#eeeeee')

        LABEL_ANCHOR = "w"

        self.columnconfigure(0, minsize=120)
        self.columnconfigure(1, minsize=120)
        self.columnconfigure(2, minsize=200)
        self.columnconfigure(3, minsize=250)
        self.columnconfigure(4, minsize=250)

        self.titleLabel = Label(self, text="Znaleziony obiekt " + str(index + 1))
        self.titleLabel.grid(row=0, column=0, columnspan=2, sticky=W)

        self.canvas = Canvas(self, width=imageObject.size[0], height=imageObject.size[1])
        self.canvas.grid(row=1, column=0, rowspan=6, sticky=W)
        self.canvas.create_image(0, 0, anchor=NW, image=imageObject.image)

        self.canvasEdges = Canvas(self, width=imageObject.size[0], height=imageObject.size[1])
        self.canvasEdges.grid(row=1, column=1, rowspan=6, sticky=W)
        self.canvasEdges.create_image(0, 0, anchor=NW, image=imageObject.imageEdges)

        textSurface = "Pole powierzchni: " + str(imageObject.surfaceArea)
        self.surfaceLabel = Label(self, text=textSurface)
        self.surfaceLabel.grid(row=1, column=2, sticky=NW)

        textCircuit = "Obwód: " + str(imageObject.circuit)
        self.circuitLabel = Label(self, text=textCircuit)
        self.circuitLabel.grid(row=2, column=2, sticky=NW)

        textLh = "Lh = " + str(imageObject.lobject.lh)
        self.lhLabel = Label(self, text=textLh)
        self.lhLabel.grid(row=3, column=2, sticky=NW)

        textLv = "Lv = " + str(imageObject.lobject.lv)
        self.lvLabel = Label(self, text=textLv)
        self.lvLabel.grid(row=4, column=2, sticky=NW)

        textLmax = "Lmax = " + str(imageObject.lobject.lmax)
        self.lmaxLabel = Label(self, text=textLmax)
        self.lmaxLabel.grid(row=5, column=2, sticky=NW)

        self.separator = ttk.Separator(self, orient='horizontal')
        self.separator.grid(row=10, column=0, columnspan=6, sticky=EW)
        # -------------------------------------------
        textm00 = "m00 = " + str(imageObject.mParameters[0])
        self.m00Label = Label(self, text=textm00)
        self.m00Label.grid(row=1, column=3, sticky=NW)

        textm01 = "m01 = " + str(imageObject.mParameters[1])
        self.m01Label = Label(self, text=textm01)
        self.m01Label.grid(row=2, column=3, sticky=NW)

        textm10 = "m10 = " + str(imageObject.mParameters[2])
        self.m10Label = Label(self, text=textm10)
        self.m10Label.grid(row=3, column=3, sticky=NW)

        textRmin = "rmin = " + str(imageObject.rmin)
        self.rminlabel = Label(self, text=textRmin)
        self.rminlabel.grid(row=4, column=3, sticky=NW)

        textRmax = "Rmax = " + str(imageObject.rmax)
        self.rmaxlabel = Label(self, text=textRmax)
        self.rmaxlabel.grid(row=5, column=3, sticky=NW)

        textCenter = "Środek ciężkości: (x " + str(imageObject.centerToPrint[0]) + ", y " + str(imageObject.centerToPrint[1]) + ")"
        self.centerLabel = Label(self, text=textCenter)
        self.centerLabel.grid(row=6, column=3, sticky=NW)

        # -------------------------------------------
        textW1 = "W1 = " + str(round(imageObject.w1, 2))
        self.w1Label = Label(self, text=textW1)
        self.w1Label.grid(row=1, column=4, sticky=NW)

        textW2 = "W2 = " + str(round(imageObject.w2, 2))
        self.w2Label = Label(self, text=textW2)
        self.w2Label.grid(row=2, column=4, sticky=NW)

        textW3 = "W3 = " + str(round(imageObject.w3, 2))
        self.w3Label = Label(self, text=textW3)
        self.w3Label.grid(row=3, column=4, sticky=NW)

        textW4 = "W4 = " + str(round(imageObject.w4, 2))
        self.w4Label = Label(self, text=textW4)
        self.w4Label.grid(row=4, column=4, sticky=NW)

        textW5 = "W5 = " + str(round(imageObject.w5, 2))
        self.w5Label = Label(self, text=textW5)
        self.w5Label.grid(row=5, column=4, sticky=NW)

        textW6 = "W6 = " + str(round(imageObject.w6, 2))
        self.w6Label = Label(self, text=textW6)
        self.w6Label.grid(row=1, column=5, sticky=NW)

        textW8 = "W7 = " + str(round(imageObject.w7, 2))
        self.w7Label = Label(self, text=textW8)
        self.w7Label.grid(row=2, column=5, sticky=NW)

        textW8 = "W8 = " + str(round(imageObject.w8, 2))
        self.w8Label = Label(self, text=textW8)
        self.w8Label.grid(row=3, column=5, sticky=NW)

        textW9 = "W9 = " + str(round(imageObject.w9, 2))
        self.w9Label = Label(self, text=textW9)
        self.w9Label.grid(row=4, column=5, sticky=NW)

        textW10 = "W10 = " + str(round(imageObject.w10, 2))
        self.w10Label = Label(self, text=textW10)
        self.w10Label.grid(row=5, column=5, sticky=NW)

        self.titleLabel.config(bg="#eeeeee")
        self.surfaceLabel.config(bg="#eeeeee")
        self.circuitLabel.config(bg="#eeeeee")
        self.lhLabel.config(bg="#eeeeee")
        self.lvLabel.config(bg="#eeeeee")
        self.lmaxLabel.config(bg="#eeeeee")
        self.m00Label.config(bg="#eeeeee")
        self.m01Label.config(bg="#eeeeee")
        self.m10Label.config(bg="#eeeeee")
        self.centerLabel.config(bg="#eeeeee")
        self.w1Label.config(bg="#eeeeee")
        self.w2Label.config(bg="#eeeeee")
        self.w3Label.config(bg="#eeeeee")
        self.w4Label.config(bg="#eeeeee")
        self.w5Label.config(bg="#eeeeee")
        self.w6Label.config(bg="#eeeeee")
        self.w7Label.config(bg="#eeeeee")
        self.w8Label.config(bg="#eeeeee")
        self.w9Label.config(bg="#eeeeee")
        self.w10Label.config(bg="#eeeeee")


def findSizeToCircuit(imageCircuitArray, fromX, fromY):
    surface = 0

    minSize = 99999
    maxSize = 0

    for x in range(0, len(imageCircuitArray) - 1):
        for y in range(0, len(imageCircuitArray[0]) - 1):
            if imageCircuitArray[x, y] == 255:
                localSize = math.sqrt(pow(x - fromX, 2) + pow(y - fromY, 2))
                if localSize < minSize:
                    minSize = localSize
                if localSize > maxSize:
                    maxSize = localSize

    print( fromX, fromY , "MIN: ", minSize, "MAX: ", maxSize)
    return {
        "max": maxSize,
        "min": minSize
    }


IMAGE_ARRAY = []
IMAGE_EDGE_ARRAY = []


class ListView(tk.Frame):
    def __init__(self, parent, detectedObjects):
        super().__init__(parent)
        counter = 0
        IMAGE_ARRAY.clear()
        IMAGE_EDGE_ARRAY.clear()

        self.elements_frame = Frame(self,  width=1100, height=780, bg='#eeeeee')
        self.elements_frame.grid(row=1, column=1, pady=20, padx=20, sticky=N)

        self.elements_content = Frame(self, width=1050, height=650, bg='#eeeeee')
        self.elements_content.grid(row=1, column=1, pady=20, padx=20, sticky=N)

        for lobject in detectedObjects:
            _array = np.array(lobject.image, dtype=np.uint8)
            _regionprops = regionprops(_array)
            print("Area", _regionprops[0]['Area'])
            print("Centeroid", _regionprops[0]['Centroid'][0])
            print("Perimeter", )
            _edgeArray = filters.roberts(_array).astype('uint8')
            _edgeArray = prettyWhite(_edgeArray)

            _image = Image.fromarray(_array, "L").resize((100, 100))
            _imageEdge = Image.fromarray(_edgeArray, "L").resize((100, 100))

            _imageSize = _image.size
            _surfaceArea = round(_regionprops[0]['Area'])
            _circuit = round(_regionprops[0]['Perimeter'])
            # _LArray = getL(_array)

            centerObject = findCenter(_image)
            _image = centerObject[0]
            _centerCoordsToPrint = centerObject[1]
            _centerCoords = [round(_regionprops[0]['Centroid'][0]), round(_regionprops[0]['Centroid'][1])]
            _mParameters = centerObject[2]

            _imageComponent = ImageTk.PhotoImage(_image)
            _imageEdgeComponent = ImageTk.PhotoImage(_imageEdge)

            IMAGE_ARRAY.append(_imageComponent)
            IMAGE_EDGE_ARRAY.append(_imageEdgeComponent)

            imageObject = ImageObject(
                image=IMAGE_ARRAY[counter],
                imageArray=_array,
                edgeArray=_edgeArray,
                imageEdge=IMAGE_EDGE_ARRAY[counter],
                size=_imageSize,
                surfaceArea=_surfaceArea,
                circuit=_circuit,
                center=_centerCoords,
                centerToPrint=_centerCoordsToPrint,
                lobject=lobject,
                mParameters=_mParameters)
            self.row = ListViewRow(self.elements_content, imageObject, counter)

            counter += 1


# TODO Obsługa RGB, RGBA itd...
class Window(object):

    def __init__(self):
        self.master = tk.Tk()
        self.master.title('Tytuł aplikacji')
        self.master.maxsize(1500, 1000)

        # self.master.geometry("1500x1000")

        # Podział
        self.left_frame = Frame(self.master, width=190, height=800)
        self.left_frame.grid(rowspan=2, column=0, padx=10, pady=5, sticky=N)

        self.center_frame = Frame(self.master, width=800, height=200)
        self.center_frame.grid(row=0, column=1, padx=0, pady=10, sticky=N)

        self.elements_frame = Frame(self.master, width=800, height=780)
        self.elements_frame.grid(row=1, column=1, pady=10, sticky=N)

        # self.right_frame = Frame(self.master, width=190, height=800, bg='grey')
        # self.right_frame.grid(rowspan=2, column=2, padx=10, pady=5, sticky=N)

        # Inicjalizacja obrazków z których chcemy korzystać
        # self.listImage1 = FullImage('ksztalty.bmp')
        self.listImage1 = FullImage(path='indeks1.bmp')
        self.listImage2 = FullImage(path='indeks2.bmp')
        self.listImage3 = FullImage(path='center.bmp')
        self.listImage4 = FullImage(path='center2.bmp')
        self.listImage5 = FullImage(path='center3.bmp')
        self.listImage6 = FullImage(path='center4.bmp')
        # self.listImage5 = FullImage('center4.bmp')

        self.setup_new_image(self.listImage1)

        # Lista obrazków do wyboru

        self.refresh_image_state()

        # Orginalny obrazek - lewy górny róg
        self.canvasOrginalImage = tk.Canvas(self.center_frame, width=128, height=128)
        self.canvasOrginalImage.grid(row=0, column=0, sticky=N, pady=2)
        self.orginalImageOnCanvas = self.canvasOrginalImage.create_image(0, 0, anchor='nw',
                                                                         image=self.orginalImage.imageComponent)

        self.orginalImageLabel = Label(self.center_frame, text="Obrazek orginalny")
        self.orginalImageLabel.grid(row=1, column=0, sticky=N)

        # Zmodyfikowany obrazek - prawy górny róg
        self.canvasParsedImage = tk.Canvas(self.center_frame, width=128, height=128)
        self.canvasParsedImage.grid(row=0, column=2, sticky=N, pady=2)
        self.parsedImageOnCanvas = self.canvasParsedImage.create_image(0, 0, anchor='nw',
                                                                       image=self.transformedImage.imageComponent)

        self.parsedImageLabel = Label(self.center_frame, text="Obrazek zaindeksowany\n(po wykonaniu operacji)")
        self.parsedImageLabel.grid(row=1, column=2, sticky=N)

        # Button - Wykonaj akcje - lewy dolny róg
        self.listView = ListView(self.elements_frame, self.transformedImage.detectedObjects)
        self.listView.grid(row=0, column=0, sticky=N, pady=10)

        # Button - Wykonaj akcje - lewy dolny róg
        self.button = tk.Button(self.center_frame, width=30, text='Transform', command=self.on_click)
        self.button.grid(row=0, column=1, padx=10)

        # idk
        self.master.mainloop()

    def refresh_image_state(self):
        ttk.Button(self.left_frame, image=self.listImage1.imageComponent,
                   command=lambda: self.on_click_image(self.listImage1, 1)).grid(column=0, row=0, sticky=N + W, pady=5)
        ttk.Button(self.left_frame, image=self.listImage2.imageComponent,
                   command=lambda: self.on_click_image(self.listImage2, 2)).grid(column=0, row=1, sticky=N + W, pady=5)
        ttk.Button(self.left_frame, image=self.listImage3.imageComponent,
                   command=lambda: self.on_click_image(self.listImage3, 3)).grid(column=0, row=2, sticky=N + W, pady=5)
        ttk.Button(self.left_frame, image=self.listImage4.imageComponent,
                   command=lambda: self.on_click_image(self.listImage4, 4)).grid(column=0, row=3, sticky=N + W, pady=5)
        ttk.Button(self.left_frame, image=self.listImage5.imageComponent,
                   command=lambda: self.on_click_image(self.listImage5, 5)).grid(column=0, row=4, sticky=N + W, pady=5)
        ttk.Button(self.left_frame, image=self.listImage6.imageComponent,
                   command=lambda: self.on_click_image(self.listImage6, 5)).grid(column=0, row=5, sticky=N + W, pady=5)

    def refreshList(self):
        self.listView.destroy()

        self.listView = ListView(self.master, self.transformedImage.detectedObjects)
        self.listView.grid(row=1, column=1, pady=10, sticky=N)

    def on_click(self):
        _image = FullImage(img=getSmallerImages(self.transformedImage))

        self.transformedImage.refreshImageState(_image)
        self.canvasParsedImage.itemconfig(self.parsedImageOnCanvas, image=_image.imageComponent)
        self.refreshList()

    def setup_new_image(self, image):
        newImage = FullImage(img=image)
        self.orginalImage = newImage
        self.transformedImage = newImage
        return newImage

    def on_click_image(self, image, index):
        newImage = self.setup_new_image(image)

        self.orginalImage.refreshImageState(newImage)
        self.transformedImage.refreshImageState(newImage)

        self.canvasOrginalImage.itemconfig(self.orginalImageOnCanvas, image=newImage.imageComponent)
        self.canvasParsedImage.itemconfig(self.parsedImageOnCanvas, image=newImage.imageComponent)
        self.refreshList()
        # self.orginalImageOnCanvas = self.canvasOrginalImage.itemconfig(self.orginalImageOnCanvas,image=self.orginalImage.imageComponent)
        # self.parsedImageOnCanvas = self.canvasParsedImage.itemconfig(self.parsedImageOnCanvas,image=self.transformedImage.imageComponent)


Window()
