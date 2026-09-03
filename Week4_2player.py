"""
Week 4 (two player version): the turtle hurdles race, but lane 1 and lane 2 are
both driven by a human. Lanes 3 and 4 stay under AI control.

All four turtles are still cut out of the same sprite sheet with Pillow - the
rivals are the same frames put through a hue rotation.

Controls:
    Player 1 : LEFT / RIGHT run, UP or SPACE jump, RIGHT SHIFT sprint
    Player 2 : A / D run, W jump, LEFT SHIFT sprint
    R        : race again
    ESC      : quit
"""

import math
import random
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


# --------------------------------------------------------------------------------------
# Cutting the sheet up with Pillow (same helpers as the single player version)
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
# Race settings
# --------------------------------------------------------------------------------------
ANIMATIONS = {
    "idle": [0],
    "walk": [0, 1, 2, 3, 4, 5, 7],
    "jump": [6],
    "stumble": [4, 5],
}

NARRATIVE = [
    "SHELLBOURNE STADIUM - Final of the 100 m Turtle Hurdles.",
    "Toby in lane 1, Shellina in lane 2, and two rivals behind them.",
    "Two turtles, two sets of controls. The starter raises the gun...",
]

# Track layout
START_X = 90
FINISH_X = SCREEN_WIDTH - 70
RACE_DISTANCE = 100  # metres, for the on-screen readout
LANE_COUNT = 4
LANE_BOTTOM = 130  # y of the lowest runner's centre
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

BEST_TIME_FILE = Path(__file__).parent / "lab" / "best_time_2p.txt"

# Two control schemes, one per human lane
PLAYER_ONE_CONTROLS = {
    "left": {arcade.key.LEFT},
    "right": {arcade.key.RIGHT},
    "jump": {arcade.key.UP, arcade.key.SPACE},
    "sprint": {arcade.key.RSHIFT},
}

PLAYER_TWO_CONTROLS = {
    "left": {arcade.key.A},
    "right": {arcade.key.D},
    "jump": {arcade.key.W},
    "sprint": {arcade.key.LSHIFT},
}

# Runner name, hue rotation, label on the scoreboard, and the control scheme.
# A control scheme of None means the turtle is driven by the AI.
RUNNERS = [
    ("Toby", 0, "P1", PLAYER_ONE_CONTROLS),  # green, player 1
    ("Shellina", 90, "P2", PLAYER_TWO_CONTROLS),  # blue, player 2
    ("Bruno", 190, "  ", None),  # magenta, AI
    ("Zippy", 268, "  ", None),  # yellow, AI
]

# The green of the turtle's skin, taken from the sprite sheet itself
TURTLE_GREEN = (70, 205, 100)

# Palette
SKY = (120, 195, 235)
TRACK_LIGHT = (206, 124, 88)
TRACK_DARK = (188, 108, 74)
CROWD_BOTTOM = 458
CROWD_TOP = 512
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

HUD_BOTTOM = 522


def metresToX(metres):
    return START_X + (metres / RACE_DISTANCE) * (FINISH_X - START_X)


def ordinal(number):
    return {1: "1st", 2: "2nd", 3: "3rd"}.get(number, f"{number}th")


def loadBestTime():
    """Read the best time on this track from disk, ignoring a missing or corrupt file."""
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

    def __init__(self, name, lane, color, textures, mirroredTextures, label, controls):
        self.name = name
        self.lane = lane
        self.color = color
        self.textures = textures
        self.mirroredTextures = mirroredTextures
        self.label = label

        # A human runner carries a control scheme, an AI runner does not
        self.controls = controls
        self.isHuman = controls is not None

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

        # Human input state, read fresh every frame from the held keys
        self.direction = 0  # -1 left, 0 still, +1 right
        self.sprinting = False
        self.stamina = MAX_STAMINA

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

    # ----- human control -------------------------------------------------------------
    def readHeldKeys(self, heldKeys):
        """
        Work out the direction and the sprint from whatever is held right now.
        Polling instead of reacting to key presses is what lets a player hold
        their run key through the countdown and still be moving when the gun goes.
        """
        right = bool(heldKeys & self.controls["right"])
        left = bool(heldKeys & self.controls["left"])

        if right and not left:
            self.direction = 1
            self.facingRight = True
        elif left and not right:
            self.direction = -1
            self.facingRight = False
        else:
            self.direction = 0

        self.sprinting = bool(heldKeys & self.controls["sprint"])

    def updateHuman(self, deltaTime, heldKeys):
        """One human lane: read the keys, burn or refill stamina, then move."""
        self.readHeldKeys(heldKeys)

        speed = BASE_SPEED
        sprinting = self.sprinting and self.direction != 0 and self.stamina > 0
        emptied = False

        if sprinting:
            speed *= SPRINT_MULTIPLIER
            self.stamina = max(0, self.stamina - deltaTime)
            emptied = self.stamina == 0
        else:
            self.stamina = min(MAX_STAMINA, self.stamina + STAMINA_REGEN * deltaTime)

        if self.stumbleTime > 0:
            speed *= STUMBLE_PENALTY

        self.move(self.direction * speed * deltaTime)

        if self.onGround and self.stumbleTime <= 0:
            self.setState("walk" if self.direction != 0 else "idle")

        self.updatePhysics(deltaTime)

        ratio = 0 if self.direction == 0 else speed / (BASE_SPEED * SPRINT_MULTIPLIER)
        self.animate(deltaTime, speedRatio=ratio)

        return emptied

    # ----- AI control ------------------------------------------------------------------
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
    """Four-turtle hurdles race with two human lanes sharing one keyboard."""

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Turtle 100 m Hurdles - 2 Players")
        self.background_color = SKY

        # Crop the sheet once with Pillow, then dress every runner from those frames
        pilFrames = cropFramesWithPillow(IMAGE_PATH, ROW_COUNT, COLUMN_COUNT)

        self.runners = []
        self.spriteList = arcade.SpriteList()

        for lane, (name, hue, label, controls) in enumerate(RUNNERS):
            runner = Runner(
                name,
                lane,
                hueShiftedColor(TURTLE_GREEN, hue),
                makeTextures(pilFrames, name, hue),
                makeTextures(pilFrames, name, hue, mirrored=True),
                label,
                controls,
            )
            self.runners.append(runner)
            self.spriteList.append(runner.sprite)

        # The two human lanes, in scoreboard order
        self.humans = [runner for runner in self.runners if runner.isHuman]

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
        self.timeText = arcade.Text(
            "", 400, 578, arcade.color.WHITE, 18, bold=True, anchor_x="center"
        )
        self.bestText = arcade.Text("", 16, 528, (200, 220, 235), 11)

        # One status line and one stamina bar per human lane
        self.playerTexts = []
        self.staminaLabels = []
        for index, runner in enumerate(self.humans):
            y = 574 - index * 26
            self.playerTexts.append(
                arcade.Text("", 16, y, runner.color, 15, bold=True)
            )
            self.staminaLabels.append(
                arcade.Text(f"{runner.label} SPRINT", 500, y + 1, runner.color, 11)
            )

        self.narrativeText = arcade.Text("", 16, 32, arcade.color.WHITE, 15)
        self.helpText = arcade.Text(
            "P1: LEFT/RIGHT run  UP jump  RSHIFT sprint     "
            "P2: A/D run  W jump  LSHIFT sprint     R again    ESC quit",
            16,
            11,
            (170, 190, 205),
            11,
        )
        self.countdownText = arcade.Text(
            "", SCREEN_WIDTH // 2, 320, arcade.color.WHITE, 78, bold=True,
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
            "RESULT", 400, 375, (235, 200, 60), 22, bold=True, anchor_x="center"
        )
        self.resultRows = []
        for row in range(LANE_COUNT):
            y = 332 - row * 30
            self.resultRows.append(
                (
                    arcade.Text("", 248, y, arcade.color.WHITE, 16, bold=True),
                    arcade.Text("", 310, y, arcade.color.WHITE, 16),
                    arcade.Text("", 470, y, arcade.color.WHITE, 16),
                )
            )
        self.resultWinner = arcade.Text(
            "", 400, 195, arcade.color.WHITE, 17, bold=True, anchor_x="center"
        )
        self.resultFooter = arcade.Text(
            "", 400, 172, arcade.color.WHITE, 13, anchor_x="center"
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

        self.passedHurdles = set()
        self.leader = None
        self.confetti = []
        self.newRecord = False

        self.sayTimer = 0
        self.narrativeText.text = NARRATIVE[0]

        for placeText, nameText, timeText in self.resultRows:
            placeText.text = ""
            nameText.text = ""
            timeText.text = ""

    def say(self, text, hold=2.0, force=False):
        """Post a line of commentary, unless a more recent one is still on screen."""
        if force or self.sayTimer <= 0:
            self.narrativeText.text = text
            self.sayTimer = hold

    # ----- keyboard -------------------------------------------------------------------
    def on_key_press(self, key, modifiers):
        self.heldKeys.add(key)

        if key == arcade.key.ESCAPE:
            self.quitting = True
            self.close()
            return

        if key == arcade.key.R:
            self.reset()
            return

        # Jumping is the one action that is a tap, not a hold, so each human
        # lane checks the key against its own scheme
        if self.state == "racing":
            for runner in self.humans:
                if key in runner.controls["jump"]:
                    runner.startJump()

    def on_key_release(self, key, modifiers):
        self.heldKeys.discard(key)

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

            for runner in self.runners:
                if runner.isHuman:
                    # A human who has already crossed the line coasts to a stop
                    if runner.finishTime is not None:
                        runner.setState("idle")
                        runner.updatePhysics(deltaTime)
                        runner.animate(deltaTime)
                        continue

                    if runner.updateHuman(deltaTime, self.heldKeys):
                        self.say(
                            f"{runner.name} is running on empty - ease off!", force=True
                        )
                else:
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
        # Leaning on a run key during the countdown is allowed - the runner
        # simply goes the instant the gun fires.
        line = min(int((3.4 - self.countdown) / 1.1), len(NARRATIVE) - 1)
        self.narrativeText.text = NARRATIVE[line]

        if self.countdown <= 0:
            self.state = "racing"
            self.countdownText.text = ""
            self.say("They're away! Two turtles, one finish line!", force=True)
        else:
            self.countdownText.text = "GO!" if self.countdown < 0.4 else str(
                int(self.countdown)
            )

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
                    if runner.isHuman:
                        self.say(
                            f"{runner.name} is clean over hurdle {index + 1}!", hold=1.2
                        )
                    continue

                runner.stumble()

                if runner.isHuman:
                    self.say(
                        f"{runner.name} clips hurdle {index + 1} and stumbles!",
                        force=True,
                    )
                else:
                    self.say(f"{runner.name} smashes into a hurdle!")

    def checkLead(self):
        leader = max(self.runners, key=lambda runner: runner.x)

        if leader is not self.leader and leader.x > START_X + 30:
            self.leader = leader
            self.say(f"{leader.name} takes the lead!")

    def checkFinish(self):
        for runner in self.runners:
            if runner.finishTime is None and runner.x >= FINISH_X:
                runner.finishTime = self.raceTime

                if runner.isHuman:
                    self.say(
                        f"{runner.name} crosses in {runner.finishTime:.2f} s!",
                        force=True,
                    )

        # The race is over once both humans are home
        if all(runner.finishTime is not None for runner in self.humans):
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

        for place, (finishTime, runner) in enumerate(standings, start=1):
            runner.place = place
            runner.setState("idle")

            placeText, nameText, timeText = self.resultRows[place - 1]
            placeText.text = f"{runner.label} {place}"
            nameText.text = runner.name
            timeText.text = f"{finishTime:5.2f} s"

            for text in (placeText, nameText, timeText):
                text.color = runner.color

        # Head to head: the human with the lower time wins the duel
        winner = min(self.humans, key=lambda runner: runner.finishTime)
        loser = max(self.humans, key=lambda runner: runner.finishTime)
        gap = loser.finishTime - winner.finishTime

        self.resultWinner.text = (
            f"{winner.label} WINS - {winner.name} by {gap:.2f} s"
        )
        self.resultWinner.color = winner.color

        if self.bestTime is None or winner.finishTime < self.bestTime:
            self.bestTime = winner.finishTime
            self.newRecord = True
            saveBestTime(winner.finishTime)

        if self.newRecord:
            self.resultFooter.text = "NEW TRACK RECORD!    Press R to race again"
            self.resultFooter.color = (235, 200, 60)
        else:
            self.resultFooter.text = "Press R to race again"
            self.resultFooter.color = arcade.color.WHITE

        if winner.place == 1:
            self.say(
                f"{winner.name} takes it, and beats the AI too! The stadium erupts!",
                force=True,
            )
            self.spawnConfetti()
        else:
            self.say(
                f"{winner.name} wins the duel but only finished "
                f"{ordinal(winner.place)} overall.",
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

        for index, runner in enumerate(self.humans):
            if runner.place is not None:
                place = runner.place
            else:
                # Mid-race the position is simply how many turtles are further
                # down the track
                place = sum(1 for other in self.runners if other.x > runner.x) + 1

            self.playerTexts[index].text = (
                f"{runner.label} {runner.name:9s}"
                f"{runner.metres:5.1f} / {RACE_DISTANCE} m   "
                f"{ordinal(place)} of {LANE_COUNT}"
            )

        if self.bestTime is None:
            self.bestText.text = "Track record: --.--  (first race)"
        else:
            self.bestText.text = f"Track record: {self.bestTime:.2f} s"

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

            # A human lane gets a coloured tab, so each player can find their own
            if runner.isHuman:
                arcade.draw_lrbt_rectangle_filled(0, 8, bottom, top, runner.color)

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
        # Top bar, tall enough for one row per player
        arcade.draw_lrbt_rectangle_filled(
            0, SCREEN_WIDTH, HUD_BOTTOM, SCREEN_HEIGHT, (28, 36, 48)
        )
        self.timeText.draw()
        self.bestText.draw()

        for index, runner in enumerate(self.humans):
            self.playerTexts[index].draw()
            self.staminaLabels[index].draw()
            self.drawStaminaBar(runner, 570 - index * 26)

        # Bottom commentary bar
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, 58, (28, 36, 48))
        self.narrativeText.draw()
        self.helpText.draw()

    def drawStaminaBar(self, runner, bottom):
        barLeft, barRight = 590, 784
        top = bottom + 15

        arcade.draw_lrbt_rectangle_filled(
            barLeft, barRight, bottom, top, (60, 70, 84)
        )

        fill = barLeft + (barRight - barLeft) * (runner.stamina / MAX_STAMINA)
        color = runner.color if runner.stamina > 1.0 else (225, 90, 70)

        if fill > barLeft:
            arcade.draw_lrbt_rectangle_filled(barLeft, fill, bottom, top, color)

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
        left, right, bottom, top = 210, 590, 155, 415
        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, (28, 36, 48, 235))
        arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, (235, 200, 60), 3)

        self.resultTitle.draw()

        for placeText, nameText, timeText in self.resultRows:
            placeText.draw()
            nameText.draw()
            timeText.draw()

        self.resultWinner.draw()
        self.resultFooter.draw()


def main():
    TurtleSprintGame()
    arcade.run()


if __name__ == "__main__":
    main()
