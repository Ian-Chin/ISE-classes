from pathlib import Path

import cv2 as cv
import numpy as np
import matplotlib.pyplot as plot
import pygame

ASSET_DIR = Path(__file__).parent / "lab" / "asset"
SCENE_PATH = ASSET_DIR / "background.jpeg"

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


# ---------------------------------------------------------------
# Part 1: image manipulation tutorial
# ---------------------------------------------------------------
def imageTutorial():
    # Load  image
    image = cv.imread(str(SCENE_PATH))

    # understanding image
    print("Original shape: ", image.shape)
    print("Original Size: ", image.size)
    h, w, d = image.shape
    # scale factor 2 only for small images, otherwise the stacked window gets too wide
    scale = 2 if w < 600 else 1
    newimg = cv.resize(image, (w * scale, h * scale))
    print("new shape: ", newimg.shape)
    print("new Size: ", newimg.size)

    # display the image
    cv.imshow('Original - New Image', image)
    cv.imshow('New Image', newimg)
    cv.waitKey(0)
    cv.destroyAllWindows()

    # Convert to different color spaces
    grayImg = cv.cvtColor(newimg, cv.COLOR_BGR2GRAY)
    hsvImg = cv.cvtColor(newimg, cv.COLOR_BGR2HSV)
    labImg = cv.cvtColor(newimg, cv.COLOR_BGR2LAB)

    combineImages = np.hstack((newimg, hsvImg, labImg))
    cv.namedWindow('converted - new, hsv, lab Image', cv.WINDOW_NORMAL)
    cv.imshow('converted - new, hsv, lab Image', combineImages)
    cv.waitKey(0)
    cv.destroyAllWindows()

    b, g, r = cv.split(newimg)
    h, s, v = cv.split(hsvImg)

    # channels
    zeros = np.zeros_like(b)
    rgbImg = cv.merge((r, g, b))
    RedChannel = cv.merge((zeros, zeros, r))  # bgr
    BlueChannel = cv.merge((b, zeros, zeros))
    GreenChannel = cv.merge((zeros, g, zeros))

    # beta - brightness
    # alpha - contrast
    updatedImage1 = cv.convertScaleAbs(newimg, alpha=1, beta=0.5)
    updatedImage2 = cv.convertScaleAbs(newimg, alpha=1.5, beta=1)

    # Display the images
    cv.imshow('new Image', newimg)
    cv.imshow('Grayscale Image', grayImg)
    cv.imshow('rbg Image', rgbImg)
    cv.imshow('darker Image', updatedImage1)
    cv.imshow('brighter Image', updatedImage2)
    cv.waitKey(0)
    cv.destroyAllWindows()

    images = [image, grayImg, hsvImg, labImg, rgbImg, RedChannel, BlueChannel, GreenChannel]
    titles = ['Original Image', 'Grayscale Image', 'HSV Image', 'LAB Image', 'RGB Image', 'Red Channel', 'Blue channel', 'green channel']

    # Plot the images
    plot.figure(figsize=(10, 8))
    for i in range(len(images)):
        plot.subplot(4, 2, i + 1)
        plot.imshow(images[i], cmap='gray' if len(images[i].shape) == 2 else None)
        plot.title(titles[i])
        plot.axis('off')

    plot.tight_layout()
    plot.show()


# ---------------------------------------------------------------
# Part 2: task - adjusted backgrounds used as pygame scene
# ---------------------------------------------------------------
def buildBackgrounds(path: Path) -> dict:
    scene = cv.imread(str(path))
    scene = cv.resize(scene, (SCREEN_WIDTH, SCREEN_HEIGHT))

    b, g, r = cv.split(scene)
    zeros = np.zeros_like(b)

    return {
        "Original": scene,
        "Red Channel": cv.merge((zeros, zeros, r)),
        "Green Channel": cv.merge((zeros, g, zeros)),
        "Blue Channel": cv.merge((b, zeros, zeros)),
        "Brighter": cv.convertScaleAbs(scene, alpha=1.0, beta=60),
        "Darker": cv.convertScaleAbs(scene, alpha=0.5, beta=0),
    }


def toSurface(bgrImage: np.ndarray) -> pygame.Surface:
    # opencv is BGR (rows, cols), pygame wants RGB (cols, rows)
    rgbImage = cv.cvtColor(bgrImage, cv.COLOR_BGR2RGB)
    return pygame.surfarray.make_surface(rgbImage.swapaxes(0, 1))


def runPygameScene():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("OpenCV Background in Pygame")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)

    backgrounds = buildBackgrounds(SCENE_PATH)
    names = list(backgrounds.keys())
    surfaces = [toSurface(backgrounds[name]) for name in names]
    current = 1  # start on red channel scene

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif pygame.K_1 <= event.key <= pygame.K_6:
                    current = event.key - pygame.K_1

        screen.blit(surfaces[current], (0, 0))

        label = font.render(f"[1-6] Background: {names[current]}", True, (255, 255, 255))
        pygame.draw.rect(screen, (0, 0, 0), (10, 10, label.get_width() + 20, label.get_height() + 12))
        screen.blit(label, (20, 16))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    imageTutorial()
    runPygameScene()
