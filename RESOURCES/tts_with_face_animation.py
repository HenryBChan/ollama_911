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

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((400, 400))
pygame.display.set_caption("Talking Avatar")

# Load images
mouth_closed_img = pygame.image.load("images/911_women_closed.png")
mouth_open_img = pygame.image.load("images/911_women_open.png")

# Resize images to fit the window
mouth_closed_img = pygame.transform.scale(mouth_closed_img, (300, 300))
mouth_open_img = pygame.transform.scale(mouth_open_img, (300, 300))

# Talking state
talking = False

# Function to animate mouth
def animate_mouth():
    global talking
    clock = pygame.time.Clock()
    current_img = mouth_closed_img
    while talking:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        # Toggle image to simulate talking
        current_img = mouth_open_img if current_img == mouth_closed_img else mouth_closed_img
        screen.fill((255, 255, 255))
        screen.blit(current_img, (50, 50))
        pygame.display.update()
        time.sleep(0.25)  # Adjust speed here
        clock.tick(60)

    # When done talking, show mouth closed
    screen.fill((255, 255, 255))
    screen.blit(mouth_closed_img, (50, 50))
    pygame.display.update()

# Function to speak and animate
def speak(text):
    global talking
    talking = True
    animation_thread = threading.Thread(target=animate_mouth)
    animation_thread.start()
    engine.say(text)
    engine.runAndWait()
    talking = False
    animation_thread.join()

# Main loop
running = True
while running:
    screen.fill((255, 255, 255))
    screen.blit(mouth_closed_img, (50, 50))
    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:  # Press SPACE to speak
                threading.Thread(target=speak, args=("Hello, I'm speaking to you right now!",)).start()

pygame.quit()
