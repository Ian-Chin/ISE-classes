from PIL import Image
from PIL import ImageEnhance
from PIL import ImageOps
from member2 import loadImage, createTexture


def convertToRGB(imagePath):
    image = loadImage(imagePath)
    rgbImage = image.convert("RGB")
    return createTexture(rgbImage, "rgbImage")


def convertToRGBA(imagePath):
    image = loadImage(imagePath)
    rgbaImage = image.convert("RGBA")
    return createTexture(rgbaImage, "rgbaImage")


def convertToGrayscale(imagePath):
    image = loadImage(imagePath)
    grayImage = image.convert("L")
    return createTexture(grayImage, "grayImage")


def invertImage(imagePath):
    image = loadImage(imagePath)
    rgbImage = image.convert("RGB")
    invertedImage = ImageOps.invert(rgbImage)
    return createTexture(invertedImage, "invertedImage")


def adjustBrightness(imagePath, brightnessFactor):
    image = loadImage(imagePath)
    enhancer = ImageEnhance.Brightness(image)
    adjustedImage = enhancer.enhance(brightnessFactor)
    return createTexture(adjustedImage, "brightnessImage")


def adjustContrast(imagePath, contrastFactor):
    image = loadImage(imagePath)
    enhancer = ImageEnhance.Contrast(image)
    adjustedImage = enhancer.enhance(contrastFactor)
    return createTexture(adjustedImage, "contrastImage")


def tintImage(imagePath, tintColor):
    image = loadImage(imagePath)
    rgbaImage = image.convert("RGBA")
    tintLayer = Image.new("RGBA", rgbaImage.size, tintColor)
    tintedImage = Image.blend(rgbaImage, tintLayer, 0.35)
    return createTexture(tintedImage, "tintedImage")


def sepiaImage(imagePath):
    # Grayscale first, then map dark-to-light onto brown-to-cream
    image = loadImage(imagePath)
    rgbaImage = image.convert("RGBA")
    grayImage = rgbaImage.convert("L")
    sepiaRGB = ImageOps.colorize(grayImage, black=(40, 20, 0), white=(255, 240, 192))
    sepiaRGB.putalpha(rgbaImage.getchannel("A"))
    return createTexture(sepiaRGB, "sepiaImage")


def getPixelValue(imagePath, xPosition, yPosition):
    image = loadImage(imagePath)
    rgbImage = image.convert("RGB")
    return rgbImage.getpixel((xPosition, yPosition))


def invertPixel(pixelValue):
    redValue = pixelValue[0]
    greenValue = pixelValue[1]
    blueValue = pixelValue[2]
    return (255 - redValue, 255 - greenValue, 255 - blueValue)
