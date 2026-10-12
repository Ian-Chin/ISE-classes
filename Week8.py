
import math
import arcade
from PIL import Image, ImageDraw, ImageEnhance
from arcade.types import Color

def NormalizeColor(color) -> tuple[float, float, float, float]:

    if hasattr(color, "normalized"):
        return color.normalized

    r = color[0] / 255.0
    g = color[1] / 255.0
    b = color[2] / 255.0
    a = (color[3] / 255.0) if len(color) > 3 else 1.0
    return (r, g, b, a)

def generateTexturedBlock(size: int = 128, contrast: float = 1.0) -> arcade.Texture:
    img = Image.new("RGBA", (size, size), (140, 100, 60, 255))
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, size - 1, size - 1], outline=(70, 45, 20, 255), width=8)
 
    draw.line([0, 0, size - 1, size - 1], fill=(95, 60, 30, 255), width=6)
    draw.line([0, size - 1, size - 1, 0], fill=(95, 60, 30, 255), width=6)

    draw.rectangle([size * 0.35, size * 0.35, size * 0.65, size * 0.65], outline=(180, 130, 80, 255), width=3)

    if contrast != 1.0:
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(contrast)

    return arcade.Texture(image=img, name=f"2d_block_texture_{contrast:.1f}_{size}")

class Cube(arcade.View):
    def __init__(self):
        super().__init__()

        self.cubeX = self.window.width / 2 - 140
        self.cubeY = self.window.height / 2 - 20
        self.cubeSize = 110

        self.pyramidX = self.window.width / 2 + 170
        self.pyramidY = self.window.height / 2 - 60
        self.pyramidSize = 90
        self.pyramidTone = (0.45, 0.95, 0.8)
        self.pyramidSpeed = 250.0
        self.keysHeld = set()

        self.contrast = 1.0
        self.baseTone = (1.0, 0.9, 0.75)
        self.lightAngle = 0.0
        self.lightDistance = 240.0

        self.texture = generateTexturedBlock(128, self.contrast)

    def on_show_view(self):
        self.window.background_color = (20, 24, 36)

    def on_update(self, deltaTime: float):
        self.lightAngle += deltaTime * 1.2

        dx = (arcade.key.D in self.keysHeld) - (arcade.key.A in self.keysHeld)
        dy = (arcade.key.W in self.keysHeld) - (arcade.key.S in self.keysHeld)
        self.pyramidX += dx * self.pyramidSpeed * deltaTime
        self.pyramidY += dy * self.pyramidSpeed * deltaTime

        s = self.pyramidSize
        self.pyramidX = max(s, min(self.window.width - s, self.pyramidX))
        self.pyramidY = max(s * 0.5 + 50, min(self.window.height - s * 1.6 - 60, self.pyramidY))

    def getLightPosition(self):
        lx = self.cubeX + math.cos(self.lightAngle) * self.lightDistance
        ly = self.cubeY + math.sin(self.lightAngle) * (self.lightDistance * 0.5) + 120
        return lx, ly

    def on_key_press(self, key: int, modifiers: int):
        if key in (arcade.key.W, arcade.key.A, arcade.key.S, arcade.key.D):
            self.keysHeld.add(key)
        elif key == arcade.key.UP:
            self.contrast = min(3.0, self.contrast + 0.25)
            self.texture = generateTexturedBlock(128, self.contrast)
        elif key == arcade.key.DOWN:
            self.contrast = max(0.5, self.contrast - 0.25)
            self.texture = generateTexturedBlock(128, self.contrast)
        elif key == arcade.key.SPACE:
            if self.baseTone == (1.0, 0.9, 0.75):
                self.baseTone = (0.7, 0.9, 1.0)
            elif self.baseTone == (0.7, 0.9, 1.0):
                self.baseTone = (0.9, 0.6, 1.0)
            else:
                self.baseTone = (1.0, 0.9, 0.75)

    def on_key_release(self, key: int, modifiers: int):
        self.keysHeld.discard(key)
    
    
    def drawShadow(self, lx: float, ly: float):
        dx = self.cubeX - lx
        dy = (self.cubeY - 40) - ly

        shadowDx = dx * 0.35
        shadowDy = dy * 0.12

        s = self.cubeSize
        shadowPoints = [
            (self.cubeX - s + shadowDx, self.cubeY - s * 0.5 + shadowDy),
            (self.cubeX + shadowDx, self.cubeY - s * 0.9 + shadowDy),
            (self.cubeX + s + shadowDx, self.cubeY - s * 0.5 + shadowDy),
            (self.cubeX + shadowDx, self.cubeY - s * 0.1 + shadowDy),
        ]
        arcade.draw_polygon_filled(shadowPoints, color=(8, 10, 18, 170))

    def drawCube(self, lx: float, ly: float):
        s = self.cubeSize
        h = s * 0.85

        topCenter = (self.cubeX, self.cubeY + h)
        topRight = (self.cubeX + s, self.cubeY + h * 0.5)
        topBottom = (self.cubeX, self.cubeY)
        topLeft = (self.cubeX - s, self.cubeY + h * 0.5)

        botLeft = (self.cubeX - s, self.cubeY + h * 0.5 - h)
        botCenter = (self.cubeX, self.cubeY - h)
        botRight = (self.cubeX + s, self.cubeY + h * 0.5 - h)

        topLight = max(0.35, min(1.0, (ly - self.cubeY) / 160.0))
        leftLight = max(0.25, min(0.85, (self.cubeX - lx) / 220.0 + 0.5))
        rightLight = max(0.25, min(0.85, (lx - self.cubeX) / 220.0 + 0.5))

        def getFaceColor(baseIntensity: int, lightMult: float) -> tuple[int, int, int]:
            r = int(baseIntensity * self.baseTone[0] * lightMult)
            g = int(baseIntensity * self.baseTone[1] * lightMult)
            b = int(baseIntensity * self.baseTone[2] * lightMult)
            return (min(255, max(0, r)), min(255, max(0, g)), min(255, max(0, b)))

        colorTop = getFaceColor(255, topLight)
        colorLeft = getFaceColor(200, leftLight)
        colorRight = getFaceColor(230, rightLight)

        arcade.draw_polygon_filled([topLeft, topBottom, botCenter, botLeft], color=colorLeft)
        arcade.draw_polygon_filled([topBottom, topRight, botRight, botCenter], color=colorRight)

        arcade.draw_polygon_filled([topCenter, topRight, topBottom, topLeft], color=colorTop)

        arcade.draw_texture_rect(
            texture=self.texture,
            rect=arcade.XYWH(self.cubeX, self.cubeY - h * 0.38, s * 0.9, h * 0.72),
            color=Color(colorRight[0], colorRight[1], colorRight[2], 200),
        )

        edges = [
            (topCenter, topRight), (topRight, topBottom), (topBottom, topLeft), (topLeft, topCenter),
            (topBottom, botCenter), (topLeft, botLeft), (topRight, botRight),
            (botLeft, botCenter), (botCenter, botRight)
        ]
        for p1, p2 in edges:
            arcade.draw_line(p1[0], p1[1], p2[0], p2[1], color=(35, 40, 55), line_width=2)

    def drawPyramidShadow(self, lx: float, ly: float):
        dx = self.pyramidX - lx
        dy = (self.pyramidY - 30) - ly

        shadowDx = dx * 0.35
        shadowDy = dy * 0.12

        s = self.pyramidSize
        shadowPoints = [
            (self.pyramidX - s + shadowDx, self.pyramidY + shadowDy),
            (self.pyramidX + shadowDx, self.pyramidY - s * 0.5 + shadowDy),
            (self.pyramidX + s + shadowDx, self.pyramidY + shadowDy),
            (self.pyramidX + shadowDx, self.pyramidY + s * 0.5 + shadowDy),
        ]
        arcade.draw_polygon_filled(shadowPoints, color=(8, 10, 18, 170))

    def drawPyramid(self, lx: float, ly: float):
        s = self.pyramidSize
        h = s * 1.6

        apex = (self.pyramidX, self.pyramidY + h)
        baseLeft = (self.pyramidX - s, self.pyramidY)
        baseFront = (self.pyramidX, self.pyramidY - s * 0.5)
        baseRight = (self.pyramidX + s, self.pyramidY)

        leftLight = max(0.25, min(0.95, (self.pyramidX - lx) / 220.0 + 0.55))
        rightLight = max(0.25, min(0.95, (lx - self.pyramidX) / 220.0 + 0.55))

        def getFaceColor(baseIntensity: int, lightMult: float) -> tuple[int, int, int]:
            r = int(baseIntensity * self.pyramidTone[0] * lightMult)
            g = int(baseIntensity * self.pyramidTone[1] * lightMult)
            b = int(baseIntensity * self.pyramidTone[2] * lightMult)
            return (min(255, max(0, r)), min(255, max(0, g)), min(255, max(0, b)))

        colorLeft = getFaceColor(220, leftLight)
        colorRight = getFaceColor(240, rightLight)

        arcade.draw_polygon_filled([apex, baseLeft, baseFront], color=colorLeft)
        arcade.draw_polygon_filled([apex, baseFront, baseRight], color=colorRight)

        edges = [
            (apex, baseLeft), (apex, baseFront), (apex, baseRight),
            (baseLeft, baseFront), (baseFront, baseRight)
        ]
        for p1, p2 in edges:
            arcade.draw_line(p1[0], p1[1], p2[0], p2[1], color=(35, 40, 55), line_width=2)

    def on_draw(self):
        self.clear()

        lx, ly = self.getLightPosition()

        self.drawShadow(lx, ly)

        self.drawPyramidShadow(lx, ly)

        if self.pyramidY > self.cubeY:
            self.drawPyramid(lx, ly)
            self.drawCube(lx, ly)
        else:
            self.drawCube(lx, ly)
            self.drawPyramid(lx, ly)

        arcade.draw_circle_filled(lx, ly, radius=10, color=arcade.color.WHITE)
        arcade.draw_circle_filled(lx, ly, radius=18, color=(255, 240, 180, 70))

        arcade.draw_text(
            text=f"Cube & Pyramid ->  Contrast: {self.contrast:.2f}x",
            x=self.window.width / 2,
            y=self.window.height - 40,
            color=arcade.color.WHITE,
            font_size=16,
            anchor_x="center",
        )

        arcade.draw_text(
            text="[WASD] Move Pyramid  |  [UP/DOWN] Contrast Shift  |  [SPACE] Change Color Tone",
            x=self.window.width / 2,
            y=30,
            color=arcade.color.LIGHT_GRAY,
            font_size=13,
            anchor_x="center",
        )

window = arcade.Window(800, 600, "Cube & Pyramid Lighting")
view = Cube()
window.show_view(view)
arcade.run()
