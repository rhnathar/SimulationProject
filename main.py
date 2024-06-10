import pygame
import time

# Initialize Pygame
pygame.init()

# Set up some constants
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
VEHICLE_SIZE = 5
VEHICLE_SPEED = 2
CIRCUIT_WIDTH, CIRCUIT_HEIGHT = 400, 400
CIRCUIT_X, CIRCUIT_Y = (WINDOW_WIDTH - CIRCUIT_WIDTH) // 2, (WINDOW_HEIGHT - CIRCUIT_HEIGHT) // 2

ENTRY_LANE_X = 370
EXIT_LANE_X = 430
LANE_Y = 0

# Create game window
win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

class Vehicle:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self, win):
        pygame.draw.rect(win, (255, 0, 0), (self.x, self.y, VEHICLE_SIZE, VEHICLE_SIZE))

    def move(self):
        if self.x == ENTRY_LANE_X and self.y < CIRCUIT_Y:
            self.y += VEHICLE_SPEED
        elif self.y == CIRCUIT_Y and self.x > CIRCUIT_X and self.x < EXIT_LANE_X:
            self.x -= VEHICLE_SPEED
        elif self.x == CIRCUIT_X and self.y >= CIRCUIT_Y and self.y < CIRCUIT_Y + CIRCUIT_HEIGHT - VEHICLE_SIZE:
            self.y += VEHICLE_SPEED
        elif self.y >= CIRCUIT_Y + CIRCUIT_HEIGHT - VEHICLE_SIZE and self.x >= CIRCUIT_X and self.x < CIRCUIT_X + CIRCUIT_WIDTH - VEHICLE_SIZE:
            self.x += VEHICLE_SPEED
        elif self.x >= CIRCUIT_X + CIRCUIT_WIDTH - VEHICLE_SIZE and self.y <= CIRCUIT_Y + CIRCUIT_HEIGHT + VEHICLE_SIZE and self.y > CIRCUIT_Y:
            self.y -= VEHICLE_SPEED
        elif self.y == CIRCUIT_Y and self.x > EXIT_LANE_X:
            self.x -= VEHICLE_SPEED
        elif self.x == EXIT_LANE_X and self.y <= CIRCUIT_Y:
           self.y -= VEHICLE_SPEED

# Create vehicles
vehicles = [Vehicle(ENTRY_LANE_X, LANE_Y)]

# Game loop
clock = pygame.time.Clock()

# Game loop
run = True
last_spawn_time = time.time()
while run:
    # This will delay the game so it runs at 60 frames per second
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    win.fill((0, 0, 0))
    pygame.draw.rect(win, (255, 255, 255), (CIRCUIT_X, CIRCUIT_Y, CIRCUIT_WIDTH, CIRCUIT_HEIGHT), 2)
    #entry lane
    pygame.draw.line(win, (255, 255, 255), (370, 0), (370, 100), 2)
    #exit lane
    pygame.draw.line(win, (255, 255, 255), (430, 0), (430, 100), 2)
    # Spawn new vehicle every 2 seconds
    if time.time() - last_spawn_time > 2:
        vehicles.append(Vehicle(ENTRY_LANE_X, LANE_Y))
        last_spawn_time = time.time()

    for vehicle in vehicles:
        vehicle.move()
        vehicle.draw(win)

        # Remove vehicle if it reaches the exit lane
        if vehicle.x >= EXIT_LANE_X and vehicle.y == 0:
            vehicles.remove(vehicle)

    pygame.display.update()

pygame.quit()