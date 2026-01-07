import pygame
import random

# -----------------------------
# Configuration
# -----------------------------
SCREEN_W, SCREEN_H = 1200, 720
FPS = 60

NUM_OPERATORS = 20
MIN_QUEUE_TIME = 3.0  # seconds (simulation time)

CALL_LENGTH_START = 7 * 60
CALL_INTERVAL_START = 45
STEP = 15

FONT_SIZE = 22

QUEUE_PERSON_SIZE = 14
QUEUE_MAX_PER_ROW = 60

SIM_RATE_START = 20
SIM_RATE_MIN = 1

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

    def update(self, sim_dt):
        if self.busy:
            self.time_remaining -= sim_dt
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
sim_time = 0
running_sim = False

sim_rate = SIM_RATE_START

start_button = pygame.Rect(520, 320, 160, 60)

# -----------------------------
# Helper Functions
# -----------------------------
def draw_text(text, x, y, color=(255, 255, 255)):
    screen.blit(font.render(text, True, color), (x, y))


def format_time(seconds):
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m}:{s:02d}"


# -----------------------------
# Main Loop
# -----------------------------
running = True
while running:
    wall_dt = clock.tick(FPS) / 1000
    sim_dt = wall_dt * sim_rate

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

            elif event.key == pygame.K_w:
                sim_rate += 1

            elif event.key == pygame.K_s:
                sim_rate = max(SIM_RATE_MIN, sim_rate - 1)

        elif event.type == pygame.MOUSEBUTTONDOWN and not running_sim:
            if start_button.collidepoint(event.pos):
                running_sim = True
                sim_time = 0
                time_since_last_call = 0

    # -------------------------
    # Simulation Logic
    # -------------------------
    if running_sim:
        sim_time += sim_dt
        time_since_last_call += sim_dt

        # Generate Calls
        if time_since_last_call >= call_interval:
            time_since_last_call = 0
            call_queue.append({
                "duration": random.uniform(avg_call_length * 0.8, avg_call_length * 1.2),
                "enqueue_time": sim_time
            })

        # Assign Calls (respect minimum queue time)
        for operator in operators:
            if not operator.busy:
                for call in call_queue:
                    if sim_time - call["enqueue_time"] >= MIN_QUEUE_TIME:
                        operator.assign_call(call["duration"])
                        call_queue.remove(call)
                        break

        # Update Operators
        for operator in operators:
            operator.update(sim_dt)

    # -------------------------
    # Drawing
    # -------------------------
    screen.fill((25, 25, 25))

    draw_text("911 CALL CENTER SIMULATION", 20, 20)
    draw_text(f"Simulation Time: {format_time(sim_time)}", 20, 60)
    draw_text(f"Simulation Rate: {sim_rate}x (W / S)", 20, 90)

    draw_text(f"Avg Call Length: {format_time(avg_call_length)} (↑ / ↓)", 20, 130)
    draw_text(f"Call Interval: {call_interval}s (← / →)", 20, 160)
    draw_text(f"Calls Waiting: {len(call_queue)}", 20, 190)

    # Start Button
    if not running_sim:
        pygame.draw.rect(screen, (50, 180, 50), start_button)
        draw_text("START", start_button.x + 45, start_button.y + 18)

    # -------------------------
    # Queue Visualization
    # -------------------------
    base_x, base_y = 20, 240
    for i, _ in enumerate(call_queue):
        row = i // QUEUE_MAX_PER_ROW
        col = i % QUEUE_MAX_PER_ROW
        x = base_x + col * (QUEUE_PERSON_SIZE + 2)
        y = base_y + row * (QUEUE_PERSON_SIZE + 6)

        pygame.draw.rect(
            screen,
            (200, 200, 50),
            (x, y, QUEUE_PERSON_SIZE, QUEUE_PERSON_SIZE)
        )

    draw_text("Incoming Call Queue", base_x, base_y - 25)

    # -------------------------
    # Operators
    # -------------------------
    for i, operator in enumerate(operators):
        x = 20 + (i % 10) * 100
        y = 420 + (i // 10) * 100
        color = (200, 50, 50) if operator.busy else (50, 200, 50)
        pygame.draw.rect(screen, color, (x, y, 80, 45))
        draw_text(f"O{i+1}", x + 20, y + 12)

    pygame.display.flip()

pygame.quit()
