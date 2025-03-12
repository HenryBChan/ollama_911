import pygame
import time
import numpy as np
import pyaudio
import wave

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((400, 400))
pygame.display.set_caption("Voice UI")

# Load button image
button_image = pygame.image.load("images/phone_button.jpg")
button_image = pygame.transform.scale(button_image, (100, 100))
button_rect = button_image.get_rect(center=(200, 300))

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Fonts
font = pygame.font.Font(None, 36)

# Audio setup
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
NOISE_THRESHOLD = 1000  # Adjust this based on ambient noise levels
THRESHOLD_LOW = 10  # Offset so spectrum bottom can be moved up
p = pyaudio.PyAudio()
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

def get_audio_spectrum():
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
    wf = wave.open("recorded_audio.wav", "wb")
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b"".join(audio_frames))
    wf.close()

running = True
while running:
    screen.fill(BLACK)
    
    # Backend processing check
    if backend_processing:
        if time.time() - processing_start_time > 2:
            backend_processing = False
    
    # Draw button
    screen.blit(button_image, button_rect.topleft)
    
    # Draw status text
    status_text = "No Speak" if backend_processing else "Speak"
    status_color = RED if backend_processing else GREEN
    text_surface = font.render(status_text, True, status_color)
    screen.blit(text_surface, (160, 200))
    
    # Draw recording spectrum continuously while button is pressed
    if recording:
        spectrum = get_audio_spectrum()
        audio_frames.append(stream.read(CHUNK, exception_on_overflow=False))
    draw_spectrum(spectrum, 150)
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and button_rect.collidepoint(event.pos):
            if not backend_processing:
                recording = True
                audio_frames = []  # Reset audio frames for new recording
        elif event.type == pygame.MOUSEBUTTONUP and recording:
            recording = False
            backend_processing = True
            processing_start_time = time.time()
            save_audio()
    
    pygame.display.flip()
    pygame.time.delay(10)  # Reduced delay for more real-time responsiveness

stream.stop_stream()
stream.close()
p.terminate()
pygame.quit()
