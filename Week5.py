import arcade
import random
from pathlib import Path

screenWidth = 800
screenHeight = 600
screenTitle = "Capture Game"

# Week 4 mascot: the turtle sprite sheet (2 rows x 4 columns = 8 frames)
assetDir = Path(__file__).parent / "lab" / "asset"
playerSheetPath = assetDir / "turtle.png"

sheetRowCount = 2
sheetColumnCount = 4
frameCount = sheetRowCount * sheetColumnCount

# How long one animation frame stays on screen
frameDuration = 0.12

targetCount = 15
playerSpeed = 5

# Collect every treasure before this many seconds to win
timeLimit = 10.0

praiseWords = [
    "OUHHHHHH!",
    "OHHHHHHH!",
    "OHHHHHHHHHH!",
    "AMAZING!",
    "WELL DONE!",
]

class CaptureGame(arcade.Window):

    def __init__(self):
        super().__init__(
            screenWidth,
            screenHeight,
            screenTitle
        )

        self.playerSprite = None
        self.targetList = arcade.SpriteList()

        self.score = 0

        self.moveUp = False
        self.moveDown = False
        self.moveLeft = False
        self.moveRight = False

        # Instruction
        self.showInstruction = True

        # Praise message
        self.praiseMessage = ""

        # Praise message timer
        self.praiseTimer = 0

        # Animation frames, one set facing right and one facing left
        self.rightFrames = []
        self.leftFrames = []

        # Animation state
        self.currentFrame = 0
        self.animationTime = 0
        self.facingRight = True

        # Game timer (counts up in seconds)
        self.gameTime = 0

        # "playing", "win" or "lose"
        self.gameState = "playing"

    def setup(self):
        # Cut the sprite sheet into a grid of textures, one per frame
        spriteSheet = arcade.load_spritesheet(playerSheetPath)

        frameWidth = spriteSheet.image.width // sheetColumnCount
        frameHeight = spriteSheet.image.height // sheetRowCount

        self.rightFrames = spriteSheet.get_texture_grid(
            (frameWidth, frameHeight),
            sheetColumnCount,
            frameCount
        )

        # Mirrored copies so the turtle faces the way it walks
        self.leftFrames = [
            texture.flip_left_right()
            for texture in self.rightFrames
        ]

        self.currentFrame = 0
        self.animationTime = 0
        self.facingRight = True

        self.playerSprite = arcade.Sprite(
            self.rightFrames[0],
            scale=0.4
        )

        self.playerSprite.center_x = screenWidth // 2
        self.playerSprite.center_y = screenHeight // 2

        self.targetList = arcade.SpriteList()

        for i in range(targetCount):

            targetSprite = arcade.Sprite(
                r"C:\Users\ianga\Downloads\ISE\Python Code\pngtree-apple-pixel-art-png-image_10214986.png",
                scale=0.1
            )

            targetSprite.center_x = random.randint(
                50,
                screenWidth - 50
            )

            targetSprite.center_y = random.randint(
                100,
                screenHeight - 50
            )

            self.targetList.append(targetSprite)

        #reset
        self.score = 0
        self.showInstruction = True
        self.praiseMessage = ""
        self.praiseTimer = 0
        self.gameTime = 0
        self.gameState = "playing"

    def on_draw(self):
        self.clear(arcade.color.DARK_BLUE)

        arcade.draw_text(
            f"Score: {self.score} / {targetCount}",
            20,
            screenHeight - 40,
            arcade.color.YELLOW,
            20
        )

        # Timer on the top right of the screen, counting down to the limit
        timeLeft = max(0, timeLimit - self.gameTime)

        # Turn the clock red in the last 3 seconds
        if timeLeft <= 3:
            timeColor = arcade.color.RED
        else:
            timeColor = arcade.color.YELLOW

        arcade.draw_text(
            f"Time: {timeLeft:.1f}s",
            screenWidth - 20,
            screenHeight - 40,
            timeColor,
            20,
            anchor_x="right"
        )

        if self.showInstruction:

            instructionX = (
                self.playerSprite.center_x
                + self.playerSprite.width / 2
                + 10
            )

            instructionY = self.playerSprite.center_y

            arcade.draw_text(
                "Touch the treasure!",
                instructionX,
                instructionY,
                arcade.color.WHITE,
                18,
                anchor_y="center"
            )

        self.targetList.draw()

        arcade.draw_sprite(self.playerSprite)

        if self.praiseTimer > 0:

            arcade.draw_text(
                self.praiseMessage,
                screenWidth / 2,
                screenHeight - 120,
                arcade.color.RED,
                32,
                anchor_x="center"
            )

        # Win or lose message once the game is over
        if self.gameState != "playing":

            if self.gameState == "win":
                message = "YOU WIN!"
                detail = f"All {targetCount} treasures in {self.gameTime:.1f}s"
                messageColor = arcade.color.GREEN
            else:
                message = "YOU LOSE!"
                detail = f"Time is up - only {self.score} of {targetCount}"
                messageColor = arcade.color.RED

            arcade.draw_text(
                message,
                screenWidth / 2,
                screenHeight / 2 + 30,
                messageColor,
                60,
                anchor_x="center",
                bold=True
            )

            arcade.draw_text(
                detail,
                screenWidth / 2,
                screenHeight / 2 - 20,
                arcade.color.WHITE,
                22,
                anchor_x="center"
            )

            arcade.draw_text(
                "Press R to play again",
                screenWidth / 2,
                screenHeight / 2 - 60,
                arcade.color.WHITE,
                18,
                anchor_x="center"
            )

    def animatePlayer(self, deltaTime, isMoving):
        # Standing still: hold the first frame
        if not isMoving:
            self.currentFrame = 0
            self.animationTime = 0

        else:
            self.animationTime += deltaTime

            if self.animationTime >= frameDuration:
                self.animationTime = 0
                self.currentFrame += 1

                # Wrap back to the first frame after the last one
                if self.currentFrame >= frameCount:
                    self.currentFrame = 0

        if self.facingRight:
            self.playerSprite.texture = self.rightFrames[self.currentFrame]
        else:
            self.playerSprite.texture = self.leftFrames[self.currentFrame]

    def on_update(self, deltaTime):
        # The game is over, so nothing moves and the clock stops
        if self.gameState != "playing":
            return

        # Timer keeps counting while the game is running
        self.gameTime += deltaTime

        isMoving = (
            self.moveUp
            or self.moveDown
            or self.moveLeft
            or self.moveRight
        )


        if isMoving:
            self.showInstruction = False

        if self.moveUp:
            self.playerSprite.center_y += playerSpeed

        if self.moveDown:
            self.playerSprite.center_y -= playerSpeed

        if self.moveLeft:
            self.playerSprite.center_x -= playerSpeed
            self.facingRight = False

        if self.moveRight:
            self.playerSprite.center_x += playerSpeed
            self.facingRight = True

        # Walk cycle, so the movement of the character can be seen
        self.animatePlayer(deltaTime, isMoving)

        self.playerSprite.center_x = max(
            self.playerSprite.width / 2,
            min(
                screenWidth - self.playerSprite.width / 2,
                self.playerSprite.center_x
            )
        )

        self.playerSprite.center_y = max(
            self.playerSprite.height / 2,
            min(
                screenHeight - self.playerSprite.height / 2,
                self.playerSprite.center_y
            )
        )

        if self.praiseTimer > 0:

            self.praiseTimer -= deltaTime

            if self.praiseTimer <= 0:

                self.praiseTimer = 0
                self.praiseMessage = ""

        hitList = arcade.check_for_collision_with_list(
            self.playerSprite,
            self.targetList
        )

        for targetSprite in hitList:

            targetSprite.remove_from_sprite_lists()

            # Increase score
            self.score += 1

            # Choose random praise word
            self.praiseMessage = random.choice(praiseWords)

            # Display for 2 seconds
            self.praiseTimer = 2.0

        # Every treasure taken before the limit is a win
        if self.score >= targetCount:
            self.gameState = "win"

        # Still treasures left when the time runs out is a loss
        elif self.gameTime >= timeLimit:
            self.gameState = "lose"
            self.praiseMessage = ""
            self.praiseTimer = 0

    def on_key_press(self, key, modifiers):
        # R starts a new game once this one is over
        if key == arcade.key.R and self.gameState != "playing":
            self.setup()
            return

        if key == arcade.key.UP or key == arcade.key.W:
            self.moveUp = True

        if key == arcade.key.DOWN or key == arcade.key.S:
            self.moveDown = True

        if key == arcade.key.LEFT or key == arcade.key.A:
            self.moveLeft = True

        if key == arcade.key.RIGHT or key == arcade.key.D:
            self.moveRight = True

    def on_key_release(self, key, modifiers):
        if key == arcade.key.UP or key == arcade.key.W:
            self.moveUp = False

        if key == arcade.key.DOWN or key == arcade.key.S:
            self.moveDown = False

        if key == arcade.key.LEFT or key == arcade.key.A:
            self.moveLeft = False

        if key == arcade.key.RIGHT or key == arcade.key.D:
            self.moveRight = False

game = CaptureGame()
game.setup()
arcade.run()
