import pygame
import random
import time

# -----------------------------
# Configuration
# -----------------------------
SCREEN_W, SCREEN_H = 1000, 600
FPS = 60

NUM_OPERATORS = 20

CALL_LENGTH_START = 7 * 60        # 7 minutes
CALL_INTERVAL_START = 45          # 45 seconds
STEP = 15                         # adjustment step (seconds)

FONT_SIZE = 22

# -----------------------------
# Operator Class
# -----------------------------
class Operator:
    def __init__(self):
        self.busy = False
        self.time_remaining = 0

    def assign_call(self, duration):
        self.busy = True
        self.time_remaining = duration

    def update(self, dt):
        if self.busy:
            self.time_remaining -= dt
            if self.time_remaining <= 0:
                self.busy = False
                self.time_remaining = 0


# -----------------------------
# Pygame Setup
# -----------------------------
pygame.init()
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("911 Call Center Simulation")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, FONT_SIZE)

# -----------------------------
# Simulation State
# -----------------------------
operators = [Operator() for _ in range(NUM_OPERATORS)]
call_queue = []

avg_call_length = CALL_LENGTH_START
call_interval = CALL_INTERVAL_START

time_since_last_call = 0

# -----------------------------
# Helper Functions
# -----------------------------
def draw_text(text, x, y):
    surface = font.render(text, True, (255, 255, 255))
    screen.blit(surface, (x, y))


def format_time(seconds):
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m}:{s:02d}"


# -----------------------------
# Main Loop
# -----------------------------
running = True
while running:
    dt = clock.tick(FPS) / 1000  # seconds since last frame
    time_since_last_call += dt

    # -------------------------
    # Events
    # -------------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            elif event.key == pygame.K_UP:
                avg_call_length += STEP

            elif event.key == pygame.K_DOWN:
                avg_call_length = max(STEP, avg_call_length - STEP)

            elif event.key == pygame.K_RIGHT:
                call_interval += STEP

            elif event.key == pygame.K_LEFT:
                call_interval = max(STEP, call_interval - STEP)

    # -------------------------
    # Generate Calls
    # -------------------------
    if time_since_last_call >= call_interval:
        time_since_last_call = 0

        # Slight randomness around average
        duration = random.uniform(
            avg_call_length * 0.8,
            avg_call_length * 1.2
        )
        call_queue.append(duration)

    # -------------------------
    # Assign Calls
    # -------------------------
    for operator in operators:
        if not operator.busy and call_queue:
            call_duration = call_queue.pop(0)
            operator.assign_call(call_duration)

    # -------------------------
    # Update Operators
    # -------------------------
    for operator in operators:
        operator.update(dt)

    # -------------------------
    # Drawing
    # -------------------------
    screen.fill((30, 30, 30))

    busy_ops = sum(1 for o in operators if o.busy)
    free_ops = NUM_OPERATORS - busy_ops

    draw_text("911 CALL CENTER SIMULATION", 20, 20)
    draw_text(f"Operators: {NUM_OPERATORS}", 20, 60)
    draw_text(f"Busy: {busy_ops}", 20, 90)
    draw_text(f"Free: {free_ops}", 20, 120)
    draw_text(f"Calls Waiting in Queue: {len(call_queue)}", 20, 150)

    draw_text(
        f"Avg Call Length: {format_time(avg_call_length)}  (↑ / ↓)",
        20, 200
    )
    draw_text(
        f"Call Arrival Interval: {call_interval}s  (← / →)",
        20, 230
    )

    # Operator status visualization
    for i, operator in enumerate(operators):
        x = 20 + (i % 10) * 90
        y = 300 + (i // 10) * 80

        color = (200, 50, 50) if operator.busy else (50, 200, 50)
        pygame.draw.rect(screen, color, (x, y, 70, 40))

        label = f"O{i+1}"
        draw_text(label, x + 10, y + 10)

    pygame.display.flip()

pygame.quit()
