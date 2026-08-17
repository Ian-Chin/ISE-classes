"""Week 2 - Part 4: Screen recording with pyscreenrecorder.

    pip install pyscreenrecorder
"""

from pyscreenrecorder import ScreenRecorder

print("start....")
ScreenRecorder(
    filename="examplewithPyScreenRecorder.mp4",
    duration=5,
    fps=60,
    monitor_number=1,
    resolution=(1920, 1080),
    mouse=True,
    mouse_color=(255, 0, 0),
    mouse_size=10,
    mouse_thickness=3,
)
print("done")
