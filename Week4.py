"""
Week 4: Imaging and Special Effects - Working with Animation
"""

import math
import random
import sys
from pathlib import Path

import arcade
from PIL import Image

ASSET_DIR = Path(__file__).parent / "lab" / "asset"
IMAGE_PATH = ASSET_DIR / "turtle.png"

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

ROW_COUNT = 2
COLUMN_COUNT = 4
FRAME_COUNT = ROW_COUNT * COLUMN_COUNT

colorModes = {
    "1": "Black and White (1-bit)",
    "L": "Grayscale (8-bit)",
    "P": "Palette-based",
    "RGB": "RGB Color",
    "RGBA": "RGB Color + Alpha",
    "CMYK": "CMYK Color",
    "YCbCr": "YCbCr Color",
    "I": "32-bit Integer",
    "F": "32-bit Floating Point",
}

def printImageInfo(img):
    """
    Print the resolution, colour mode, channel count and format of a Pillow image,
    then dump a 3x3 block of pixel values taken from the middle of the image.
    Shared by Task 1, Task 2 and the exercise so the code is written only once.
    """
    width = img.width
    height = img.height

    print(f"Resolution: {width} X {height} pixels")
    print(f"Total number of pixel: {width * height} pixels")
    print(f"Color mode: {img.mode} ->({colorModes.get(img.mode, 'Unknown')})")
    print(f"Color channels: {len(img.getbands())}")
    print(f"Format: {img.format}")

    # Sample a small 3x3 patch from the centre of the image
    startRow = int(height / 2)
    startCol = int(width / 2)

    for y in range(min(startRow, height), startRow + 3):
        for x in range(min(startCol, width), startCol + 3):
            pixel = img.getpixel((x, y))
            print(f"{pixel} ", end="")
        print()


# --------------------------------------------------------------------------------------
# Task 1: Understand the image
# --------------------------------------------------------------------------------------
def task1():
    """Open the turtle sheet with Pillow, report its properties and preview it."""
    img = Image.open(IMAGE_PATH)
    printImageInfo(img)
    img.show()


# --------------------------------------------------------------------------------------
# Task 2: Do the same thing with Arcade, and draw the image as a sprite
# --------------------------------------------------------------------------------------
class Task2Window(arcade.Window):
    """Arcade window that reports the image details and shows the whole sheet centred."""

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Working with Pillow")

        # Inspect the file with Pillow before handing it to Arcade
        img = Image.open(IMAGE_PATH)
        printImageInfo(img)
        img.close()

        # Load the same file as a sprite and park it in the middle of the screen
        self.sprite = arcade.Sprite(IMAGE_PATH)
        self.sprite.center_x = SCREEN_WIDTH // 2
        self.sprite.center_y = SCREEN_HEIGHT // 2

        self.spriteList = arcade.SpriteList()
        self.spriteList.append(self.sprite)

    def on_draw(self):
        self.clear()
        self.spriteList.draw()


# --------------------------------------------------------------------------------------
# Task 3: Create a sprite animation from the sheet
# --------------------------------------------------------------------------------------
class Task3Window(arcade.Window):
    """Slice the sheet with arcade.load_spritesheet and loop through the frames."""

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Sprite Animation")

        # Work out the size of one character from the size of the whole sheet
        spriteSheet = arcade.load_spritesheet(IMAGE_PATH)
        sheetWidth = spriteSheet.image.width
        sheetHeight = spriteSheet.image.height

        frameWidth = sheetWidth // COLUMN_COUNT
        frameHeight = sheetHeight // ROW_COUNT

        print(f"Sprite sheet: {sheetWidth} x {sheetHeight}")
        print(f"Frame size: {frameWidth} x {frameHeight}")

        # Cut the sheet into a grid of textures, one per character
        self.animationFrames = spriteSheet.get_texture_grid(
            (frameWidth, frameHeight),
            COLUMN_COUNT,
            FRAME_COUNT,
        )

        # Start on the first frame, centred on screen
        self.sprite = arcade.Sprite(self.animationFrames[0])
        self.sprite.center_x = SCREEN_WIDTH // 2
        self.sprite.center_y = SCREEN_HEIGHT // 2

        self.spriteList = arcade.SpriteList()
        self.spriteList.append(self.sprite)

        # Animation state: current frame, elapsed time, and how long a frame is held
        self.currentFrame = 0
        self.animationTime = 0
        self.frameDuration = 0.15

    def on_draw(self):
        self.clear()
        self.spriteList.draw()

    def on_update(self, deltaTime):
        self.animationTime += deltaTime

        if self.animationTime >= self.frameDuration:
            self.animationTime = 0
            self.currentFrame += 1

            # Wrap back to the first frame once the last one has been shown
            if self.currentFrame >= len(self.animationFrames):
                self.currentFrame = 0

            self.sprite.texture = self.animationFrames[self.currentFrame]


# --------------------------------------------------------------------------------------
# Exercise 1: Slice the sheet with Pillow instead of arcade.load_spritesheet (cropping)
# --------------------------------------------------------------------------------------
def cropFramesWithPillow(imagePath, rowCount, columnCount):

    sheet = Image.open(imagePath).convert("RGBA")

    frameWidth = sheet.width // columnCount
    frameHeight = sheet.height // rowCount

    print(f"Sprite sheet: {sheet.width} x {sheet.height}")
    print(f"Frame size: {frameWidth} x {frameHeight}")

    frames = []

    for row in range(rowCount):
        for column in range(columnCount):
            left = column * frameWidth
            upper = row * frameHeight
            box = (left, upper, left + frameWidth, upper + frameHeight)

            frames.append(sheet.crop(box))

    sheet.close()
    return frames


def shiftHue(image, degrees):
    """
    Recolour one frame by rotating its hue, so the same crops can dress four
    different runners. The alpha mask is put back afterwards, otherwise the
    HSV round trip would fill the transparent background.
    """
    if degrees == 0:
        return image

    alpha = image.getchannel("A")
    hue, saturation, value = image.convert("RGB").convert("HSV").split()

    offset = int(degrees / 360 * 255) % 256
    hue = hue.point(lambda level: (level + offset) % 256)

    recoloured = Image.merge("HSV", (hue, saturation, value)).convert("RGBA")
    recoloured.putalpha(alpha)
    return recoloured


def hueShiftedColor(rgb, degrees):
    """Push a single colour through the same rotation used on the sprite frames."""
    swatch = Image.new("RGBA", (1, 1), rgb + (255,))
    return shiftHue(swatch, degrees).convert("RGB").getpixel((0, 0))


def makeTextures(frames, tag, hueShift=0, mirrored=False):
    """Turn the cropped Pillow frames into arcade textures, optionally recoloured/flipped."""
    textures = []

    for index, frame in enumerate(frames):
        image = shiftHue(frame, hueShift)
        if mirrored:
            image = image.transpose(Image.FLIP_LEFT_RIGHT)

        # Arcade caches textures by hash, so every variant needs its own name
        textures.append(arcade.Texture(image, hash=f"{tag}-{index}-{int(mirrored)}"))

    return textures


# --------------------------------------------------------------------------------------
# Exercise 2 + 3: Key-driven animation wrapped in a short sport-event narrative
# --------------------------------------------------------------------------------------

ANIMATIONS = {
    "idle": [0],
    "walk": [0, 1, 2, 3, 4, 5, 7],
    "jump": [6],
    "stumble": [4, 5],
}

# Exercise 3: the pre-race commentary. The rest of the story is generated live
# by the race itself (see Race.say), so no two races are narrated the same way.
NARRATIVE = [
    "SHELLBOURNE STADIUM - Final of the 100 m Turtle Hurdles.",
    "Toby 'Tailwind' Turtle is in lane 1, three rivals alongside him.",
    "The stadium falls silent. The starter raises the gun...",
]

# Track layout
START_X = 90
FINISH_X = SCREEN_WIDTH - 70
RACE_DISTANCE = 100  # metres, for the on-screen readout
LANE_COUNT = 4
LANE_BOTTOM = 150  # y of the lowest runner's centre
LANE_SPACING = 88
RUNNER_SCALE = 0.42
SHADOW_DROP = 204 * RUNNER_SCALE / 2  # frame bottom, where the runner's shadow sits

# Running
BASE_SPEED = 190  # pixels per second
SPRINT_MULTIPLIER = 1.65
MAX_STAMINA = 2.5  # seconds of sprint in the tank
STAMINA_REGEN = 0.6  # refilled per second while jogging
STUMBLE_PENALTY = 0.45  # speed multiplier while tripping
STUMBLE_TIME = 0.7

# Jumping and hurdles
JUMP_SPEED = 430
GRAVITY = -1250
HURDLE_METRES = [22, 44, 66, 88]
HURDLE_HEIGHT = 34
HURDLE_HALF_WIDTH = 23  # how close counts as a clip

BEST_TIME_FILE = Path(__file__).parent / "lab" / "best_time.txt"

SPRINT_KEYS = frozenset({arcade.key.LSHIFT, arcade.key.RSHIFT})

# Runner name and the hue rotation applied to its copy of the sprite sheet.
# The scoreboard colour is derived from the same rotation, so the name on the
# result panel always matches the turtle on the track.
RUNNERS = [
    ("Toby", 0),  # green, the player
    ("Shellina", 90),  # blue
    ("Bruno", 190),  # magenta
    ("Zippy", 268),  # yellow
]

# The green of the turtle's skin, taken from the sprite sheet itself
TURTLE_GREEN = (70, 205, 100)

# Palette
SKY = (120, 195, 235)
TRACK_LIGHT = (206, 124, 88)
TRACK_DARK = (188, 108, 74)
CROWD_BOTTOM = 470
CROWD_TOP = 536
CROWD_COLORS = [
    (232, 196, 160),
    (196, 148, 112),
    (240, 240, 240),
    (226, 96, 88),
    (92, 148, 216),
    (244, 208, 96),
]
CONFETTI_COLORS = [
    (235, 200, 60),
    (226, 96, 88),
    (92, 200, 140),
    (120, 160, 240),
    (245, 245, 245),
]


def metresToX(metres):
    return START_X + (metres / RACE_DISTANCE) * (FINISH_X - START_X)


def ordinal(number):
    return {1: "1st", 2: "2nd", 3: "3rd"}.get(number, f"{number}th")


def loadBestTime():
    """Read the personal best from disk, ignoring a missing or corrupt file."""
    try:
        return float(BEST_TIME_FILE.read_text().strip())
    except (OSError, ValueError):
        return None


def saveBestTime(seconds):
    try:
        BEST_TIME_FILE.write_text(f"{seconds:.2f}")
    except OSError:
        pass  # A read-only folder should not crash the race


class Runner:
    """One turtle in the race: its textures, its lane, and its animation state."""

    def __init__(self, name, lane, color, textures, mirroredTextures, isPlayer):
        self.name = name
        self.lane = lane
        self.color = color
        self.textures = textures
        self.mirroredTextures = mirroredTextures
        self.isPlayer = isPlayer

        self.baseY = LANE_BOTTOM + lane * LANE_SPACING
        self.sprite = arcade.Sprite(textures[0], scale=RUNNER_SCALE)
        self.reset()

    # ----- state -------------------------------------------------------------------
    def reset(self):
        self.x = START_X
        self.jumpOffset = 0
        self.verticalSpeed = 0
        self.onGround = True
        self.facingRight = True

        self.state = "idle"
        self.currentFrame = 0
        self.animationTime = 0
        self.frameDuration = 0.14

        self.stumbleTime = 0
        self.finishTime = None
        self.place = None

        # Each rival gets its own pace and its own surge rhythm, so the race
        # plays out differently every time
        self.aiSpeed = BASE_SPEED * random.uniform(0.92, 1.12)
        self.surgeRate = random.uniform(0.6, 1.4)
        self.surgePhase = random.uniform(0, 6.28)
        self.clumsiness = random.uniform(0.05, 0.4)

        self.applyPosition()

    def applyPosition(self):
        self.sprite.center_x = self.x
        self.sprite.center_y = self.baseY + self.jumpOffset

    @property
    def metres(self):
        return (self.x - START_X) / (FINISH_X - START_X) * RACE_DISTANCE

    def setState(self, state):
        if self.state != state:
            self.state = state
            self.currentFrame = 0
            self.animationTime = 0

    # ----- actions -----------------------------------------------------------------
    def startJump(self):
        if self.onGround and self.stumbleTime <= 0:
            self.verticalSpeed = JUMP_SPEED
            self.onGround = False
            self.setState("jump")
            return True
        return False

    def stumble(self):
        self.stumbleTime = STUMBLE_TIME
        self.setState("stumble")

    def move(self, distance):
        self.x = max(START_X, min(FINISH_X, self.x + distance))

    # ----- per-frame update ---------------------------------------------------------
    def updatePhysics(self, deltaTime):
        if self.stumbleTime > 0:
            self.stumbleTime -= deltaTime
            # Wobble the sprite while tripping, then straighten it up again
            self.sprite.angle = math.sin(self.stumbleTime * 40) * 18
            if self.stumbleTime <= 0:
                self.sprite.angle = 0
        else:
            self.sprite.angle = 0

        if not self.onGround:
            self.verticalSpeed += GRAVITY * deltaTime
            self.jumpOffset += self.verticalSpeed * deltaTime

            if self.jumpOffset <= 0:
                self.jumpOffset = 0
                self.verticalSpeed = 0
                self.onGround = True
                self.setState("idle")

        self.applyPosition()

    def animate(self, deltaTime, speedRatio=1.0):
        # Legs turn over faster the faster the turtle is actually moving
        if self.state == "walk":
            self.frameDuration = max(0.05, 0.16 - 0.07 * speedRatio)
        else:
            self.frameDuration = 0.14

        self.animationTime += deltaTime
        if self.animationTime < self.frameDuration:
            return

        self.animationTime = 0
        sequence = ANIMATIONS[self.state]

        self.currentFrame += 1
        if self.currentFrame >= len(sequence):
            self.currentFrame = 0

        source = self.textures if self.facingRight else self.mirroredTextures
        self.sprite.texture = source[sequence[self.currentFrame]]

    def updateAi(self, deltaTime, elapsed, hurdleXs):
        """Rival logic: hold a pace, surge now and then, and jump the hurdles."""
        if self.finishTime is not None:
            return

        speed = self.aiSpeed + math.sin(elapsed * self.surgeRate + self.surgePhase) * 26
        if self.stumbleTime > 0:
            speed *= STUMBLE_PENALTY

        self.move(speed * deltaTime)

        if self.stumbleTime <= 0 and self.state != "jump":
            self.setState("walk")

        # Look ahead for the next hurdle and take off in time - unless this one
        # is having a clumsy day
        for hurdleX in hurdleXs:
            gap = hurdleX - self.x
            if 45 <= gap <= 80 and self.onGround:
                if random.random() > self.clumsiness:
                    self.startJump()
                break

        self.animate(deltaTime, speedRatio=min(1.0, speed / BASE_SPEED))


class TurtleSprintGame(arcade.Window):
    """
    Exercise 1 + 2 + 3: a four-turtle hurdles race.

    All four runners are drawn from the same sprite sheet - the rivals are the
    player's frames put through a hue rotation in Pillow.

    Controls:
        RIGHT / LEFT : run
        SPACE or UP  : jump the hurdle
        SHIFT (hold) : sprint, while the stamina bar lasts
        R            : race again
        ESC          : quit
    """


    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Turtle 100 m Hurdles")
        self.background_color = SKY

        # Exercise 1: crop the sheet once with Pillow, then dress every runner
        # from those same frames
        pilFrames = cropFramesWithPillow(IMAGE_PATH, ROW_COUNT, COLUMN_COUNT)

        self.runners = []
        self.spriteList = arcade.SpriteList()

        for lane, (name, hue) in enumerate(RUNNERS):
            runner = Runner(
                name,
                lane,
                hueShiftedColor(TURTLE_GREEN, hue),
                makeTextures(pilFrames, name, hue),
                makeTextures(pilFrames, name, hue, mirrored=True),
                isPlayer=(lane == 0),
            )
            self.runners.append(runner)
            self.spriteList.append(runner.sprite)

        self.player = self.runners[0]
        self.hurdleXs = [metresToX(metres) for metres in HURDLE_METRES]

        # A cheap crowd: coloured dots picked once and redrawn every frame
        self.crowd = [
            (
                random.uniform(0, SCREEN_WIDTH),
                random.uniform(CROWD_BOTTOM, CROWD_TOP),
                random.choice(CROWD_COLORS),
            )
            for _ in range(220)
        ]

        # Text objects are created once and only their .text is updated
        self.timeText = arcade.Text("", 16, 566, arcade.color.WHITE, 17, bold=True)
        self.distanceText = arcade.Text("", 200, 566, arcade.color.WHITE, 17)
        self.placeText = arcade.Text("", 370, 566, arcade.color.WHITE, 17, bold=True)
        self.bestText = arcade.Text("", 16, 546, (200, 220, 235), 11)
        self.staminaText = arcade.Text("SPRINT", 560, 568, arcade.color.WHITE, 11)
        self.narrativeText = arcade.Text("", 16, 32, arcade.color.WHITE, 15)
        self.helpText = arcade.Text(
            "RIGHT run    SPACE jump    SHIFT sprint    R race again    ESC quit",
            16,
            11,
            (170, 190, 205),
            11,
        )
        self.countdownText = arcade.Text(
            "", SCREEN_WIDTH // 2, 330, arcade.color.WHITE, 78, bold=True,
            anchor_x="center",
        )
        self.laneTexts = [
            arcade.Text(
                str(lane + 1),
                18,
                runner.baseY - SHADOW_DROP + 4,
                (255, 255, 255, 150),
                13,
                bold=True,
            )
            for lane, runner in enumerate(self.runners)
        ]

        # Result panel: four rows of three columns, filled in when the race ends
        self.resultTitle = arcade.Text(
            "RESULT", 400, 383, (235, 200, 60), 22, bold=True, anchor_x="center"
        )
        self.resultRows = []
        for row in range(LANE_COUNT):
            y = 340 - row * 30
            self.resultRows.append(
                (
                    arcade.Text("", 254, y, arcade.color.WHITE, 16, bold=True),
                    arcade.Text("", 300, y, arcade.color.WHITE, 16),
                    arcade.Text("", 470, y, arcade.color.WHITE, 16),
                )
            )
        self.resultFooter = arcade.Text(
            "", 400, 197, arcade.color.WHITE, 14, bold=True, anchor_x="center"
        )

        # Keys are polled rather than edge-triggered, so a key that is already
        # held down when the gun goes still counts
        self.heldKeys = set()
        self.quitting = False

        self.bestTime = loadBestTime()
        self.reset()

    # ----- race state ---------------------------------------------------------------
    def reset(self):
        """Put every runner back in the blocks and restart the countdown."""
        for runner in self.runners:
            runner.reset()

        self.state = "countdown"
        self.countdown = 3.4
        self.raceTime = 0

        self.direction = 0  # -1 left, 0 still, +1 right
        self.sprinting = False
        self.stamina = MAX_STAMINA

        self.passedHurdles = set()
        self.leader = None
        self.confetti = []
        self.results = []
        self.newRecord = False

        self.sayTimer = 0
        self.narrativeText.text = NARRATIVE[0]

    def say(self, text, hold=2.0, force=False):
        """Post a line of commentary, unless a more recent one is still on screen."""
        if force or self.sayTimer <= 0:
            self.narrativeText.text = text
            self.sayTimer = hold

    # ----- Exercise 2: keyboard control ---------------------------------------------
    def on_key_press(self, key, modifiers):
        self.heldKeys.add(key)

        if key == arcade.key.ESCAPE:
            self.quitting = True
            self.close()

        elif key == arcade.key.R:
            self.reset()

        # Jumping is the one action that is a tap, not a hold
        elif key in (arcade.key.SPACE, arcade.key.UP) and self.state == "racing":
            self.player.startJump()

    def on_key_release(self, key, modifiers):
        self.heldKeys.discard(key)

    def readHeldKeys(self):
        """
        Work out the direction and the sprint from whatever is held right now.
        Polling instead of reacting to key presses is what lets the player hold
        RIGHT through the countdown and still be moving the moment the gun goes.
        """
        right = arcade.key.RIGHT in self.heldKeys
        left = arcade.key.LEFT in self.heldKeys

        if right and not left:
            self.direction = 1
            self.player.facingRight = True
        elif left and not right:
            self.direction = -1
            self.player.facingRight = False
        else:
            self.direction = 0

        self.sprinting = bool(self.heldKeys & SPRINT_KEYS)

    # ----- game loop -----------------------------------------------------------------
    def on_update(self, deltaTime):
        # Arcade dispatches one more update after close(), by which point the
        # text objects no longer have a graphics context to talk to
        if self.quitting:
            return

        if self.sayTimer > 0:
            self.sayTimer -= deltaTime

        if self.state == "countdown":
            self.updateCountdown(deltaTime)

        elif self.state == "racing":
            self.raceTime += deltaTime
            self.updatePlayer(deltaTime)

            for runner in self.runners[1:]:
                runner.updateAi(deltaTime, self.raceTime, self.hurdleXs)
                runner.updatePhysics(deltaTime)

            self.checkHurdles()
            self.checkLead()
            self.checkFinish()

        self.updateConfetti(deltaTime)
        self.updateHud()

    def updateCountdown(self, deltaTime):
        self.countdown -= deltaTime

        # Read out the pre-race narrative while the starter takes his time.
        # Leaning on RIGHT during the countdown is allowed - the runner simply
        # goes the instant the gun fires.
        line = min(int((3.4 - self.countdown) / 1.1), len(NARRATIVE) - 1)
        self.narrativeText.text = NARRATIVE[line]

        if self.countdown <= 0:
            self.state = "racing"
            self.countdownText.text = ""
            self.say("They're away! Hold RIGHT and chase them down!", force=True)
        else:
            self.countdownText.text = "GO!" if self.countdown < 0.4 else str(
                int(self.countdown)
            )

    def updatePlayer(self, deltaTime):
        player = self.player
        self.readHeldKeys()

        speed = BASE_SPEED
        sprinting = self.sprinting and self.direction != 0 and self.stamina > 0

        if sprinting:
            speed *= SPRINT_MULTIPLIER
            self.stamina = max(0, self.stamina - deltaTime)
            if self.stamina == 0:
                self.say("Toby is running on empty - ease off and recover!", force=True)
        else:
            self.stamina = min(MAX_STAMINA, self.stamina + STAMINA_REGEN * deltaTime)

        if player.stumbleTime > 0:
            speed *= STUMBLE_PENALTY

        player.move(self.direction * speed * deltaTime)

        if player.onGround and player.stumbleTime <= 0:
            player.setState("walk" if self.direction != 0 else "idle")

        player.updatePhysics(deltaTime)
        ratio = 0 if self.direction == 0 else speed / (BASE_SPEED * SPRINT_MULTIPLIER)
        player.animate(deltaTime, speedRatio=ratio)

    def checkHurdles(self):
        """A runner who is not high enough when it reaches a hurdle trips over it."""
        for runner in self.runners:
            for index, hurdleX in enumerate(self.hurdleXs):
                key = (runner.name, index)
                if key in self.passedHurdles:
                    continue

                if abs(runner.x - hurdleX) > HURDLE_HALF_WIDTH:
                    continue

                self.passedHurdles.add(key)

                if runner.jumpOffset >= HURDLE_HEIGHT:
                    if runner.isPlayer:
                        self.say(f"Clean over hurdle {index + 1}!", hold=1.2)
                elif runner.isPlayer:
                    runner.stumble()
                    self.say(f"He clips hurdle {index + 1}! Toby stumbles!", force=True)
                else:
                    runner.stumble()
                    self.say(f"{runner.name} smashes into a hurdle!")

    def checkLead(self):
        leader = max(self.runners, key=lambda runner: runner.x)

        if leader is not self.leader and leader.x > START_X + 30:
            self.leader = leader
            if leader.isPlayer:
                self.say("Toby hits the front!")
            else:
                self.say(f"{leader.name} takes the lead!")

    def checkFinish(self):
        for runner in self.runners:
            if runner.finishTime is None and runner.x >= FINISH_X:
                runner.finishTime = self.raceTime

        if self.player.finishTime is not None:
            self.finishRace()

    def finishRace(self):
        """
        Freeze the race and work out the placings. Rivals still on the track are
        ranked on the time they were on course for - a photo finish, decided on paper.
        """
        self.state = "finished"

        standings = []
        for runner in self.runners:
            if runner.finishTime is not None:
                finishTime = runner.finishTime
            else:
                finishTime = self.raceTime + (FINISH_X - runner.x) / max(
                    runner.aiSpeed, 1
                )
            standings.append((finishTime, runner))

        standings.sort(key=lambda entry: entry[0])

        self.results = []
        for place, (finishTime, runner) in enumerate(standings, start=1):
            runner.place = place
            runner.setState("idle")
            self.results.append((place, runner.name, finishTime, runner.color))

            marker = ">" if runner.isPlayer else " "
            placeText, nameText, timeText = self.resultRows[place - 1]
            placeText.text = f"{marker} {place}"
            nameText.text = runner.name
            timeText.text = f"{finishTime:5.2f} s"

            for text in (placeText, nameText, timeText):
                text.color = runner.color

        playerTime = self.player.finishTime

        if self.bestTime is None or playerTime < self.bestTime:
            self.bestTime = playerTime
            self.newRecord = True
            saveBestTime(playerTime)

        if self.newRecord:
            self.resultFooter.text = "NEW PERSONAL BEST!"
            self.resultFooter.color = (235, 200, 60)
        else:
            self.resultFooter.text = "Press R to race again"
            self.resultFooter.color = arcade.color.WHITE

        if self.player.place == 1:
            self.say("TOBY TAKES IT! The stadium erupts!", force=True)
            self.spawnConfetti()
        else:
            self.say(
                f"Toby is beaten into {ordinal(self.player.place)}. Press R for a rematch.",
                force=True,
            )

    # ----- confetti ------------------------------------------------------------------
    def spawnConfetti(self):
        for _ in range(180):
            self.confetti.append(
                {
                    "x": random.uniform(0, SCREEN_WIDTH),
                    "y": random.uniform(SCREEN_HEIGHT, SCREEN_HEIGHT + 320),
                    "vx": random.uniform(-35, 35),
                    "vy": random.uniform(-170, -70),
                    "size": random.uniform(4, 9),
                    "color": random.choice(CONFETTI_COLORS),
                }
            )

    def updateConfetti(self, deltaTime):
        if not self.confetti:
            return

        for piece in self.confetti:
            piece["x"] += piece["vx"] * deltaTime
            piece["y"] += piece["vy"] * deltaTime

        self.confetti = [piece for piece in self.confetti if piece["y"] > -20]

    # ----- drawing --------------------------------------------------------------------
    def updateHud(self):
        self.timeText.text = f"{self.raceTime:5.2f} s"
        self.distanceText.text = f"{self.player.metres:5.1f} / {RACE_DISTANCE} m"

        if self.player.place is not None:
            place = self.player.place
        else:
            # Mid-race the position is simply how many turtles are further down the track
            place = sum(1 for runner in self.runners if runner.x > self.player.x) + 1
        self.placeText.text = f"{ordinal(place)} of {LANE_COUNT}"

        if self.bestTime is None:
            self.bestText.text = "Best: --.--  (first race)"
        else:
            self.bestText.text = f"Best: {self.bestTime:.2f} s"

    def on_draw(self):
        self.clear()

        self.drawCrowd()
        self.drawTrack()
        self.spriteList.draw()
        self.drawHud()
        self.drawConfetti()

        if self.state == "countdown":
            self.countdownText.draw()
        elif self.state == "finished":
            self.drawResults()

    def drawCrowd(self):
        arcade.draw_lrbt_rectangle_filled(
            0, SCREEN_WIDTH, CROWD_BOTTOM - 14, CROWD_TOP + 10, (72, 82, 96)
        )
        for x, y, color in self.crowd:
            arcade.draw_circle_filled(x, y, 3.5, color)

    def drawTrack(self):
        for lane, runner in enumerate(self.runners):
            groundY = runner.baseY - SHADOW_DROP
            bottom = groundY - 4
            top = bottom + LANE_SPACING

            # Alternating lane colours so the four lanes read apart
            shade = TRACK_LIGHT if lane % 2 == 0 else TRACK_DARK
            arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, bottom, top, shade)
            arcade.draw_line(0, top, SCREEN_WIDTH, top, (245, 245, 245, 120), 2)

            arcade.draw_line(START_X, bottom, START_X, top, arcade.color.WHITE, 2)
            self.laneTexts[lane].draw()

            for hurdleX in self.hurdleXs:
                self.drawHurdle(hurdleX, groundY)

            self.drawFinishLine(bottom, top)

    def drawHurdle(self, x, groundY):
        arcade.draw_line(x - 9, groundY, x - 9, groundY + HURDLE_HEIGHT, (240, 240, 240), 3)
        arcade.draw_line(x + 9, groundY, x + 9, groundY + HURDLE_HEIGHT, (240, 240, 240), 3)
        arcade.draw_lrbt_rectangle_filled(
            x - 13,
            x + 13,
            groundY + HURDLE_HEIGHT - 7,
            groundY + HURDLE_HEIGHT,
            (225, 90, 70),
        )

    def drawFinishLine(self, bottom, top):
        """Checkered finish line, two squares wide."""
        square = 9
        row = 0
        y = bottom
        while y < top:
            for column in range(2):
                dark = (row + column) % 2 == 0
                color = arcade.color.BLACK if dark else arcade.color.WHITE
                arcade.draw_lrbt_rectangle_filled(
                    FINISH_X + column * square,
                    FINISH_X + (column + 1) * square,
                    y,
                    min(y + square, top),
                    color,
                )
            y += square
            row += 1

    def drawHud(self):
        # Top bar
        arcade.draw_lrbt_rectangle_filled(
            0, SCREEN_WIDTH, 540, SCREEN_HEIGHT, (28, 36, 48)
        )
        self.timeText.draw()
        self.distanceText.draw()
        self.placeText.draw()
        self.bestText.draw()

        # Stamina bar
        barLeft, barRight, barBottom, barTop = 560, 780, 550, 566
        arcade.draw_lrbt_rectangle_filled(
            barLeft, barRight, barBottom, barTop, (60, 70, 84)
        )
        fill = barLeft + (barRight - barLeft) * (self.stamina / MAX_STAMINA)
        color = (235, 200, 60) if self.stamina > 1.0 else (225, 90, 70)
        if fill > barLeft:
            arcade.draw_lrbt_rectangle_filled(barLeft, fill, barBottom, barTop, color)
        self.staminaText.draw()

        # Bottom commentary bar
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, 58, (28, 36, 48))
        self.narrativeText.draw()
        self.helpText.draw()

    def drawConfetti(self):
        for piece in self.confetti:
            arcade.draw_lrbt_rectangle_filled(
                piece["x"],
                piece["x"] + piece["size"],
                piece["y"],
                piece["y"] + piece["size"] * 1.6,
                piece["color"],
            )

    def drawResults(self):
        left, right, bottom, top = 230, 570, 175, 425
        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, (28, 36, 48, 235))
        arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, (235, 200, 60), 3)

        self.resultTitle.draw()

        for placeText, nameText, timeText in self.resultRows:
            placeText.draw()
            nameText.draw()
            timeText.draw()

        self.resultFooter.draw()


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "ex"

    if mode == "1":
        task1()
        return

    if mode == "2":
        Task2Window()
    elif mode == "3":
        Task3Window()
    else:
        TurtleSprintGame()

    arcade.run()


if __name__ == "__main__":
    main()
