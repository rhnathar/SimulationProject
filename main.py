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

class Button:
    def __init__(self, color, x, y, width, height, text=''):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))
        if self.text != '':
            font = pygame.font.SysFont('arial', 20)
            text = font.render(self.text, 1, (0, 0, 0))
            win.blit(text, (self.x + (self.width / 2 - text.get_width() / 2), self.y + (self.height / 2 - text.get_height() / 2)))

    def isOver(self, pos):
        if self.x < pos[0] < self.x + self.width:
            if self.y < pos[1] < self.y + self.height:
                return True
        return False
    
class Portal:
    def __init__(self, x, y, color="red"):
        self.x = x
        self.y = y
        self.color = color
        self.vehicles_detected_time = {}

    def draw(self, win):
        pygame.draw.circle(win, self.color, (self.x, self.y), 4)

    def update(self, vehicle):
        for vehicle in vehicles:
            if vehicle.x <= self.x + 10 and vehicle.y <= self.y:
                if vehicle not in self.vehicles_detected_time:
                    self.vehicles_detected_time[vehicle] = time.time()
                elif time.time() - self.vehicles_detected_time[vehicle] >= 3:
                    self.color = "green"
            else:
                if vehicle in self.vehicles_detected_time:
                    del self.vehicles_detected_time[vehicle]
                if not self.vehicles_detected_time:
                    self.color = "red"
            if vehicle.x < self.x - 15:
                self.color = "red"
class Vehicle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = VEHICLE_SPEED
        self.speed_portal = 0
        self.desired_speed = VEHICLE_SPEED
        self.in_status = False

    def draw(self, win):
        pygame.draw.rect(win, (0, 0, 255), (self.x, self.y, VEHICLE_SIZE, VEHICLE_SIZE))

    def move(self, portal):
        if self.x == ENTRY_LANE_X and self.y < CIRCUIT_Y:
            self.y += self.speed
        elif self.y >= CIRCUIT_Y and self.x > CIRCUIT_X and self.x < EXIT_LANE_X and self.y < CIRCUIT_Y + CIRCUIT_HEIGHT - VEHICLE_SIZE:
            if self.in_status == False and self.x >= portal.x:
                distance = self.x - portal.x
                self.speed_portal = distance/70 * self.desired_speed
                self.x -= min(self.speed_portal, self.speed)
            if portal.color == 'green' and self.x <= portal.x + 5:
                self.in_status = True
            if self.in_status:
                distance = self.x - CIRCUIT_X
                self.speed_portal = (1 - distance/105) * self.desired_speed
                self.x -= min(self.speed, self.speed_portal)
        elif self.x <= CIRCUIT_X and self.y >= CIRCUIT_Y and self.y < CIRCUIT_Y + CIRCUIT_HEIGHT - VEHICLE_SIZE:
            self.y += self.speed
        elif self.y >= CIRCUIT_Y + CIRCUIT_HEIGHT - VEHICLE_SIZE and self.x < CIRCUIT_X + CIRCUIT_WIDTH - VEHICLE_SIZE:
            self.x += self.speed
        elif self.x >= CIRCUIT_X + CIRCUIT_WIDTH - VEHICLE_SIZE and self.y >= CIRCUIT_Y:
            self.y -= self.speed
        elif self.y <= CIRCUIT_Y and self.x >= EXIT_LANE_X:
            self.x -= self.speed
        elif self.x <= EXIT_LANE_X + VEHICLE_SIZE and self.y <= CIRCUIT_Y:
           self.y -= self.speed
    def calculate_acceleration(self, front_vehicle, s):
        # IDM parameters
        v0 = 2  # Desired speed in pixels per frame
        a = 0.3  # Comfortable acceleration in pixels per frame per frame   
        b = 0.2  # Comfortable deceleration in pixels per frame per frame
        T = 1.5  # Headway time in seconds
        s0 = 7  # Minimum safe distance in pixels
        delta = 4

        # Convert time headway to frames
        fps = 60
        T_d = T * fps
        s_star = s0 + self.speed * T_d + (self.speed * front_vehicle.speed) / (2 * (a * b)**0.5)
        acceleration = a * (1 - (self.speed / v0)**delta - (s_star / s)**2)
        return acceleration
# Create vehicles
vehicles = [Vehicle(ENTRY_LANE_X, LANE_Y)]

# Create button
button = Button((0, 255, 0), 350, 250, 100, 50, 'Generate')

# create portal
portal = Portal(300, 105)

# Game loop
clock = pygame.time.Clock()

# Game loop
run = True
last_spawn_time = time.time()
while run:
    # This will delay the game so it runs at 60 frames per second
    clock.tick(60)

    for event in pygame.event.get():
        pos = pygame.mouse.get_pos()
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if button.isOver(pos):
                vehicles.append(Vehicle(ENTRY_LANE_X, LANE_Y))

    
    win.fill((0, 0, 0))
    button.draw(win)
    pygame.draw.rect(win, (255, 255, 255), (CIRCUIT_X, CIRCUIT_Y, CIRCUIT_WIDTH, CIRCUIT_HEIGHT), 2)
    #entry lane
    pygame.draw.line(win, (255, 255, 255), (370, 0), (370, 100), 2)
    #exit lane
    pygame.draw.line(win, (255, 255, 255), (430, 0), (430, 100), 2)
    # Spawn new vehicle every 2 seconds

    for i in range(len(vehicles)):
        vehicle = vehicles[i]

        # If there is a previous vehicle, adjust speed based on distance
        if i > 0:
            prev_vehicle = vehicles[i-1]
            distance = ((vehicle.x - prev_vehicle.x)**2 + (vehicle.y - prev_vehicle.y)**2)**0.5
            if(distance == 0):
                vehicle.speed = 0
            else:
                a_i = vehicle.calculate_acceleration(vehicles[i-1], distance)
                # Adjust speed based on acceleration
                vehicle.speed = max(0, vehicle.speed + a_i)

    for vehicle in vehicles:
        vehicle.move(portal)
        vehicle.draw(win)
        portal.update(vehicle)

        # Remove vehicle if it reaches the exit lane
        if vehicle.x >= EXIT_LANE_X and vehicle.y == 0:
            vehicles.remove(vehicle)
    portal.draw(win)
    pygame.display.update()

pygame.quit()