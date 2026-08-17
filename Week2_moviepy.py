"""moviepy"""

from moviepy import VideoFileClip, AudioFileClip

clip = VideoFileClip("myrecording.mp4")
print("original:", clip.duration, "seconds,", clip.size)

clip = clip.subclipped(0, 3)
clip = clip.resized(0.5)
sound = AudioFileClip("mysound.wav") 
sound = sound.subclipped(0, clip.duration)
clip = clip.with_audio(sound)

clip.write_videofile("moviepy_output.mp4")

clip.close()
sound.close()

print("done")
