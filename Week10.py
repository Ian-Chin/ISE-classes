import math
import random
import arcade

windowWidth = 800
windowHeight = 600
windowTitle = "Visual Effects Example"


def blinkingCircle(posX: float, posY: float, elapsedTime: float, isBlinkingOn: bool, radius: float = 50):
    if isBlinkingOn:
        circleColor = (
            arcade.color.YELLOW_ORANGE
            if int(elapsedTime * 5) % 2 == 0
            else arcade.color.YELLOW
        )
    else:
        circleColor = arcade.color.YELLOW_ROSE

    arcade.draw_circle_filled(posX, posY, radius, circleColor)


def ScreenShake(shakeTime: float, deltaTime: float) -> tuple[float, float, float]:
    if shakeTime > 0:
        shakeTime -= deltaTime
        return random.randint(-10, 10), random.randint(-10, 10), shakeTime
    return 0.0, 0.0, 0.0


def Magnifier(mouseX: float, mouseY: float, offsetX: float, offsetY: float,
              elapsedTime: float, isBlinkingOn: bool, lensRadius: float = 65.0):
    lensX = mouseX + offsetX
    lensY = mouseY + offsetY

    circleX = 400 + offsetX
    circleY = 300 + offsetY

    distanceToCircle = math.hypot(lensX - circleX, lensY - circleY)

    arcade.draw_circle_filled(lensX, lensY, lensRadius, (240, 245, 255, 120))

    if distanceToCircle < (lensRadius + 50):
        blinkingCircle(circleX, circleY, elapsedTime, isBlinkingOn, radius=80)

    arcade.draw_circle_outline(lensX, lensY, lensRadius, arcade.color.LIGHT_BLUE, 4)
    arcade.draw_line(lensX + 45, lensY - 45, lensX + 80, lensY - 80, arcade.color.DARK_BROWN, 10)


def MaskingEffect(mouseX: float, mouseY: float, offsetX: float, offsetY: float,
                  elapsedTime: float, isBlinkingOn: bool, isWaterOn: bool, spotRadius: float = 100.0):
    spotX = mouseX + offsetX
    spotY = mouseY + offsetY

    arcade.draw_rect_filled(arcade.XYWH(windowWidth // 2, windowHeight // 2, windowWidth, windowHeight), arcade.color.BLACK)
    arcade.draw_circle_filled(spotX, spotY, spotRadius, arcade.color.WHITE)

    circleX = 400 + offsetX
    circleY = 300 + offsetY
    if math.hypot(spotX - circleX, spotY - circleY) < (spotRadius + 50):
        blinkingCircle(circleX, circleY, elapsedTime, isBlinkingOn)

    if isWaterOn:
        for i in range(12):
            waveX = 200 + math.sin(elapsedTime * 4 + i * 0.4) * 20 + offsetX
            waveY = 80 + (i * 10) + offsetY
            if math.hypot(spotX - waveX, spotY - waveY) < (spotRadius + 100):
                arcade.draw_rect_filled(
                    arcade.XYWH(waveX, waveY, 200, 6),
                    (0, 120, 255, 180),
                )

    arcade.draw_circle_outline(spotX, spotY, spotRadius, (255, 255, 200, 200), 5)


def setGreenscreen(window: arcade.Window, isActive: bool):
    if isActive:
        window.background_color = (0, 255, 0)
    else:
        window.background_color = arcade.color.WHITE


def waterDistortion(elapsedTime: float, offsetX: float, offsetY: float):
    for i in range(12):
        waveX = 200 + math.sin(elapsedTime * 4 + i * 0.4) * 20 + offsetX
        waveY = 80 + (i * 10) + offsetY
        arcade.draw_rect_filled(
            arcade.XYWH(waveX, waveY, 200, 6),
            (0, 120, 255, 180),
        )


class myWindow(arcade.Window):
    def __init__(self):
        super().__init__(windowWidth, windowHeight, windowTitle)

        self.elapsedTime = 0.0
        self.shakeTime = 0.0
        self.shakeX = 0.0
        self.shakeY = 0.0
        self.mouseX = windowWidth // 2
        self.mouseY = windowHeight // 2

        self.background_color = arcade.color.WHITE

        self.activeEffects = {
            1: False,  # Blinking animation state
            2: False,  # Screen Shake
            3: False,  # Magnifier Lens
            4: False,  # Masking / Spotlight
            5: False,  # Green Screen
            6: False,  # Water Distortion
        }

    def on_update(self, deltaTime: float):
        self.elapsedTime += deltaTime

        if self.activeEffects[2]:
            self.shakeX, self.shakeY, self.shakeTime = ScreenShake(
                self.shakeTime, deltaTime
            )
        else:
            self.shakeX, self.shakeY = 0.0, 0.0

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        self.mouseX = x
        self.mouseY = y

    def on_key_press(self, key, modifiers):
        if key == arcade.key.KEY_1:
            self.activeEffects[1] = not self.activeEffects[1]
        elif key == arcade.key.KEY_2:
            self.activeEffects[2] = not self.activeEffects[2]
        elif key == arcade.key.KEY_3:
            self.activeEffects[3] = not self.activeEffects[3]
        elif key == arcade.key.KEY_4:
            self.activeEffects[4] = not self.activeEffects[4]
        elif key == arcade.key.KEY_5:
            self.activeEffects[5] = not self.activeEffects[5]
            setGreenscreen(self, self.activeEffects[5])
        elif key == arcade.key.KEY_6:
            self.activeEffects[6] = not self.activeEffects[6]
        elif key == arcade.key.SPACE and self.activeEffects[2]:
            self.shakeTime = 0.4

    def on_draw(self):
        self.clear()

        blinkingCircle(
            400 + self.shakeX,
            300 + self.shakeY,
            self.elapsedTime,
            self.activeEffects[1]
        )

        if self.activeEffects[6]:
            waterDistortion(self.elapsedTime, self.shakeX, self.shakeY)

        if self.activeEffects[4]:
            MaskingEffect(self.mouseX, self.mouseY, self.shakeX, self.shakeY,
                          self.elapsedTime, self.activeEffects[1], self.activeEffects[6])

        if self.activeEffects[3]:
            Magnifier(
                self.mouseX,
                self.mouseY,
                self.shakeX,
                self.shakeY,
                self.elapsedTime,
                self.activeEffects[1],
            )

        textColor = arcade.color.BLACK if not self.activeEffects[5] else arcade.color.DARK_GREEN

        arcade.draw_text("PRESS NUMBER KEYS TO TOGGLE EFFECTS:", 20, 560, textColor, 12, bold=True)
        arcade.draw_text(f"[1] Blinking Animation: {'ON' if self.activeEffects[1] else 'OFF'}", 20, 530, textColor, 12)
        arcade.draw_text(f"[2] Screen Shake (SPACE to shake): {'ON' if self.activeEffects[2] else 'OFF'}", 20, 505, textColor, 12)
        arcade.draw_text(f"[3] Magnifier Lens: {'ON' if self.activeEffects[3] else 'OFF'}", 20, 480, textColor, 12)
        arcade.draw_text(f"[4] Spotlight Masking: {'ON' if self.activeEffects[4] else 'OFF'}", 20, 455, textColor, 12)
        arcade.draw_text(f"[5] Green Screen: {'ON' if self.activeEffects[5] else 'OFF'}", 20, 430, textColor, 12)
        arcade.draw_text(f"[6] Water Distortion: {'ON' if self.activeEffects[6] else 'OFF'}", 20, 405, textColor, 12)


if __name__ == "__main__":
    window = myWindow()
    arcade.run()
