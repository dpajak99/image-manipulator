from tkinter import *
from PIL import Image, ImageTk
from numpy import asarray

import tkinter as tk

# TODO - Rozdzielić na pliki
# TODO - Dopracować layout
# TODO - Lista dostępnych obrazków / Importowanie własnego?
# TODO - Optymaliiiiiiizacja
# TODO - Opis

# Normalizuje pojedynczy piksel
def normalizePixel(pixel):
    if pixel < 0:
        pixel = 0
    elif pixel > 255:
        pixel = 255
    return pixel


# Nieużywana metoda - służy mi jako baza, którą sobie napisałem na samym początku. Rozjaśnia obrazek
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


# Kasuje element z tablicy
def removeFromArray(array, item):
    result = []
    for a in array:
        if a != item:
            result.append(a)
    return result


# Wykrywa i "kataloguje" obiekty na rysunku
def detectObjects(image):
    print(image.mode)
    imageArray = asarray(image).copy()
    imageArray = imageArray.astype('uint8')
    imageArray.setflags(write=True)
    # Inicjalizacja zmiennych
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
            # Wypełnianie tablicy sklejeń
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
    # Nadawanie wartości zgodnie z tablicą sklejeń
    for x in range(image.size[1]):
        for y in range(image.size[0]):
            if imageArray[x, y] != 0:
                imageArray[x, y] = int(gluingTable[int(imageArray[x, y])])+50

    transformedImage = Image.fromarray(imageArray, "L")
    return transformedImage


# Wykrywa środek ciężkości
def findCenter(image):
    print(image.mode)
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
            m10 = m10 + (x*imageArray[x, y])
            m01 = m01 + (y*imageArray[x, y])

    print(m00)
    print(m10)
    print(m01)

    # Wyznaczanie koordynatów środka ciężkości coords[i,j]
    i = int(m10/m00)
    j = int(m01/m00)

    print( i, j )

    # Rysuje plusa w środku ciężkości
    # TODO - Make it better
    imageArray[i, j] = 0
    imageArray[i, j+1] = 0
    imageArray[i, j-1] = 0
    imageArray[i, j + 2] = 0
    imageArray[i, j - 2] = 0
    imageArray[i+1, j] = 0
    imageArray[i-1, j] = 0
    imageArray[i+2, j] = 0
    imageArray[i-2, j] = 0

    # Parsuje 1 na 255 żeby obraz był widoczny
    for x in range(1, image.size[1] - 1):
        for y in range(1, image.size[0] - 1):
            if imageArray[x, y] == 1:
                imageArray[x, y] = 255

    # TODO Poprawić jakoś tą "L" żeby było bardziej unikalne
    transformedImage = Image.fromarray(imageArray, "L")
    return transformedImage


# TODO Obsługa RGB, RGBA itd...
class MAIN(object):

    def __init__(self):
        self.master = tk.Tk()
        self.master.title('Tytuł aplikacji')
        self.master.grid()

        # Inicjalizacja obrazka z którego chcemy korzystać
        self.orginalImage = Image.open('indeks2.bmp')
        self.transformedImage = self.orginalImage

        self.componentOrginalImage = ImageTk.PhotoImage(self.orginalImage)
        self.componentParsedImage = ImageTk.PhotoImage(self.transformedImage)

        # Orginalny obrazek - lewy górny róg
        self.canvasOrginalImage = tk.Canvas(self.master, width=800, height=800)
        self.canvasOrginalImage.grid(row=1, column=0, sticky=W, pady=2)
        self.orginalImageOnCanvas = self.canvasOrginalImage.create_image(0, 0, anchor='nw', image=self.componentOrginalImage)

        # Zmodyfikowany obrazek - prawy górny róg
        self.canvasParsedImage = tk.Canvas(self.master, width=800, height=800)
        self.canvasParsedImage.grid(row=1, column=1, sticky=W, pady=2)
        self.parsedImageOnCanvas = self.canvasParsedImage.create_image(0, 0, anchor='nw', image=self.componentParsedImage)

        # Button - Wykonaj akcje - lewy dolny róg
        self.button = tk.Button(self.master, width=50, text='Transform', command=self.on_click)
        self.button.grid(row=2, column=0, sticky=W, pady=2)

        # idk
        self.master.mainloop()

    def on_click(self):
        # Rozjaśnia obrazek
        # self.transformedImage = transformImage(self.transformedImage)

        # Znajduje środek obrazka
        # self.transformedImage = findCenter(self.transformedImage)

        # Wykrywa obiekty na rysunku
        self.transformedImage = detectObjects(self.transformedImage)

        self.componentParsedImage = ImageTk.PhotoImage(self.transformedImage)
        self.canvasParsedImage.itemconfig(self.parsedImageOnCanvas, image=self.componentParsedImage)

    # --- main ---


MAIN()
