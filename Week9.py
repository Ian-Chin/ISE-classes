import arcade
import arcade.gui
import random
import math
import numpy as np
from PIL import Image

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Smoke Simulation"

BACKGROUND = (25, 28, 35)

emissionRate = 35
PARTICLE_LIFETIME = 6.0
SPAWN_RADIUS = 2

class SmokeParticle:
    def __init__(self, x, y):
        self.x = x + random.uniform(-SPAWN_RADIUS, SPAWN_RADIUS)
        self.y = y + random.uniform(-SPAWN_RADIUS, SPAWN_RADIUS)

        self.vx = random.uniform(-25, 25)
        self.vy = random.uniform(60, 80)

        self.radius = random.uniform(5, 12)
        self.max_radius = random.uniform(50, 100)

        self.age = 0.0
        self.lifetime = random.uniform(4.0, PARTICLE_LIFETIME)

        self.drift = random.uniform(-25, 25)
        self.gray = random.randint(100, 180)

    def update(self, dt):
        self.age += dt
        progress = min(self.age / self.lifetime, 1.0)

        # Rise upward
        self.y += self.vy * dt

        # Spread sideways
        spread = 0.3 + progress
        self.x += (self.vx + self.drift * spread) * dt

        # Expand smoothly
        self.radius = 5 + (self.max_radius - 5) * progress

        # turbulence
        self.drift += random.uniform(-12, 12) * dt
        self.drift = max(-45, min(45, self.drift))

    def draw(self):
        progress = min(self.age / self.lifetime, 1.0)
        fade = (1.0 - progress) ** 1.5

        layers = [
            (1.00, 8),
            (0.82, 10),
            (0.64, 12),
            (0.46, 15),
            (0.28, 18),
        ]

        for scale, base_alpha in layers:
            radius = self.radius * scale
            alpha = int(base_alpha * fade)

            if alpha > 0:
                arcade.draw_circle_filled(
                    self.x,
                    self.y,
                    radius,
                    (
                        self.gray,
                        self.gray,
                        self.gray,
                        alpha,
                    ),
                )

    @property
    def is_dead(self):
        return self.age >= self.lifetime

GRID_WIDTH = 160
GRID_HEIGHT = 120

GRID_SIZE_X = SCREEN_WIDTH / GRID_WIDTH
GRID_SIZE_Y = SCREEN_HEIGHT / GRID_HEIGHT

RISE_SPEED = 7.0
WIND_STRENGTH = 3.0
SMOKE_SPREAD_SPEED = 0.20
SMOKE_DISAPPEAR_SPEED = 0.05
EMISSION_SPEED = 2.0

emissionX = SCREEN_WIDTH // 2
emissionY = 85

class ProceduralSmoke:
    def __init__(self):
        self.density = np.zeros(
            (GRID_HEIGHT, GRID_WIDTH),
            dtype=np.float32,
        )

        self.time = 0.0

        yy, xx = np.mgrid[0:GRID_HEIGHT, 0:GRID_WIDTH]
        self.xx = xx.astype(np.float32)
        self.yy = yy.astype(np.float32)

        self.source_x = emissionX / GRID_SIZE_X
        self.source_y = emissionY / GRID_SIZE_Y

        # Precalculate the source shape.
        self.source = np.exp(
            -(
                (self.xx - self.source_x) ** 2
                + (self.yy - self.source_y) ** 2
            ) / 5.0
        ).astype(np.float32)

        self.texture = None

    def update(self, dt):
        self.time += dt

        pulse = 0.85 + 0.15 * math.sin(self.time * 1.2)

        # Emit smoke.
        self.density += (
            self.source * EMISSION_SPEED * pulse * dt
        )

        # Move smoke upward and sideways.
        sample_x = np.clip(
            self.xx - WIND_STRENGTH * dt,
            0,
            GRID_WIDTH - 1.001,
        )

        sample_y = np.clip(
            self.yy - RISE_SPEED * dt,
            0,
            GRID_HEIGHT - 1.001,
        )

        # Bilinear interpolation.
        x0 = sample_x.astype(np.int32)
        y0 = sample_y.astype(np.int32)

        x1 = np.minimum(x0 + 1, GRID_WIDTH - 1)
        y1 = np.minimum(y0 + 1, GRID_HEIGHT - 1)

        fx = sample_x - x0
        fy = sample_y - y0

        d00 = self.density[y0, x0]
        d10 = self.density[y0, x1]
        d01 = self.density[y1, x0]
        d11 = self.density[y1, x1]

        moved = (
            d00 * (1 - fx) * (1 - fy)
            + d10 * fx * (1 - fy)
            + d01 * (1 - fx) * fy
            + d11 * fx * fy
        )

        self.density = moved

        # Diffuse smoke into neighboring cells.
        center = self.density

        left = np.roll(center, 1, axis=1)
        right = np.roll(center, -1, axis=1)
        down = np.roll(center, -1, axis=0)
        up = np.roll(center, 1, axis=0)

        average = (left + right + down + up) * 0.25

        self.density += SMOKE_SPREAD_SPEED * (
            average - center
        )

        # Gradually dissipate smoke.
        self.density *= math.exp(
            -SMOKE_DISAPPEAR_SPEED * dt
        )

        np.clip(self.density, 0.0, 1.0, out=self.density)

    def draw(self):
        d = self.density

        opacity = np.clip(
            d * 200, 0, 200
        ).astype(np.uint8)

        gray = np.clip(
            100 + d * 50, 0, 150
        ).astype(np.uint8)

        rgba = np.zeros(
            (GRID_HEIGHT, GRID_WIDTH, 4),
            dtype=np.uint8,
        )

        rgba[:, :, 0] = gray
        rgba[:, :, 1] = gray
        rgba[:, :, 2] = gray
        rgba[:, :, 3] = opacity

        # Convert the density grid into a texture.
        image = Image.fromarray(rgba[::-1].copy())

        self.texture = arcade.Texture(image)

        arcade.draw_texture_rect(
            self.texture,
            arcade.LBWH(
                0,
                0,
                SCREEN_WIDTH,
                SCREEN_HEIGHT,
            ),
        )

def backButton(view):
    button = arcade.gui.UIFlatButton(
        text="Back to Menu",
        width=180,
        height=45,
    )

    @button.event("on_click")
    def on_click(event):
        view.window.show_view(MainMenuView())

    view.ui_manager.add(button)
    return button

class MainMenuView(arcade.View):
    def __init__(self):
        super().__init__()

        self.ui_manager = arcade.gui.UIManager()
        self.ui_manager.enable()

        # (button text, view class) for every effect in the menu.
        self.options = [
            ("Particle Smoke", ParticleSmokeView),
            ("Generative Smoke", generativeSmokeView),
            ("Fire Simulation", FireView),
            ("Snow Simulation", SnowView),
            ("Firework Simulation", FireworkView),
        ]

        self.buttons = []

        for text, view_class in self.options:
            button = arcade.gui.UIFlatButton(
                text=text,
                width=300,
                height=50,
            )

            @button.event("on_click")
            def on_click(event, view_class=view_class):
                self.window.show_view(view_class())

            self.ui_manager.add(button)
            self.buttons.append(button)

    def on_draw(self):
        self.clear()

        arcade.draw_text(
            "EFFECTS Example",
            SCREEN_WIDTH / 2,
            520,
            arcade.color.WHITE,
            30,
            anchor_x="center",
            bold=True,
        )

        arcade.draw_text(
            "Select an effect",
            SCREEN_WIDTH / 2,
            480,
            (190, 195, 205),
            17,
            anchor_x="center",
        )

        self.ui_manager.draw()

    def on_show_view(self):
        arcade.set_background_color(BACKGROUND)
        self.ui_manager.enable()

        for i, button in enumerate(self.buttons):
            button.center_x = SCREEN_WIDTH / 2
            button.center_y = 410 - i * 70

    def on_hide_view(self):
        self.ui_manager.disable()

class ParticleSmokeView(arcade.View):
    def __init__(self):
        super().__init__()

        self.particles = []
        self.emission_accumulator = 0.0

        self.source_x = SCREEN_WIDTH // 2
        self.source_y = 100

        self.ui_manager = arcade.gui.UIManager()
        self.ui_manager.enable()

        self.back_button = backButton(self)

    def on_show_view(self):
        arcade.set_background_color(BACKGROUND)
        self.ui_manager.enable()

        self.back_button.center_x = 110
        self.back_button.center_y = SCREEN_HEIGHT - 40

    def on_hide_view(self):
        self.ui_manager.disable()

    def on_update(self, dt):
        self.emission_accumulator += dt * emissionRate

        while self.emission_accumulator >= 1.0:
            self.particles.append(
                SmokeParticle(self.source_x, self.source_y)
            )
            self.emission_accumulator -= 1.0

        for particle in self.particles:
            particle.update(dt)

        self.particles = [
            particle
            for particle in self.particles
            if not particle.is_dead
        ]

    def on_draw(self):
        self.clear()

        for particle in self.particles:
            particle.draw()

        # Smoke emitter.
        arcade.draw_circle_filled(
            self.source_x,
            self.source_y,
            5,
            (155, 160, 170),
        )

        arcade.draw_text(
            "Particle Smoke",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT - 40,
            arcade.color.WHITE,
            20,
            anchor_x="center",
        )

        self.ui_manager.draw()

class generativeSmokeView(arcade.View):
    def __init__(self):
        super().__init__()

        self.smoke = ProceduralSmoke()

        self.ui_manager = arcade.gui.UIManager()
        self.ui_manager.enable()

        self.back_button = backButton(self)

    def on_show_view(self):
        arcade.set_background_color((255, 255, 255))
        self.ui_manager.enable()

        self.back_button.center_x = 110
        self.back_button.center_y = SCREEN_HEIGHT - 40

    def on_hide_view(self):
        self.ui_manager.disable()

    def on_update(self, dt):
        dt = min(dt, 1.0 / 30.0)
        self.smoke.update(dt)

    def on_draw(self):
        self.clear()

        self.smoke.draw()

        arcade.draw_circle_filled(
            emissionX,
            emissionY,
            5,
            (155, 160, 170),
        )

        arcade.draw_text(
            "Generative Method",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT - 40,
            arcade.color.BLACK,
            20,
            anchor_x="center",
        )

        self.ui_manager.draw()


FIRE_EMISSION_RATE = 90
FIRE_SOURCE_X = SCREEN_WIDTH // 2
FIRE_SOURCE_Y = 80
FIRE_BASE_WIDTH = 70

FIRE_COLORS = [
    (0.00, (255, 250, 200)),
    (0.20, (255, 210, 60)),
    (0.45, (255, 120, 20)),
    (0.70, (200, 40, 10)),
    (1.00, (60, 50, 50)),
]

def fireColor(progress):
    for i in range(len(FIRE_COLORS) - 1):
        p0, c0 = FIRE_COLORS[i]
        p1, c1 = FIRE_COLORS[i + 1]

        if progress <= p1:
            t = (progress - p0) / (p1 - p0)
            return tuple(int(c0[k] + (c1[k] - c0[k]) * t) for k in range(3))

    return FIRE_COLORS[-1][1]

class FireParticle:
    def __init__(self, x, y):
        offset = random.gauss(0, FIRE_BASE_WIDTH / 4)
        self.x = x + offset
        self.y = y + random.uniform(-3, 3)

        self.vx = -offset * 0.4 + random.uniform(-10, 10)
        self.vy = random.uniform(90, 160)

        self.radius = random.uniform(12, 20)

        self.age = 0.0
        center_bonus = 1.0 - min(abs(offset) / FIRE_BASE_WIDTH, 1.0)
        self.lifetime = random.uniform(0.5, 0.9) + center_bonus * 0.6

        self.flicker = random.uniform(0, math.pi * 2)

    def update(self, dt):
        self.age += dt

        self.vy += 40 * dt
        self.y += self.vy * dt

        # Flicker sideways.
        self.x += (self.vx + math.sin(self.age * 12 + self.flicker) * 25) * dt
        self.vx *= 0.96

    def draw(self):
        progress = min(self.age / self.lifetime, 1.0)

        # Flames shrink as they rise.
        radius = self.radius * (1.0 - progress * 0.7)
        r, g, b = fireColor(progress)
        alpha = int(110 * (1.0 - progress) ** 1.2)

        if alpha > 0:
            self.drawTriangle(radius * 1.6, (r, g, b, alpha // 4))
            self.drawTriangle(radius, (r, g, b, alpha))

    def drawTriangle(self, size, color):
        # Upward-pointing triangle centred on the particle.
        arcade.draw_triangle_filled(
            self.x, self.y + size,
            self.x - size * 0.866, self.y - size * 0.5,
            self.x + size * 0.866, self.y - size * 0.5,
            color,
        )

    @property
    def is_dead(self):
        return self.age >= self.lifetime

class FireView(arcade.View):
    def __init__(self):
        super().__init__()

        self.particles = []
        self.emission_accumulator = 0.0

        self.ui_manager = arcade.gui.UIManager()
        self.ui_manager.enable()

        self.back_button = backButton(self)

    def on_show_view(self):
        arcade.set_background_color((15, 10, 10))
        self.ui_manager.enable()

        self.back_button.center_x = 110
        self.back_button.center_y = SCREEN_HEIGHT - 40

    def on_hide_view(self):
        self.ui_manager.disable()

    def on_update(self, dt):
        self.emission_accumulator += dt * FIRE_EMISSION_RATE

        while self.emission_accumulator >= 1.0:
            self.particles.append(FireParticle(FIRE_SOURCE_X, FIRE_SOURCE_Y))
            self.emission_accumulator -= 1.0

        for particle in self.particles:
            particle.update(dt)

        self.particles = [
            particle
            for particle in self.particles
            if not particle.is_dead
        ]

    def on_draw(self):
        self.clear()

        # Glow on the ground under the fire.
        arcade.draw_ellipse_filled(FIRE_SOURCE_X, FIRE_SOURCE_Y - 10, 260, 50, (255, 100, 20, 25))

        # Additive blending makes overlapping flames brighter.
        self.window.ctx.blend_func = self.window.ctx.BLEND_ADDITIVE
        for particle in self.particles:
            particle.draw()
        self.window.ctx.blend_func = self.window.ctx.BLEND_DEFAULT

        # Logs.
        arcade.draw_lbwh_rectangle_filled(FIRE_SOURCE_X - 80, FIRE_SOURCE_Y - 30, 160, 18, (90, 55, 30))
        arcade.draw_lbwh_rectangle_filled(FIRE_SOURCE_X - 60, FIRE_SOURCE_Y - 18, 120, 14, (110, 70, 40))

        arcade.draw_text(
            "Fire Simulation",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT - 40,
            arcade.color.WHITE,
            20,
            anchor_x="center",
        )

        self.ui_manager.draw()

# ---------------- Snow ----------------

SNOWFLAKE_COUNT = 300
SNOW_GROUND_COLUMNS = 80
SNOW_MAX_HEIGHT = 120

class Snowflake:
    def __init__(self, start_on_screen=False):
        self.reset()

        if start_on_screen:
            self.y = random.uniform(0, SCREEN_HEIGHT)

    def reset(self):
        self.x = random.uniform(0, SCREEN_WIDTH)
        self.y = SCREEN_HEIGHT + random.uniform(5, 50)

        # Bigger flakes are closer, so they fall faster and look brighter.
        self.size = random.uniform(1.5, 4.5)
        self.vy = 25 + self.size * 15
        self.alpha = int(120 + self.size * 30)

        self.sway_speed = random.uniform(0.5, 2.0)
        self.sway_amount = random.uniform(10, 30)
        self.phase = random.uniform(0, math.pi * 2)
        self.time = 0.0

    def update(self, dt, wind):
        self.time += dt
        self.y -= self.vy * dt
        self.x += (wind + math.sin(self.time * self.sway_speed + self.phase) * self.sway_amount) * dt

        # Wrap around the sides.
        if self.x < 0:
            self.x += SCREEN_WIDTH
        elif self.x > SCREEN_WIDTH:
            self.x -= SCREEN_WIDTH

    def draw(self):
        arcade.draw_circle_filled(self.x, self.y, self.size, (255, 255, 255, min(self.alpha, 255)))

class SnowView(arcade.View):
    def __init__(self):
        super().__init__()

        self.flakes = [Snowflake(start_on_screen=True) for _ in range(SNOWFLAKE_COUNT)]

        self.ground = [0.0] * SNOW_GROUND_COLUMNS
        self.time = 0.0

        self.ui_manager = arcade.gui.UIManager()
        self.ui_manager.enable()

        self.back_button = backButton(self)

    def on_show_view(self):
        arcade.set_background_color((20, 30, 55))
        self.ui_manager.enable()

        self.back_button.center_x = 110
        self.back_button.center_y = SCREEN_HEIGHT - 40

    def on_hide_view(self):
        self.ui_manager.disable()

    def on_update(self, dt):
        self.time += dt

        wind = math.sin(self.time * 0.3) * 30

        column_width = SCREEN_WIDTH / SNOW_GROUND_COLUMNS

        for flake in self.flakes:
            flake.update(dt, wind)

            column = min(int(flake.x / column_width), SNOW_GROUND_COLUMNS - 1)

            if flake.y <= self.ground[column]:
                if self.ground[column] < SNOW_MAX_HEIGHT:
                    self.ground[column] += flake.size * 1.0
                flake.reset()

        smoothed = self.ground[:]
        for i in range(1, SNOW_GROUND_COLUMNS - 1):
            smoothed[i] = self.ground[i] * 0.9 + (self.ground[i - 1] + self.ground[i + 1]) * 0.05
        self.ground = smoothed

    def on_draw(self):
        self.clear()

        for flake in self.flakes:
            flake.draw()

        column_width = SCREEN_WIDTH / SNOW_GROUND_COLUMNS
        points = [(0, 0)]
        for i, height in enumerate(self.ground):
            points.append((i * column_width + column_width / 2, height))
        points.append((SCREEN_WIDTH, 0))
        arcade.draw_polygon_filled(points, (235, 240, 250))

        arcade.draw_text(
            "Snow Simulation",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT - 40,
            arcade.color.WHITE,
            20,
            anchor_x="center",
        )

        self.ui_manager.draw()


GRAVITY = 120
FIREWORK_COLORS = [
    (255, 80, 80),
    (255, 200, 60),
    (80, 200, 255),
    (140, 255, 120),
    (220, 120, 255),
    (255, 255, 255),
]

class Spark:
    def __init__(self, x, y, vx, vy, color, lifetime, size):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.age = 0.0
        self.lifetime = lifetime
        self.size = size
        self.trail = []

    def update(self, dt):
        self.age += dt

        self.trail.append((self.x, self.y))
        if len(self.trail) > 6:
            self.trail.pop(0)

        self.vy -= GRAVITY * dt
        self.vx *= 0.985
        self.vy *= 0.985

        self.x += self.vx * dt
        self.y += self.vy * dt

    def draw(self):
        progress = min(self.age / self.lifetime, 1.0)
        alpha = int(255 * (1.0 - progress))

        # Twinkle near the end of its life.
        if progress > 0.7 and random.random() < 0.3:
            return

        r, g, b = self.color

        for i, (tx, ty) in enumerate(self.trail):
            trail_alpha = int(alpha * (i + 1) / (len(self.trail) + 1) * 0.5)
            arcade.draw_circle_filled(tx, ty, self.size * 0.6, (r, g, b, trail_alpha))

        arcade.draw_circle_filled(self.x, self.y, self.size, (r, g, b, alpha))

    @property
    def is_dead(self):
        return self.age >= self.lifetime

class Rocket:
    def __init__(self, x=None, target_y=None):
        self.x = x if x is not None else random.uniform(150, SCREEN_WIDTH - 150)
        self.y = 0
        self.vx = random.uniform(-20, 20)
        self.vy = random.uniform(380, 450)

        self.target_y = target_y if target_y is not None else random.uniform(320, 480)
        self.color = random.choice(FIREWORK_COLORS)
        self.exploded = False

    def update(self, dt, sparks):
        self.vy -= GRAVITY * 0.5 * dt
        self.x += self.vx * dt
        self.y += self.vy * dt

        sparks.append(
            Spark(
                self.x, self.y,
                random.uniform(-15, 15), random.uniform(-40, -10),
                (255, 200, 120), random.uniform(0.2, 0.4), 1.5,
            )
        )

        if self.y >= self.target_y or self.vy <= 0:
            self.explode(sparks)

    def explode(self, sparks):
        self.exploded = True

        count = random.randint(70, 110)
        speed = random.uniform(160, 240)

        second_color = random.choice(FIREWORK_COLORS)

        for i in range(count):
            angle = (i / count) * math.pi * 2 + random.uniform(-0.05, 0.05)
            s = speed * random.uniform(0.85, 1.0)
            color = self.color if i % 2 == 0 else second_color

            sparks.append(
                Spark(
                    self.x, self.y,
                    math.cos(angle) * s, math.sin(angle) * s,
                    color, random.uniform(1.2, 2.0), 2.5,
                )
            )

    def draw(self):
        arcade.draw_circle_filled(self.x, self.y, 3, (255, 230, 180))

class FireworkView(arcade.View):
    def __init__(self):
        super().__init__()

        self.rockets = []
        self.sparks = []
        self.launch_timer = 0.0

        self.ui_manager = arcade.gui.UIManager()
        self.ui_manager.enable()

        self.back_button = backButton(self)

    def on_show_view(self):
        arcade.set_background_color((5, 5, 20))
        self.ui_manager.enable()

        self.back_button.center_x = 110
        self.back_button.center_y = SCREEN_HEIGHT - 40

    def on_hide_view(self):
        self.ui_manager.disable()

    def on_mouse_press(self, x, y, button, modifiers):
        # Click to launch a firework that explodes at the mouse position.
        if y < SCREEN_HEIGHT - 80:
            self.rockets.append(Rocket(x, y))

    def on_update(self, dt):
        self.launch_timer -= dt

        if self.launch_timer <= 0:
            self.rockets.append(Rocket())
            self.launch_timer = random.uniform(0.6, 1.4)

        for rocket in self.rockets:
            rocket.update(dt, self.sparks)

        self.rockets = [rocket for rocket in self.rockets if not rocket.exploded]

        for spark in self.sparks:
            spark.update(dt)

        self.sparks = [spark for spark in self.sparks if not spark.is_dead]

    def on_draw(self):
        self.clear()

        self.window.ctx.blend_func = self.window.ctx.BLEND_ADDITIVE
        for spark in self.sparks:
            spark.draw()
        for rocket in self.rockets:
            rocket.draw()
        self.window.ctx.blend_func = self.window.ctx.BLEND_DEFAULT

        arcade.draw_text(
            "Firework Simulation",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT - 40,
            arcade.color.WHITE,
            20,
            anchor_x="center",
        )

        arcade.draw_text(
            "Click to launch a firework",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT - 70,
            (170, 175, 190),
            13,
            anchor_x="center",
        )

        self.ui_manager.draw()

window = arcade.Window(
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    SCREEN_TITLE,
)

window.show_view(MainMenuView())
arcade.run()
