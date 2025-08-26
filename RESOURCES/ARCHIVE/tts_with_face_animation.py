import pyttsx3
import threading
import time
import pygame

# Initialize pyttsx3 TTS engine
engine = pyttsx3.init()

# Try to select a female voice
voices = engine.getProperty('voices')
for voice in voices:
    if "female" in voice.name.lower() or "zira" in voice.name.lower() or "samantha" in voice.name.lower():
        engine.setProperty('voice', voice.id)
        break

# Global talking flag
talking = False

# Speak function runs in a thread
def speak(text):
    global talking
    talking = True
    engine.say(text)
    engine.runAndWait()
    talking = False

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((400, 400))
pygame.display.set_caption("Talking Avatar")

# Load and resize images
mouth_closed_img = pygame.image.load("images/911_women_closed.png")
mouth_open_img = pygame.image.load("images/911_women_open.png")
mouth_closed_img = pygame.transform.scale(mouth_closed_img, (300, 300))
mouth_open_img = pygame.transform.scale(mouth_open_img, (300, 300))

# Variables for mouth animation
current_img = mouth_closed_img
last_switch_time = 0
mouth_open = False

# Clock
clock = pygame.time.Clock()

# Main loop
running = True
while running:
    current_time = time.time()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not talking:
                    threading.Thread(target=speak, args=("Hello, I'm speaking to you right now!",)).start()

    # Animate mouth if talking
    if talking:
        if current_time - last_switch_time > 0.25:  # Switch every 250 ms
            mouth_open = not mouth_open
            last_switch_time = current_time
    else:
        mouth_open = False  # Keep it closed when not talking

    current_img = mouth_open_img if mouth_open else mouth_closed_img

    screen.fill((255, 255, 255))
    screen.blit(current_img, (50, 50))
    pygame.display.update()
    clock.tick(60)

pygame.quit()
