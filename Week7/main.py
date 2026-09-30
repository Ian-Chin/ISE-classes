import os
import arcade
import member1
import member2
import member3

screenWidth = 800
screenHeight = 600
screenTitle = "Image Manipulation"

initialScale = 0.5


class myWindowApp(arcade.Window):
    def __init__(self):
        super().__init__(
            screenWidth,
            screenHeight,
            screenTitle
        )
        self.imagePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "turtle.png")
        self.imageTexture = None
        self.imageSprite = None
        self.spriteList = None
        self.scaleFactor = initialScale
        self.rotationAngle = 0
        self.loadOriginalImage()

    def loadOriginalImage(self):
        self.imageTexture = arcade.load_texture(self.imagePath)
        self.imageSprite = arcade.Sprite(
            self.imageTexture,
            scale=self.scaleFactor
        )
        self.imageSprite.scale_x = self.scaleFactor
        self.imageSprite.scale_y = self.scaleFactor
        self.imageSprite.center_x = 500
        self.imageSprite.center_y = 300
        self.spriteList = arcade.SpriteList()
        self.spriteList.append(
            self.imageSprite
        )

    def updateTexture(self, newTexture):
        self.imageTexture = newTexture
        self.imageSprite.texture = newTexture
        self.imageSprite.center_x = 500
        self.imageSprite.center_y = 300
        self.imageSprite.angle = self.rotationAngle

    def on_draw(self):
        self.clear()
        arcade.draw_text(
            "MENU",
            30,
            560,
            arcade.color.WHITE,
            20
        )
        menuItems = [
            "1 - Scale",
            "2 - Rotate",
            "3 - Flip Horizontal",
            "4 - Flip Vertical",
            "5 - Crop",
            "6 - Tint",
            "7 - Grayscale",
            "8 - Gaussian Blur",
            "A - Invert Colours",
            "B - Brightness",
            "C - Contrast",
            "D - Sharpen",
            "E - Find Edges",
            "F - Downsize",
            "G - Sepia",
            "0 - Reset"
        ]
        yPosition = 525
        for menuItem in menuItems:
            arcade.draw_text(
                menuItem,
                30,
                yPosition,
                arcade.color.WHITE,
                16
            )
            yPosition -= 30
        self.spriteList.draw()
        arcade.draw_text(
            f"Scale: {self.scaleFactor:.2f}",
            500,
            100,
            arcade.color.YELLOW,
            18
        )
        arcade.draw_text(
            f"Rotation: {self.rotationAngle} degrees",
            500,
            50,
            arcade.color.YELLOW,
            18
        )

    def on_key_press(self, key, modifiers):
        if key == arcade.key.KEY_1:
            self.scaleFactor = member1.scaleImage(
                self.scaleFactor,
                1.2
            )
            self.imageSprite.scale = self.scaleFactor
        elif key == arcade.key.KEY_2:
            self.rotationAngle = member1.rotateImage(
                self.rotationAngle, 30)
            self.imageSprite.angle = self.rotationAngle
        elif key == arcade.key.KEY_3:
            member1.flipHorizontal(self.imageSprite)
        elif key == arcade.key.KEY_4:
            member1.flipVertical(self.imageSprite)
        elif key == arcade.key.KEY_5:
            newTexture = member2.cropImage(self.imagePath)
            self.updateTexture(newTexture)
        elif key == arcade.key.KEY_6:
            newTexture = member3.tintImage(self.imagePath, (255, 80, 80, 255))
            self.updateTexture(newTexture)
        elif key == arcade.key.KEY_7:
            newTexture = member3.convertToGrayscale(self.imagePath)
            self.updateTexture(newTexture)
        elif key == arcade.key.KEY_8:
            newTexture = member2.applyBlur(self.imagePath)
            self.updateTexture(newTexture)
        elif key == arcade.key.A:
            newTexture = member3.invertImage(self.imagePath)
            self.updateTexture(newTexture)
        elif key == arcade.key.B:
            newTexture = member3.adjustBrightness(self.imagePath, 1.5)
            self.updateTexture(newTexture)
        elif key == arcade.key.C:
            newTexture = member3.adjustContrast(self.imagePath, 1.5)
            self.updateTexture(newTexture)
        elif key == arcade.key.D:
            newTexture = member2.sharpenImage(self.imagePath)
            self.updateTexture(newTexture)
        elif key == arcade.key.E:
            newTexture = member2.findEdges(self.imagePath)
            self.updateTexture(newTexture)
        elif key == arcade.key.F:
            newTexture = member2.downsizeImage(self.imagePath, 0.1)
            self.updateTexture(newTexture)
        elif key == arcade.key.G:
            newTexture = member3.sepiaImage(self.imagePath)
            self.updateTexture(newTexture)
        elif key == arcade.key.KEY_0:
            self.scaleFactor = initialScale
            self.rotationAngle = 0
            self.loadOriginalImage()


if __name__ == "__main__":
    app = myWindowApp()
    arcade.run()
