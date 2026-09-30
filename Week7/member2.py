from PIL import Image
from PIL import ImageFilter
import arcade


def loadImage(imagePath):
    return Image.open(imagePath)


def createTexture(image, textureName):
    image = image.convert("RGBA")
    return arcade.Texture(image, hash=textureName)


def applyBlur(imagePath):
    image = loadImage(imagePath)
    blurredImage = image.filter(ImageFilter.GaussianBlur(radius=5))
    return createTexture(blurredImage, "blurredImage")


def sharpenImage(imagePath):
    image = loadImage(imagePath)
    sharpenedImage = image.filter(ImageFilter.SHARPEN)
    return createTexture(sharpenedImage, "sharpenedImage")


def findEdges(imagePath):
    image = loadImage(imagePath)
    edgeImage = image.filter(ImageFilter.FIND_EDGES)
    return createTexture(edgeImage, "edgeImage")


def resizeImage(imagePath, newWidth, newHeight):
    image = loadImage(imagePath)
    resizedImage = image.resize((newWidth, newHeight), Image.Resampling.LANCZOS)
    return createTexture(resizedImage, "resizedImage")


def downsizeImage(imagePath, downsizeFactor):
    # Shrink to a fraction of the original, then scale back up with NEAREST
    # so the loss of detail (pixelation) is visible on screen
    image = loadImage(imagePath)
    originalWidth, originalHeight = image.size
    smallWidth = max(1, int(originalWidth * downsizeFactor))
    smallHeight = max(1, int(originalHeight * downsizeFactor))
    smallImage = image.resize((smallWidth, smallHeight), Image.Resampling.LANCZOS)
    downsizedImage = smallImage.resize((originalWidth, originalHeight), Image.Resampling.NEAREST)
    return createTexture(downsizedImage, f"downsizedImage{downsizeFactor}")


def cropImage(imagePath):
    image = loadImage(imagePath)
    croppedImage = image.crop((50, 50, 250, 250))
    return createTexture(croppedImage, "croppedImage")
