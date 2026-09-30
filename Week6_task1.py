# Week 6 - Task 1
# Work out the new coordinates of the rectangle by hand (with the computer helping).
# Order of the transformation:
#   1. scale 1.1 in x and y
#   2. rotate 10 degrees counterclockwise about the origin
#   3. translate 20 units in x and y
#   4. horizontal shear with factor 0.2
#   5. reflect on the x-axis

import math

# multiply two matrices (A x B)
def multiply(A, B):
    return [
        [
            sum(A[i][k] * B[k][j] for k in range(len(B)))
            for j in range(len(B[0]))
        ]
        for i in range(len(A))
    ]

# apply a 3x3 matrix on one point (x, y)
def transformPoint(M, x, y):
    result = multiply(M, [[x], [y], [1]])
    return result[0][0], result[1][0]

def scaling(sx, sy):
    return [
        [sx, 0, 0],
        [0, sy, 0],
        [0, 0, 1]
    ]

# counterclockwise rotation
def rotation(angle):
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

# horizontal shear
def skew(k):
    return [
        [1, k, 0],
        [0, 1, 0],
        [0, 0, 1]
    ]

# reflection on the x-axis (y becomes -y)
def reflection():
    return [
        [1,  0, 0],
        [0, -1, 0],
        [0,  0, 1]
    ]

# the rectangle A, B, C, D
names = ["A", "B", "C", "D"]
shape = [
    (0, 0),
    (200, 0),
    (200, 100),
    (0, 100)
]

# print one step nicely
def showStep(title, points):
    print(title)
    for name, (x, y) in zip(names, points):
        print(f"  {name}({x:.2f}, {y:.2f})")
    print()

showStep("Original rectangle:", shape)

steps = [
    ("Step 1 - scale 1.1:", scaling(1.1, 1.1)),
    ("Step 2 - rotate 10 degrees counterclockwise:", rotation(10)),
    ("Step 3 - translate 20 units:", translation(20, 20)),
    ("Step 4 - horizontal shear 0.2:", skew(0.2)),
    ("Step 5 - reflect on x-axis:", reflection())
]

# M keeps all the transformations that have been done so far
M = [
    [1, 0, 0],
    [0, 1, 0],
    [0, 0, 1]
]

for title, matrix in steps:
    M = multiply(matrix, M)
    points = [transformPoint(M, x, y) for x, y in shape]
    showStep(title, points)

print("Final combined matrix:")
for row in M:
    print("  [", ", ".join(f"{value:8.4f}" for value in row), "]")
