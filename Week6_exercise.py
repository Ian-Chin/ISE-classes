# Week 6 - Exercise
# Same idea as Week6.py but with a 5 point shape and more transformations.
# Keys:
#   r = rotate clockwise        a = rotate anticlockwise
#   t = translate (+20, +20)    g = move left (-20 in x)
#   e = scale up (x1.1)         c = compress (x0.9)
#   m = reflect on x-axis       n = reflect on y-axis
#   k = horizontal skew         v = vertical skew
#   space = reset

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import math

# matrices calculation
def multiply(A, B):
    return [
        [
            sum(A[i][k] * B[k][j] for k in range(len(B)))
            for j in range(len(B[0]))
        ]
        for i in range(len(A))
    ]

# transformation matrix on one point
def transformPoint(M, x, y):
    result = multiply(M, [[x], [y], [1]])
    return result[0][0], result[1][0]

# clockwise rotation
def rotation(angle):
    r = math.radians(angle)
    c = math.cos(r)
    s = math.sin(r)

    return [
        [c,  s, 0],
        [-s, c, 0],
        [0,  0, 1]
    ]

# anticlockwise rotation
def rotationAnti(angle):
    r = math.radians(angle)
    c = math.cos(r)
    s = math.sin(r)

    return [
        [c, -s, 0],
        [s,  c, 0],
        [0,  0, 1]
    ]

def translation(tx, ty):
    return [
        [1, 0, tx],
        [0, 1, ty],
        [0, 0, 1]
    ]

def scaling(sx, sy):
    return [
        [sx, 0, 0],
        [0, sy, 0],
        [0, 0, 1]
    ]

# reflection on the x-axis (y becomes -y)
def reflectionX():
    return [
        [1,  0, 0],
        [0, -1, 0],
        [0,  0, 1]
    ]

# reflection on the y-axis (x becomes -x)
def reflectionY():
    return [
        [-1, 0, 0],
        [0,  1, 0],
        [0,  0, 1]
    ]

# horizontal skew
def skewX(k):
    return [
        [1, k, 0],
        [0, 1, 0],
        [0, 0, 1]
    ]

# vertical skew
def skewY(k):
    return [
        [1, 0, 0],
        [k, 1, 0],
        [0, 0, 1]
    ]

# 5 point shape (a house / pentagon shape)
shape = [
    (0, 0),
    (200, 0),
    (200, 100),
    (100, 180),
    (0, 100)
]

# transformation matrix (starts as the identity matrix)
M = [
    [1, 0, 0],
    [0, 1, 0],
    [0, 0, 1]
]

angle = 0
tx = 0
ty = 0
scaleFactor = 1.0
skewXFactor = 0.0
skewYFactor = 0.0
mirrorX = False
mirrorY = False

previousEvent = "None"

# plot
fig, ax = plt.subplots(figsize=(10, 7))
ax.set_xlim(-500, 500)
ax.set_ylim(-400, 400)
ax.set_aspect("equal")
ax.grid(True)
ax.axhline(0, color="black", linewidth=2)
ax.axvline(0, color="black", linewidth=2)

polygon = Polygon(
    shape,
    closed=True,
    facecolor="lightgreen",
    edgecolor="green",
    linewidth=3
)
ax.add_patch(polygon)

previousEventText = ax.text(
    0.5,
    1.10,
    "Last Event: None",
    transform=ax.transAxes,
    ha="center",
    va="center",
    fontsize=14,
    fontweight="bold"
)

instruction = ax.text(
    0.5,
    1.04,
    "R = Rotate CW   A = Rotate CCW   T = Translate   G = Move Left\n"
    "E = Scale Up   C = Compress   M = Reflect X   N = Reflect Y   "
    "K = Skew X   V = Skew Y   SPACE = Reset",
    transform=ax.transAxes,
    ha="center",
    va="center",
    fontsize=10
)

# redraw the shape with the current matrix
def update():

    transformed = [
        transformPoint(M, x, y)
        for x, y in shape
    ]
    polygon.set_xy(transformed)

    previousEventText.set_text(
        f"Last Event: {previousEvent}"
    )
    fig.canvas.draw_idle()

# key press
def on_key(event):
    global M
    global angle, tx, ty
    global scaleFactor, skewXFactor, skewYFactor
    global mirrorX, mirrorY
    global previousEvent

    if event.key == "r":  # rotate clockwise
        angle -= 10
        R = rotation(10)
        M = multiply(R, M)
        previousEvent = f"R - Rotate Clockwise ({angle} degrees)"

    elif event.key == "a":  # rotate anticlockwise
        angle += 10
        R = rotationAnti(10)
        M = multiply(R, M)
        previousEvent = f"A - Rotate Anticlockwise ({angle} degrees)"

    elif event.key == "t":  # translate
        tx += 20
        ty += 20
        T = translation(20, 20)
        M = multiply(T, M)
        previousEvent = f"T - Translation({tx}, {ty})"

    elif event.key == "g":  # move to the left
        tx -= 20
        T = translation(-20, 0)
        M = multiply(T, M)
        previousEvent = f"G - Move Left({tx}, {ty})"

    elif event.key == "e":  # scale up
        scaleFactor = scaleFactor * 1.1
        S = scaling(1.1, 1.1)
        M = multiply(S, M)
        previousEvent = f"E - Scale Up({scaleFactor:.2f})"

    elif event.key == "c":  # compress
        scaleFactor = scaleFactor * 0.9
        S = scaling(0.9, 0.9)
        M = multiply(S, M)
        previousEvent = f"C - Compress({scaleFactor:.2f})"

    elif event.key == "m":  # reflect on x-axis
        mirrorX = not mirrorX
        F = reflectionX()
        M = multiply(F, M)
        previousEvent = f"M - Reflection about X-axis : {mirrorX}"

    elif event.key == "n":  # reflect on y-axis
        mirrorY = not mirrorY
        F = reflectionY()
        M = multiply(F, M)
        previousEvent = f"N - Reflection about Y-axis : {mirrorY}"

    elif event.key == "k":  # horizontal skew
        skewXFactor += 0.2
        K = skewX(0.2)
        M = multiply(K, M)
        previousEvent = f"K - Horizontal Skew ({skewXFactor:.1f})"

    elif event.key == "v":  # vertical skew
        skewYFactor += 0.2
        K = skewY(0.2)
        M = multiply(K, M)
        previousEvent = f"V - Vertical Skew ({skewYFactor:.1f})"

    elif event.key == " ":  # reset
        M = [
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1]
        ]

        angle = 0
        tx = 0
        ty = 0
        scaleFactor = 1.0
        skewXFactor = 0.0
        skewYFactor = 0.0
        mirrorX = False
        mirrorY = False
        previousEvent = "SPACE - Reset"

    # update screen
    update()

# add key event
fig.canvas.mpl_connect(
    "key_press_event",
    on_key
)

update()
plt.show()
