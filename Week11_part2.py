from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance, ImageOps

ASSET_DIR = Path(__file__).parent / "lab" / "asset"
SCENE_PATH = ASSET_DIR / "background.jpeg"
CHARACTER_PATH = ASSET_DIR / "character.png"

# only enlarge small images, background.jpeg is already 1024x600
SCALE = 1

# using opencv
image = cv2.imread(str(SCENE_PATH))
w, h = image.shape[:2]
image = cv2.resize(image, (h * SCALE, w * SCALE))

# using pillow
img1 = Image.open(SCENE_PATH).convert("RGBA")
img2 = Image.open(CHARACTER_PATH).convert("RGBA")
w, h = img1.size
img1 = img1.resize((w * SCALE, h * SCALE), Image.LANCZOS)
img2 = img2.resize(img1.size, Image.LANCZOS)


# Gaussian noise
def addGaussianNoise():
    # 0=average value-centre of noise, 10-noise strength
    noise = np.random.normal(0, 10, image.shape)
    # add in a wider type then clip, casting negative noise straight to uint8 wraps to 255
    noisyImg = np.clip(image.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    cv2.imshow("GaussianNoise", noisyImg)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# Salt and pepper noise
def saltPepperNoise():
    noisyImg = np.copy(image)

    # white noise - 5%
    saltMask = np.random.random(image.shape[:2]) < 0.05
    noisyImg[saltMask] = 255

    # black noise - 5%
    pepperMask = np.random.random(image.shape[:2]) < 0.05
    noisyImg[pepperMask] = 0

    cv2.imshow("SaltPepperNoise", noisyImg)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def blendImage():
    blendedImg = Image.blend(img1, img2, 0.5)  # alpha 0.5
    blendedImg.show()


def compositeImage():
    # compositeImg.paste(img2, (100,200), img2) #paste image at specific position
    overlay = img2.copy()
    overlay.putalpha(100)  # add transparency
    compositeImg = Image.alpha_composite(img1, overlay)
    compositeImg.show()


def addMask():
    # Create a mask
    mask = Image.new("L", img1.size, 0)
    draw = ImageDraw.Draw(mask)

    # white ellipse -view area
    draw.ellipse((50, 50, 250, 250), fill=255)
    maskImage = Image.new("RGBA", img1.size)
    maskImage.paste(img1, (0, 0), mask=mask)
    maskImage.show()


def gaussionBlur():
    blurImage = img1.filter(ImageFilter.GaussianBlur(radius=5))
    blurImage.show()


def SharpeningImage():
    # radius - Blur Radius
    # percent - Unsharp strength, in percent
    # threshold - minimum brightness change that will be sharpened
    sharpImage = img1.filter(ImageFilter.UnsharpMask(10, 100, 4))
    sharpImage.show()


# ---------------------------------------------------------------
# Task: other pillow filters + background brightness
# ---------------------------------------------------------------
def otherFilters():
    rgbImg = img1.convert("RGB")
    filters = {
        "Contour": rgbImg.filter(ImageFilter.CONTOUR),
        "Emboss": rgbImg.filter(ImageFilter.EMBOSS),
        "Find Edges": rgbImg.filter(ImageFilter.FIND_EDGES),
        "Box Blur": rgbImg.filter(ImageFilter.BoxBlur(4)),
        "Median": rgbImg.filter(ImageFilter.MedianFilter(5)),
        "Posterize": ImageOps.posterize(rgbImg, 3),
    }
    showGrid(filters, "Pillow Filters")


def adjustBrightness():
    rgbImg = img1.convert("RGB")
    enhancer = ImageEnhance.Brightness(rgbImg)
    # factor 1.0 = original, < 1 darker, > 1 brighter
    levels = {
        "Brightness 0.4": enhancer.enhance(0.4),
        "Brightness 0.7": enhancer.enhance(0.7),
        "Original": rgbImg,
        "Brightness 1.3": enhancer.enhance(1.3),
        "Brightness 1.6": enhancer.enhance(1.6),
        "Contrast 1.5": ImageEnhance.Contrast(rgbImg).enhance(1.5),
    }
    showGrid(levels, "Background Brightness")
    enhancer.enhance(1.3).save(ASSET_DIR / "backgroundBright.png")
    enhancer.enhance(0.6).save(ASSET_DIR / "backgroundDark.png")


def showGrid(images: dict, title: str, columns: int = 3):
    # thumbnails with labels on one canvas
    thumbW, thumbH = 400, 235
    rows = (len(images) + columns - 1) // columns
    canvas = Image.new("RGB", (thumbW * columns, (thumbH + 30) * rows), "white")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()

    for i, (name, img) in enumerate(images.items()):
        x = (i % columns) * thumbW
        y = (i // columns) * (thumbH + 30)
        canvas.paste(img.resize((thumbW, thumbH)), (x, y + 30))
        draw.text((x + 10, y + 8), name, fill="black", font=font)

    canvas.show(title=title)


if __name__ == "__main__":
    menu = {
        "1": ("Gaussian noise", addGaussianNoise),
        "2": ("Salt and pepper noise", saltPepperNoise),
        "3": ("Blend images", blendImage),
        "4": ("Composite images", compositeImage),
        "5": ("Mask", addMask),
        "6": ("Gaussian blur", gaussionBlur),
        "7": ("Sharpen", SharpeningImage),
        "8": ("Task: other filters", otherFilters),
        "9": ("Task: brightness", adjustBrightness),
    }
    while True:
        for key, (name, _) in menu.items():
            print(f"[{key}] {name}")
        choice = input("Choose (q to quit): ").strip().lower()
        if choice == "q":
            break
        if choice in menu:
            menu[choice][1]()
