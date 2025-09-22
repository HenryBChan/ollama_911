from turtle import Screen
import pygame
import time
import numpy as np
import pyaudio
import wave
import threading
import pyttsx3
import os
import shutil

out_dir = "out"

# If "out" exists, delete it
if os.path.exists(out_dir):
    shutil.rmtree(out_dir)

# Recreate a fresh "out" directory
os.makedirs(out_dir)

print(f'Directory "{out_dir}" has been reset.')

# Initialize pyttsx3 TTS engine
engine = pyttsx3.init()

# Try to select a female voice
voices = engine.getProperty('voices')
for voice in voices:
    if "female" in voice.name.lower() or "zira" in voice.name.lower() or "samantha" in voice.name.lower():
        engine.setProperty('voice', voice.id)
        break

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((400, 400))
pygame.display.set_caption("Voice UI")

# Load button image
button_image = pygame.image.load("images/phone_button.jpg")
button_image = pygame.transform.scale(button_image, (100, 100))
button_rect = button_image.get_rect(center=(300, 300))

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Fonts
font = pygame.font.Font(None, 36)

# Audio setup
CHUNK = 4096  # Increased buffer for smoother recording
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
NOISE_THRESHOLD = 1000  # Adjust this based on ambient noise levels
THRESHOLD_LOW = 10  # Offset so spectrum bottom can be moved up
p = pyaudio.PyAudio()

# Open a global stream for spectrum analysis
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

# Frequency range for human voice (approximately 85Hz to 255Hz fundamental, with harmonics)
LOW_FREQ = 85
HIGH_FREQ = 3000  # Include some harmonics for visualization

# State variables
recording = False
backend_processing = False
processing_start_time = 0
spectrum = np.zeros(20, dtype=int)
audio_frames = []
recording_thread = None


def get_audio_spectrum():
    if not recording:
        return np.full(20, THRESHOLD_LOW, dtype=int)
    
    data = np.frombuffer(stream.read(CHUNK, exception_on_overflow=False), dtype=np.int16)
    volume = np.max(np.abs(data))
    
    if volume < NOISE_THRESHOLD:
        return np.full(20, THRESHOLD_LOW, dtype=int)  # Flat spectrum with offset if below noise threshold
    
    fft_data = np.abs(np.fft.rfft(data))
    freqs = np.fft.rfftfreq(len(data), 1.0 / RATE)
    
    # Focus on the human speech range
    mask = (freqs >= LOW_FREQ) & (freqs <= HIGH_FREQ)
    fft_data = fft_data[mask]
    
    fft_data = np.log1p(fft_data)  # Log scaling for better visualization
    fft_data = np.interp(fft_data[:20], (0, np.max(fft_data)), (THRESHOLD_LOW, 100))  # Doubled max height
    return fft_data.astype(int)


def draw_spectrum(spectrum, y_offset):
    x = 50
    for bar in spectrum:
        pygame.draw.rect(screen, GREEN, (x, y_offset - bar, 10, bar))
        x += 15


def save_audio():
    global out_dir
    if not audio_frames:
        return
    wf = wave.open(f"{out_dir}/recorded_audio.wav", "wb")
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b"".join(audio_frames))
    wf.close()


def record_audio():
    global recording, audio_frames
    local_stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    while recording:
        data = local_stream.read(CHUNK, exception_on_overflow=False)
        audio_frames.append(data)
    local_stream.stop_stream()
    local_stream.close()

# 911 Woman
mouth_closed_img = pygame.image.load("images/911_women_closed.png")
mouth_open_img = pygame.image.load("images/911_women_open.png")
mouth_closed_img = pygame.transform.scale(mouth_closed_img, (100, 100))
mouth_open_img = pygame.transform.scale(mouth_open_img, (100, 100))

# Variables for mouth animation
current_img = mouth_closed_img
last_switch_time = 0
mouth_open = False

# Global talking flag
talking = False

# Speak function runs in a thread
def speak(text):
    global talking
    talking = True
    engine.say(text)
    engine.runAndWait()
    talking = False

running = True
while running:
    current_time = time.time()
    screen.fill(BLACK)
    
    # Backend processing check
    if backend_processing:
        if time.time() - processing_start_time > 2:
            backend_processing = False
    
    # Draw button
    screen.blit(button_image, button_rect.topleft)
    
    # Draw status text
    status_text = "No Speak" if backend_processing else "Speak Now"
    status_color = RED if backend_processing else GREEN
    text_surface = font.render(status_text, True, status_color)
    screen.blit(text_surface, (160, 200))
    
    # Draw recording spectrum continuously while button is pressed
    if recording:
        spectrum = get_audio_spectrum()
    draw_spectrum(spectrum, 150)
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and button_rect.collidepoint(event.pos):
            if not backend_processing:
                recording = True
                audio_frames = []  # Reset audio frames for new recording
                recording_thread = threading.Thread(target=record_audio, daemon=True)
                recording_thread.start()
        elif event.type == pygame.MOUSEBUTTONUP and recording:
            recording = False
            if recording_thread:
                recording_thread.join()
            backend_processing = True
            processing_start_time = time.time()
            save_audio()

    if not talking:
        operater_voice_txt = None  # default if file not found
        operater_voice_txt_file = f"{out_dir}/operater_voice.txt"
        if os.path.exists(operater_voice_txt_file):
            with open(operater_voice_txt_file, "r", encoding="utf-8") as f:
                operater_voice_txt = f.read()
            os.remove(operater_voice_txt_file)  # delete after reading
            # print("operater_voice.txt was read and deleted.")
            threading.Thread(target=speak, args=(operater_voice_txt,)).start()

    if talking:
        if current_time - last_switch_time > 0.25:  # Switch every 250 ms
            mouth_open = not mouth_open
            last_switch_time = current_time
    else:
        mouth_open = False  # Keep it closed when not talking

    current_img = mouth_open_img if mouth_open else mouth_closed_img 
    screen.blit(current_img, (50, 250))
    pygame.display.flip()
    pygame.time.delay(5)  # Reduced delay for smoother real-time responsiveness

# Close the global spectrum stream
stream.stop_stream()
stream.close()
p.terminate()
pygame.quit()