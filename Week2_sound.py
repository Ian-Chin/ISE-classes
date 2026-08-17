"""Week 2 - Part 3: Sound recording (5 seconds -> mysound.wav)."""

import wave

# Parameters for the recording
chunk = 1024
rate = 44100          # Sample rate per second
channel = 1           # audio channel (1 - mono, 2 - stereo)
second = 5            # Duration
outputWaveFile = "mysound.wav"

try:
    import pyaudio

    format = pyaudio.paInt16  # Audio format

    # Initialize PyAudio
    p = pyaudio.PyAudio()

    # stream for recording
    stream = p.open(format=format,
                    channels=channel,
                    rate=rate,
                    input=True,
                    frames_per_buffer=chunk)

    frames = []
    print("* Recording started...")

#44100/1024*5 = 215 iterations
    for i in range(0, int(rate / chunk * second)):
        data = stream.read(chunk)
        frames.append(data)

    print("* Recording finished.")

    stream.stop_stream()
    stream.close()
    p.terminate()  # Terminate PyAudio object

    sampleWidth = p.get_sample_size(format)
    audio = b''.join(frames)

except ImportError:
    import sounddevice as sd

    print("PyAudio not available - using sounddevice instead.")
    print("* Recording started...")

    recording = sd.rec(int(rate * second),
                       samplerate=rate,
                       channels=channel,
                       dtype='int16',
                       blocksize=chunk)
    sd.wait()

    print("* Recording finished.")

    sampleWidth = 2
    audio = recording.tobytes()

# Save the audio data to WAV file
wf = wave.open(outputWaveFile, 'wb')
wf.setnchannels(channel)
wf.setsampwidth(sampleWidth)
wf.setframerate(rate)
wf.writeframes(audio)
wf.close()

print("completed")
