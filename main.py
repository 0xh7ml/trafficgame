import pygame
import random
import asyncio
import platform

# Initialize Pygame
pygame.init()
pygame.mixer.init()  # Initialize the mixer for audio

# Screen dimensions
WIDTH, HEIGHT = 1366, 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Smart Traffic Simulation || CSC 455 Project")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
LIGHT_BLUE = (135, 206, 250)
DARK_GRAY = (50, 50, 50)

# Road and intersection settings
ROAD_WIDTH = 200  # Two lanes
LANE_WIDTH = ROAD_WIDTH // 2
INTERSECTION_X = WIDTH // 2
INTERSECTION_Y = HEIGHT // 2

# Load background image from assets folder
try:
    background_image = pygame.image.load('assets/road_background.png')
    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
except:
    background_image = None

# Load vehicle images from assets folder
vehicle_images = {}
vehicle_sizes = {
    "car": {"width": 90, "height": 90, "speed": 2},
    "bus": {"width": 161.5, "height": 101, "speed": 1.8},
    "bike": {"width": 45, "height": 45, "speed": 2.5},
    "cng": {"width": 90, "height": 90, "speed": 2.4}
}
for v_type in vehicle_sizes:
    try:
        img = pygame.image.load(f'assets/{v_type}.png')
        img = pygame.transform.scale(img, (vehicle_sizes[v_type]["width"], vehicle_sizes[v_type]["height"]))
        vehicle_images[v_type] = img
    except:
        vehicle_images[v_type] = None

# Traffic light settings
LIGHT_DIAMETER = 15
LIGHT_RADIUS = LIGHT_DIAMETER // 2  # 7.5 radius
BAR_WIDTH = 20
BAR_HEIGHT = 60  # 3 lights (15px each) + spacing
LIGHT_POS = [
    (INTERSECTION_X - BAR_WIDTH // 2, INTERSECTION_Y - 120),  # Top (vertical bar)
    (INTERSECTION_X - BAR_WIDTH // 2, INTERSECTION_Y + 60),   # Bottom (vertical bar)
    (INTERSECTION_X + 60, INTERSECTION_Y - BAR_HEIGHT // 2),  # Right (horizontal bar)
    (INTERSECTION_X - 120, INTERSECTION_Y - BAR_HEIGHT // 2)  # Left (horizontal bar)
]
LIGHT_STATE = ["red", "red", "green", "green"]  # Top, Bottom, Right, Left
LIGHT_TIMER = [30 * 60, 30 * 60, 30 * 60, 30 * 60]  # 30 seconds at 60 FPS
LIGHT_DURATION = 30 * 60

# Congestion and score
congestion_level = 0
score = 0
score_text = "Excellent"

# Day/Night mode
day_mode = True
night_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
night_overlay.fill((0, 0, 0, 128))  # 50% opacity black

# Fonts
font = pygame.font.SysFont("Arial", 24)

# Vehicle class
class Vehicle:
    # Initialize the vehicle with its position, direction, lane, type, and color
    def __init__(self, x, y, direction, lane, vehicle_type, color):
        self.vehicle_type = vehicle_type
        self.rect = pygame.Rect(x, y, vehicle_sizes[vehicle_type]["width"], vehicle_sizes[vehicle_type]["height"])
        self.direction = direction
        self.lane = lane
        self.color = color
        self.speed = vehicle_sizes[vehicle_type]["speed"]
        self.image = vehicle_images[vehicle_type]
        if self.image:
            if direction == "up":
                self.image = pygame.transform.rotate(self.image, 90)
            elif direction == "down":
                self.image = pygame.transform.rotate(self.image, -90)
            elif direction == "left":
                self.image = pygame.transform.rotate(self.image, 180)

    # Method to move the vehicle based on its direction and traffic light state
    def move(self):
        if self.direction == "up" and LIGHT_STATE[0] == "green":
            self.rect.y -= self.speed
        elif self.direction == "down" and LIGHT_STATE[1] == "green":
            self.rect.y += self.speed
        elif self.direction == "right" and LIGHT_STATE[2] == "green":
            self.rect.x += self.speed
        elif self.direction == "left" and LIGHT_STATE[3] == "green":
            self.rect.x -= self.speed

    # Method to draw the vehicle on the screen
    # If the image is not available, draw a rectangle with the vehicle type label
    def draw(self, screen):
        if self.image:
            screen.blit(self.image, self.rect.topleft)
        else:
            pygame.draw.rect(screen, self.color, self.rect)
            label = font.render(self.vehicle_type[0].upper(), True, WHITE)
            screen.blit(label, (self.rect.x + 5, self.rect.y + 5))

# Vehicles list
vehicles = []

# Menu settings
menu = True
menu_options = ["Start Simulation", "Instructions", "Exit"]
selected_option = 0
music_playing = False

def draw_menu():
    if background_image:
        screen.blit(background_image, (0, 0))
    else:
        screen.fill(LIGHT_BLUE)
    if not day_mode:
        screen.blit(night_overlay, (0, 0))
    for i, option in enumerate(menu_options):
        color = YELLOW if i == selected_option else WHITE
        text = font.render(option, True, color)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 + i * 50))

def draw_traffic_lights():
    for i, (bar_x, bar_y) in enumerate(LIGHT_POS):
        is_vertical = i in [0, 1]
        bar_width = BAR_WIDTH if is_vertical else BAR_HEIGHT
        bar_height = BAR_HEIGHT if is_vertical else BAR_WIDTH
        pygame.draw.rect(screen, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))
        colors = [RED, YELLOW, GREEN]
        active_color = RED if LIGHT_STATE[i] == "red" else GREEN if LIGHT_STATE[i] == "green" else YELLOW
        for j in range(3):
            if is_vertical:
                light_x = bar_x + BAR_WIDTH // 2
                light_y = bar_y + 10 + j * 20
            else:
                light_x = bar_x + 10 + j * 20
                light_y = bar_y + BAR_WIDTH // 2
            color = active_color if (j == 0 and LIGHT_STATE[i] == "red") or (j == 1 and LIGHT_STATE[i] == "yellow") or (j == 2 and LIGHT_STATE[i] == "green") else BLACK
            pygame.draw.circle(screen, color, (light_x, light_y), LIGHT_RADIUS)
            if color != BLACK:
                timer_text = font.render(str(LIGHT_TIMER[i] // 60), True, WHITE)
                timer_x = light_x + 15 if is_vertical else light_x
                timer_y = light_y if is_vertical else light_y + 15
                screen.blit(timer_text, (timer_x, timer_y))

def draw_hud():
    score_display = font.render(f"Score: {score_text}", True, WHITE)
    congestion_display = font.render(f"Congestion: {congestion_level}", True, WHITE)
    mode_display = font.render("Day" if day_mode else "Night", True, WHITE)
    screen.blit(score_display, (10, 10))
    screen.blit(congestion_display, (10, 40))
    screen.blit(mode_display, (10, 70))

def spawn_vehicle():
    if random.random() < 0.05:
        direction = random.choice(["up", "down", "left", "right"])
        # Updated to include "cng" in vehicle type selection
        vehicle_type = random.choice(["car", "bus", "bike", "cng"])
        color = random.choice([RED, BLUE, GREEN, YELLOW])
        if direction == "up":
            lane = 1  # Down lane (right side of vertical road)
            x = INTERSECTION_X - ROAD_WIDTH // 2 + lane * LANE_WIDTH + (LANE_WIDTH - vehicle_sizes[vehicle_type]["width"]) // 2
            y = HEIGHT
        elif direction == "down":
            lane = 0  # Upper lane (left side of vertical road)
            x = INTERSECTION_X - ROAD_WIDTH // 2 + lane * LANE_WIDTH + (LANE_WIDTH - vehicle_sizes[vehicle_type]["width"]) // 2
            y = -vehicle_sizes[vehicle_type]["height"]
        elif direction == "left":
            lane = 0  # Upper lane (top side of horizontal road)
            x = WIDTH
            y = INTERSECTION_Y - ROAD_WIDTH // 2 + lane * LANE_WIDTH + (LANE_WIDTH - vehicle_sizes[vehicle_type]["height"]) // 2
        elif direction == "right":
            lane = 1  # Down lane (bottom side of horizontal road)
            x = -vehicle_sizes[vehicle_type]["width"]
            y = INTERSECTION_Y - ROAD_WIDTH // 2 + lane * LANE_WIDTH + (LANE_WIDTH - vehicle_sizes[vehicle_type]["height"]) // 2
        vehicles.append(Vehicle(x, y, direction, lane, vehicle_type, color))

def update_congestion():
    global congestion_level, score, score_text
    congestion_level = len([v for v in vehicles if abs(v.rect.x - INTERSECTION_X) < ROAD_WIDTH or abs(v.rect.y - INTERSECTION_Y) < ROAD_WIDTH])
    if congestion_level > 10:
        score_text = "Needs Improvement"
        score = max(0, score - 1)
    elif congestion_level > 5:
        score_text = "Moderate"
        score += 1
    else:
        score_text = "Excellent"
        score += 2

def setup():
    global vehicles, congestion_level, score, score_text, day_mode
    vehicles = []
    congestion_level = 0
    score = 0
    score_text = "Excellent"
    day_mode = True

async def update_loop():
    global menu, selected_option, day_mode, LIGHT_STATE, LIGHT_TIMER, music_playing
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.stop()
                pygame.quit()
                return
            if menu:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_option = (selected_option - 1) % len(menu_options)
                    elif event.key == pygame.K_DOWN:
                        selected_option = (selected_option + 1) % len(menu_options)
                    elif event.key == pygame.K_RETURN:
                        if selected_option == 0:
                            menu = False
                            if not music_playing:
                                try:
                                    pygame.mixer.music.load('audio/road-noise.mp3')
                                    pygame.mixer.music.set_volume(0.5)
                                    pygame.mixer.music.play(-1)  # Play in loop
                                    music_playing = True
                                except:
                                    print("Audio file 'road-noise.mp3' not found in audio folder.")
                        elif selected_option == 1:
                            print("Instructions: Use G to turn lights green, D to toggle day/night, manage traffic to keep congestion low.")
                        elif selected_option == 2:
                            pygame.mixer.music.stop()
                            pygame.quit()
                            return
            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_g:
                        for i in range(4):
                            LIGHT_STATE[i] = "green" if LIGHT_STATE[i] == "red" else "red"
                            LIGHT_TIMER[i] = LIGHT_DURATION
                    elif event.key == pygame.K_d:
                        day_mode = not day_mode

        if not menu:
            # Update traffic lights
            for i in range(4):
                LIGHT_TIMER[i] -= 1
                if LIGHT_TIMER[i] <= 0:
                    LIGHT_STATE[i] = "green" if LIGHT_STATE[i] == "red" else "red"
                    LIGHT_TIMER[i] = LIGHT_DURATION

            # Spawn vehicles
            spawn_vehicle()

            # Move vehicles and check for collision
            for vehicle in vehicles[:]:
                vehicle.move()
                if (vehicle.rect.x < -vehicle_sizes[vehicle.vehicle_type]["width"] or
                    vehicle.rect.x > WIDTH or
                    vehicle.rect.y < -vehicle_sizes[vehicle.vehicle_type]["height"] or
                    vehicle.rect.y > HEIGHT):
                    vehicles.remove(vehicle)
                else:
                    for other in vehicles:
                        if vehicle != other and vehicle.rect.colliderect(other.rect) and vehicle.lane == other.lane:
                            vehicles.remove(vehicle)
                            break

            # Draw everything
            if background_image:
                screen.blit(background_image, (0, 0))
            else:
                screen.fill(LIGHT_BLUE)
            draw_traffic_lights()
            for vehicle in vehicles:
                vehicle.draw(screen)
            draw_hud()
            if not day_mode:
                screen.blit(night_overlay, (0, 0))
        else:
            draw_menu()

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(1.0 / 60)

if platform.system() == "Emscripten":
    asyncio.ensure_future(update_loop())
else:
    if __name__ == "__main__":
        asyncio.run(update_loop())