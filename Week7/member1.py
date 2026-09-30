import arcade


def scaleImage(currentScale, scaleFactor):
    return currentScale * scaleFactor


def rotateImage(currentAngle, rotationAmount):
    newAngle = currentAngle + rotationAmount
    return newAngle % 360


def flipHorizontal(imageSprite):
    imageSprite.scale_x *= -1


def flipVertical(imageSprite):
    imageSprite.scale_y *= -1
