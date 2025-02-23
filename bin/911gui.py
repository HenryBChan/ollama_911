import pygame
import time
import random
import numpy as np
import pyaudio

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
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

# State variables
recording = False
backend_processing = False
processing_start_time = 0
spectrum = []
tts_spectrum = []

def get_audio_spectrum():
    data = np.frombuffer(stream.read(CHUNK, exception_on_overflow=False), dtype=np.int16)
    fft_data = np.abs(np.fft.rfft(data))
    fft_data = np.log1p(fft_data)  # Log scaling for better visualization
    if fft_data.max() > 0:
        fft_data = np.interp(fft_data[:20], (fft_data.min(), fft_data.max()), (1, 50))
    else:
        fft_data = np.zeros(20)
    return fft_data.astype(int)

# def smooth_spectrum(previous_spectrum, new_spectrum, smoothing_factor=0.7):
#     return (smoothing_factor * np.array(previous_spectrum) + (1 - smoothing_factor) * np.array(new_spectrum)).astype(int)

def draw_spectrum(spectrum, y_offset):
    x = 50
    for bar in spectrum:
        pygame.draw.rect(screen, GREEN, (x, y_offset - bar, 10, bar))
        x += 15

running = True
while running:
    screen.fill(WHITE)
    
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
    
    # Draw recording spectrum
    if recording:
        spectrum = get_audio_spectrum()
        # spectrum = smooth_spectrum(spectrum, new_spectrum) if spectrum else new_spectrum
    # else:
    #     spectrum = []
    draw_spectrum(spectrum, 150)
    
    # # Draw TTS spectrum
    # if not backend_processing:
    #     tts_spectrum = get_audio_spectrum() if random.random() > 0.8 else []  # Simulating TTS playback
    # else:
    #     tts_spectrum = []
    # draw_spectrum(tts_spectrum, 250)
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and button_rect.collidepoint(event.pos):
            if not backend_processing:
                recording = True
        elif event.type == pygame.MOUSEBUTTONUP and recording:
            recording = False
            backend_processing = True
            processing_start_time = time.time()
    
    pygame.display.flip()
    pygame.time.delay(100)

stream.stop_stream()
stream.close()
p.terminate()
pygame.quit()