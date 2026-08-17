"""Week 2 - Exercise: capture video (webcam or screen) WITH sound."""

import argparse
import os
import queue
import subprocess
import tempfile
import time
import wave
import cv2
import numpy as np
import sounddevice as sd
import imageio_ffmpeg


RATE = 44100          # audio sample rate
CHANNELS = 1          # 1 - mono, 2 - stereo
CHUNK = 1024          # frames per audio buffer
SAMPLE_WIDTH = 2      # int16 -> 2 bytes


def open_video_source(source):
    """Return (read_frame, close, width, height) for the chosen source."""
    if source == "camera":
        cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            raise RuntimeError("not able to open computer camera")

        width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

        def read_frame():
            result, image = cam.read()
            return image if result else None

        return read_frame, cam.release, width, height

    import mss 
    sct = mss.mss()
    monitor = sct.monitors[1]          # monitor 1 = primary display
    # ffmpeg's H.264 encoder needs even dimensions
    width = monitor["width"] - monitor["width"] % 2
    height = monitor["height"] - monitor["height"] % 2

    def read_frame():
        shot = np.asarray(sct.grab(monitor))          # BGRA
        return cv2.cvtColor(shot[:height, :width], cv2.COLOR_BGRA2BGR)

    return read_frame, sct.close, width, height


def record(source, duration, output, preview):
    read_frame, close_source, width, height = open_video_source(source)

    tmp_dir = tempfile.mkdtemp(prefix="week2_")
    video_path = os.path.join(tmp_dir, "video.avi")
    audio_path = os.path.join(tmp_dir, "audio.wav")


    audio_queue = queue.Queue()

    def audio_callback(indata, frames, time_info, status):
        if status:
            print("audio status:", status)
        audio_queue.put(bytes(indata))

    frames = []
    stream = sd.RawInputStream(samplerate=RATE, channels=CHANNELS,
                               dtype='int16', blocksize=CHUNK,
                               callback=audio_callback)

    print("recording... press 'q' in the preview window to stop"
          if preview else "recording...")

    started = time.time()
    frame_count = 0
    with stream:
        while True:
            image = read_frame()
            if image is None:
                print("Not able to capture frame (stream ending)")
                break

            frames.append(image)
            frame_count += 1

            if preview:
                cv2.imshow('Recording - press q to stop', image)
                if cv2.waitKey(1) == ord('q'):
                    break

            if duration and time.time() - started >= duration:
                break

    elapsed = time.time() - started
    close_source()
    if preview:
        cv2.destroyAllWindows()

    # Drain whatever the callback produced.
    audio_chunks = []
    try:
        while True:
            audio_chunks.append(audio_queue.get_nowait())
    except queue.Empty:
        pass

    if frame_count == 0:
        raise RuntimeError("no video frames were captured")

    fps = frame_count / elapsed
    print(f"captured {frame_count} frames in {elapsed:.1f}s -> {fps:.1f} fps")

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    writer = cv2.VideoWriter(video_path, fourcc, fps, (width, height))
    for image in frames:
        writer.write(image)
    writer.release()

    audio_bytes = b''.join(audio_chunks)
    print(f"captured {len(audio_bytes) / (RATE * CHANNELS * SAMPLE_WIDTH):.1f}s of audio")

    wf = wave.open(audio_path, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(SAMPLE_WIDTH)
    wf.setframerate(RATE)
    wf.writeframes(audio_bytes)
    wf.close()

    # Mux the silent video and the WAV into a single playable file.
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    command = [ffmpeg, "-y", "-i", video_path]
    if audio_bytes:
        command += ["-i", audio_path]
    command += ["-c:v", "libx264", "-pix_fmt", "yuv420p"]
    if audio_bytes:
        # -shortest would truncate the video if the audio track came up short.
        command += ["-c:a", "aac", "-shortest"]
    command.append(output)
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr[-2000:])
        raise RuntimeError("ffmpeg failed to merge the audio and video")

    print("saved", os.path.abspath(output))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", choices=["camera", "screen"],
                        default="camera")
    parser.add_argument("--duration", type=float, default=0,
                        help="seconds to record (0 = until 'q' is pressed)")
    parser.add_argument("--output", default="myrecording.mp4")
    parser.add_argument("--no-preview", action="store_true",
                        help="hide the preview window (needs --duration)")
    args = parser.parse_args()

    preview = not args.no_preview
    if not preview and not args.duration:
        parser.error("--no-preview requires --duration, otherwise there is "
                     "no way to stop the recording")

    record(args.source, args.duration, args.output, preview)



main();
