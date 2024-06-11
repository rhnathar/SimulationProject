import pygame
import time
import configs.variables as var
from object.vehicles import Vehicle 
from object.button import Button

# Initialize Pygame
pygame.init()



# Create game window
win = pygame.display.set_mode((var.WINDOW_WIDTH, var.WINDOW_HEIGHT))

# Create vehicles
vehicles = [Vehicle(var.ENTRY_LANE_X, var.LANE_Y)]

button = Button((0, 255, 0), 350, 250, 100, 50, 'Generate')

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
                vehicles.append(Vehicle(var.ENTRY_LANE_X, var.LANE_Y))

    win.fill((0, 0, 0))
    button.draw(win)
    pygame.draw.rect(win, (255, 255, 255), (var.CIRCUIT_X, var.CIRCUIT_Y, var.CIRCUIT_WIDTH, var.CIRCUIT_HEIGHT), 2)
    #entry lane
    pygame.draw.line(win, (255, 255, 255), (370, 0), (370, 100), 2)
    #exit lane
    pygame.draw.line(win, (255, 255, 255), (430, 0), (430, 100), 2)

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
        vehicle.move(win)
        vehicle.draw(win)

        # Remove vehicle if it reaches the exit lane
        if vehicle.x >= var.EXIT_LANE_X and vehicle.y == 0:
            vehicles.remove(vehicle)

    pygame.display.update()

pygame.quit()