import pygame
import random

# -----------------------------
# Configuration
# -----------------------------
SCREEN_W, SCREEN_H = 1200, 760
FPS = 60

NUM_OPERATORS = 22
CALL_LENGTH_START = 80

CALL_PER_HOUR_START = 1200
call_per_hour = CALL_PER_HOUR_START
call_interval = 3600 / call_per_hour

STEP = 1
STEP_CALLS = 10

FONT_SIZE = 22

QUEUE_PERSON_SIZE = 14
QUEUE_MAX_PER_ROW = 60

SIM_RATE_START = 125
SIM_RATE_MIN = 1

RAINBOW_COLORS = [
    (255, 0, 0),
    (255, 127, 0),
    (255, 255, 0),
    (0, 200, 0),
    (0, 150, 255),
    (75, 0, 130),
    (148, 0, 211),
    (255, 20, 147),
]

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

time_since_last_call = 0
sim_time = 0
running_sim = False

sim_rate = SIM_RATE_START

start_button = pygame.Rect(520, 330, 160, 60)

# -----------------------------
# Helper Functions
# -----------------------------
def draw_text(text, x, y, color=(255, 255, 255)):
    screen.blit(font.render(text, True, color), (x, y))


def format_time(seconds):
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m}:{s:02d}"


def estimated_wait_time():
    if NUM_OPERATORS == 0:
        return 0
    return (len(call_queue) / NUM_OPERATORS) * avg_call_length


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
                call_per_hour += STEP_CALLS
                call_interval = 3600 / call_per_hour

            elif event.key == pygame.K_LEFT:
                call_per_hour = max(1, call_per_hour - STEP_CALLS)
                call_interval = 3600 / call_per_hour

            elif event.key == pygame.K_w:
                sim_rate += 25

            elif event.key == pygame.K_s:
                sim_rate = max(SIM_RATE_MIN, sim_rate - 25)

        elif event.type == pygame.MOUSEBUTTONDOWN and not running_sim:
            if start_button.collidepoint(event.pos):
                running_sim = True
                sim_time = 0
                time_since_last_call = 0
                call_queue.clear()

                for operator in operators:
                    operator.busy = False
                    operator.time_remaining = 0

    # -------------------------
    # Simulation Logic
    # -------------------------
    if running_sim:

        sim_time += sim_dt
        time_since_last_call += sim_dt

        # Generate calls
        max_loops = 10
        loops = 0

        while time_since_last_call >= call_interval and loops < max_loops:
            time_since_last_call -= call_interval
            loops += 1

            call_queue.append({
                "duration": random.uniform(avg_call_length * 0.8, avg_call_length * 1.2),
                "enqueue_time": sim_time,
                "color": random.choice(RAINBOW_COLORS)
            })

        # Assign calls
        for operator in operators:
            if not operator.busy and call_queue:
                call = call_queue.pop(0)
                operator.assign_call(call["duration"])

        # Update operators
        for operator in operators:
            operator.update(sim_dt)

    # -------------------------
    # Drawing
    # -------------------------
    screen.fill((25, 25, 25))

    draw_text("911 CALL CENTER SIMULATION", 20, 20)
    draw_text(f"Simulation Time: {format_time(sim_time)}", 20, 60)
    draw_text(f"Simulation Rate: {sim_rate}x (W / S)", 20, 85)

    draw_text(f"Avg Call Length: {format_time(avg_call_length)} (↑ / ↓)", 20, 110)
    draw_text(f"Call Interval: {call_interval:.2f}s", 20, 135)
    draw_text(f"Calls Per Hour: {call_per_hour:.0f} (← / →)", 20, 160)

    draw_text(f"Calls Waiting: {len(call_queue)}", 20, 185)
    draw_text(f"Estimated Wait Time: {format_time(estimated_wait_time())}", 20, 210)

    if not running_sim:
        pygame.draw.rect(screen, (50, 180, 50), start_button)
        draw_text("START", start_button.x + 45, start_button.y + 18)

    # Queue visualization
    base_x, base_y = 20, 270
    for i, call in enumerate(call_queue):
        row = i // QUEUE_MAX_PER_ROW
        col = i % QUEUE_MAX_PER_ROW

        x = base_x + col * (QUEUE_PERSON_SIZE + 2)
        y = base_y + row * (QUEUE_PERSON_SIZE + 6)

        pygame.draw.rect(screen, call["color"], (x, y, QUEUE_PERSON_SIZE, QUEUE_PERSON_SIZE))

    draw_text("Incoming Call Queue", base_x, base_y - 25)

    # Operators
    for i, operator in enumerate(operators):
        x = 20 + (i % 10) * 100
        y = 470 + (i // 10) * 100

        color = (200, 50, 50) if operator.busy else (50, 200, 50)
        pygame.draw.rect(screen, color, (x, y, 80, 45))
        draw_text(f"O{i+1}", x + 20, y + 12)

    pygame.display.flip()

pygame.quit()