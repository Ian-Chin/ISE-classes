# Week 6 - Task 2
# 2D transformation on a rectangle, controlled by the keyboard.
# Keys: r = rotate, t = translate, e = scale, m = reflect x-axis,
#       k = horizontal skew, space = reset

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

def rotation(angle):
    r = math.radians(angle)
    c = math.cos(r)
    s = math.sin(r)

    return [
        [c,  s, 0],
        [-s, c, 0],
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

def reflection():
    return [
        [1,  0, 0],
        [0, -1, 0],
        [0,  0, 1]
    ]

def skew(k):
    return [
        [1, k, 0],
        [0, 1, 0],
        [0, 0, 1]
    ]

# the rectangle
shape = [
    (0, 0),
    (200, 0),
    (200, 100),
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
skewFactor = 0.0
mirror = False

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
    facecolor="skyblue",
    edgecolor="blue",
    linewidth=3
)
ax.add_patch(polygon)

previousEventText = ax.text(
    0.5,
    1.08,
    "Last Event: None",
    transform=ax.transAxes,
    ha="center",
    va="center",
    fontsize=14,
    fontweight="bold"
)

instruction = ax.text(
    0.5,
    1.03,
    "R = Rotate   T = Translate   E = Scale   "
    "M = Reflection X-axis   K = Horizontal Skew   "
    "SPACE = Reset",
    transform=ax.transAxes,
    ha="center",
    va="center",
    fontsize=11
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
    global scaleFactor, skewFactor
    global mirror
    global previousEvent

    if event.key == "r":
        angle += 10
        R = rotation(10)
        M = multiply(R, M)
        previousEvent = f"R - Rotate Clockwise ({angle} degrees)"

    elif event.key == "t":
        tx += 20
        ty += 20
        T = translation(20, 20)
        M = multiply(T, M)
        previousEvent = f"T - Translation({tx}, {ty})"

    elif event.key == "e":
        scaleFactor += 0.1
        S = scaling(1.1, 1.1)
        M = multiply(S, M)
        previousEvent = f"E - Scale({scaleFactor:.2f})"

    elif event.key == "m":  # mirror
        mirror = not mirror
        F = reflection()
        M = multiply(F, M)
        previousEvent = f"M - Reflection about X-axis : {mirror}"

    elif event.key == "k":  # horizontal skew
        skewFactor += 0.2
        K = skew(0.2)
        M = multiply(K, M)
        previousEvent = f"K - Horizontal Skew ({skewFactor:.1f})"

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
        skewFactor = 0.0
        mirror = False
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
