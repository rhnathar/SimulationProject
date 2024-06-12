import pygame
import time

# Initialize Pygame
pygame.init()
pygame.font.init()

# Set up some constants
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
VEHICLE_SIZE = 5
VEHICLE_SPEED = 2

# Define the lanes
ENTRY_LANE1_X = 370
EXIT_LANE1_X = 430
ENTRY_LANE2_X = 360
EXIT_LANE2_X = 440
LANE_Y = 0

# parking entrance
PARKING_ENTRY1_X = 360
PARKING_ENTRY2_X = 370

# parking exit
PARKING_EXIT1_X = 440
PARKING_EXIT2_X = 430

PARKING_Y = 400
# Create game window
win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

# create font
font = pygame.font.Font(None, 15)

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
        self.on = True

    def draw(self, win):
        pygame.draw.circle(win, self.color, (self.x, self.y), 4)

    def update(self, vehicle, vehicles_lane):
        for vehicle in vehicles_lane:
            distance = vehicle.x - self.x
            if distance <=  10 and distance >=-10 and vehicle.y <= self.y:
                if vehicle not in self.vehicles_detected_time:
                    self.vehicles_detected_time[vehicle] = time.time()
                elif time.time() - self.vehicles_detected_time[vehicle] >= 3:
                    self.color = "green"
            else:
                if vehicle in self.vehicles_detected_time:
                    del self.vehicles_detected_time[vehicle]
                if not self.vehicles_detected_time:
                    self.color = "red"
            if distance < -10 and distance >= -11 and vehicle.y <= self.y:
                self.color = "red"
    
    def count_queueing_vehicles(self, vehicles_lane):
        count = 0
        for vehicle in vehicles_lane:
            distance = ((vehicle.x - self.x)**2 + (vehicle.y - self.y)**2)**0.5
            if not vehicle.in_status and not vehicle.exit_status and distance < 200:
                count += 1
        return count

class Vehicle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = VEHICLE_SPEED
        self.speed_portal = 0
        self.desired_speed = VEHICLE_SPEED
        self.in_status = False
        self.exit_status = False
        self.parked = False

    def draw(self, win):
        pygame.draw.rect(win, (0, 0, 255), (self.x, self.y, VEHICLE_SIZE, VEHICLE_SIZE))

    def move(self, enter_portal, exit_portal, CIRCUIT_WIDTH, CIRCUIT_HEIGHT, ENTRY_LANE_X, EXIT_LANE_X, PARKING_ENTRY_X, PARKING_EXIT_X, PARKING_Y):
        CIRCUIT_Y = (WINDOW_HEIGHT - CIRCUIT_HEIGHT) // 2
        CIRCUIT_X = (WINDOW_WIDTH - CIRCUIT_WIDTH) // 2
        # down from entry lane
        if self.x == ENTRY_LANE_X and self.y < CIRCUIT_Y:
            self.y += self.speed
        # left
        elif self.y >= CIRCUIT_Y and self.x > CIRCUIT_X and self.x <= ENTRY_LANE_X and self.y < CIRCUIT_Y + CIRCUIT_HEIGHT//2:
            if enter_portal.on:
                if self.in_status == False and self.x >= enter_portal.x:
                    distance = self.x - enter_portal.x
                    self.speed_portal = distance/ (ENTRY_LANE_X - enter_portal.x)  * self.desired_speed
                    self.x -= min(self.speed_portal, self.speed)
                if enter_portal.color == 'green' and self.x <= enter_portal.x + 3:
                    self.in_status = True
                if self.in_status:
                    distance = self.x - CIRCUIT_X
                    self.speed_portal = (1 - distance / (enter_portal.x - CIRCUIT_X + 5)) * self.desired_speed
                    self.x -= min(self.speed, self.speed_portal)
            else:
                self.x -= self.speed
        # down
        elif self.x <= CIRCUIT_X and self.y >= CIRCUIT_Y and self.y < CIRCUIT_Y + CIRCUIT_HEIGHT - VEHICLE_SIZE:
            self.y += self.speed
        # right
        elif self.x < PARKING_ENTRY_X and self.y >= CIRCUIT_Y + CIRCUIT_HEIGHT - VEHICLE_SIZE:
            self.x += self.speed
        elif self.x >= PARKING_ENTRY_X:
            if self.x < PARKING_EXIT_X:
                if self.y >= PARKING_Y - 2*VEHICLE_SIZE:
                    self.y -= self.speed
                if self.y <= PARKING_Y - 2*VEHICLE_SIZE:
                    self.parked = True
                    self.speed = 1
                    self.x += self.speed
            else:
                self.speed = 0
        # elif self.x >= PARKING_ENTRY_X and self.y >= CIRCUIT_Y:
        #     self.y -= self.speed
        # elif self.y <= CIRCUIT_Y and self.x >= EXIT_LANE_X:
        #     if exit_portal.on:
        #         if self.in_status and self.x >= exit_portal.x:
        #             distance = self.x - exit_portal.x
        #             self.speed_portal = distance / (CIRCUIT_X + CIRCUIT_WIDTH - exit_portal.x) * self.desired_speed
        #             self.x -= min(self.speed_portal, self.speed)
        #         if exit_portal.color == 'green' and self.x <= exit_portal.x + 5:
        #             self.in_status = False
        #             self.exit_status = True
        #         if self.in_status == False and self.exit_status == True:
        #             distance = self.x - EXIT_LANE_X
        #             self.speed_portal = (1 - distance/(exit_portal.x - EXIT_LANE_X + 5)) * self.desired_speed
        #             self.x -= min(self.speed, self.speed_portal)
        # elif self.x <= EXIT_LANE_X + VEHICLE_SIZE and self.y <= CIRCUIT_Y:
        #    self.y -= self.speed
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
vehicles_lane1 = [Vehicle(ENTRY_LANE1_X, LANE_Y)]
vehicles_lane2 = [Vehicle(ENTRY_LANE2_X, LANE_Y)]
lane = 1
# Create button
generate_button = Button((0, 255, 0), 350, 250, 100, 50, 'Generate')
unpark_button = Button((0, 255, 0), 350, 150, 100, 50, 'Unpark')
# create portal
enter_portal_1 = Portal(300, 105)
enter_portal_2 = Portal(300, 95)
exit_portal_1 = Portal(500, 105)
exit_portal_2 = Portal(500, 95)

# Game loop
clock = pygame.time.Clock()
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
            if generate_button.isOver(pos):
                # Determine which lane has fewer queueing vehicles
                queueing_vehicles_lane1 = enter_portal_1.count_queueing_vehicles(vehicles_lane1)
                queueing_vehicles_lane2 = enter_portal_2.count_queueing_vehicles(vehicles_lane2)

                if queueing_vehicles_lane1 <= queueing_vehicles_lane2:
                    vehicles_lane1.append(Vehicle(ENTRY_LANE1_X, LANE_Y))
                else:
                    vehicles_lane2.append(Vehicle(ENTRY_LANE2_X, LANE_Y))

    
    win.fill((0, 0, 0))
    generate_button.draw(win)
    unpark_button.draw(win)
    
    #entry lane 1
    pygame.draw.line(win, (255, 255, 255), (370, 0), (370, 100), 2)
    #entry lane 2
    pygame.draw.line(win, (255, 255, 255), (360, 0), (360, 90), 2)
    
    #top left 2
    pygame.draw.line(win, (255, 255, 255), (190, 90), (360, 90), 2)
    #top left 1
    pygame.draw.line(win, (255, 255, 255), (200, 100), (370, 100), 2)
    
    #left 1
    pygame.draw.line(win, (255, 255, 255), (200, 100), (200, 500), 2)
    #left 2
    pygame.draw.line(win, (255, 255, 255), (190, 90), (190, 510), 2)
    
    #bottom left 1
    pygame.draw.line(win, (255, 255, 255), (200, 500), (360, 500), 2)
    #bottom left 2
    pygame.draw.line(win, (255, 255, 255), (190, 510), (370, 510), 2)
    
    #parking entry 1
    pygame.draw.line(win, (255, 255, 255), (360, 400), (360, 500), 2)
    #parking entry 2
    pygame.draw.line(win, (255, 255, 255), (370, 400), (370, 510), 2)
    
    #parking exit 1
    pygame.draw.line(win, (255, 255, 255), (440, 400), (440, 500), 2)
    #parking exit 2
    pygame.draw.line(win, (255, 255, 255), (430, 400), (430, 510), 2)
    
    #bottom right 1
    pygame.draw.line(win, (255, 255, 255), (440, 500), (600, 500), 2)
    #bottom right 2
    pygame.draw.line(win, (255, 255, 255), (430, 510), (610, 510), 2)
    
    #right 1
    pygame.draw.line(win, (255, 255, 255), (600, 500), (600, 100), 2)
    #right 2
    pygame.draw.line(win, (255, 255, 255), (610, 510), (610, 90), 2)
    
    #top right 1
    pygame.draw.line(win, (255, 255, 255), (600, 100), (430, 100), 2)
    #top right 2
    pygame.draw.line(win, (255, 255, 255), (610, 90), (440, 90), 2)
    
    #exit lane 1
    pygame.draw.line(win, (255, 255, 255), (430, 0), (430, 100), 2)
    #exit lane 2
    pygame.draw.line(win, (255, 255, 255), (440, 0), (440, 90), 2)
    
    # lane 1
    #pygame.draw.rect(win, (255, 0, 0), (200, 100, 400, 400), 2)
    # Lane 2
    #pygame.draw.rect(win, (255, 255, 255), (190, 90, 420, 420), 2)

    # Spawn new vehicles
    for i in range(len(vehicles_lane1)):
        vehicle = vehicles_lane1[i]
        # If there is a previous vehicle, adjust speed based on distance
        if i > 0:
            prev_vehicle = vehicles_lane1[i-1]
            distance = ((vehicle.x - prev_vehicle.x)**2 + (vehicle.y - prev_vehicle.y)**2)**0.5
            if(distance == 0):
                vehicle.speed = 0
            else:
                a_i = vehicle.calculate_acceleration(vehicles_lane1[i-1], distance)
                # Adjust speed based on acceleration
                vehicle.speed = max(0, vehicle.speed + a_i)
    
    for i in range(len(vehicles_lane2)):
        vehicle = vehicles_lane2[i]
        # If there is a previous vehicle, adjust speed based on distance
        if i > 0:
            prev_vehicle = vehicles_lane2[i-1]
            distance = ((vehicle.x - prev_vehicle.x)**2 + (vehicle.y - prev_vehicle.y)**2)**0.5
            if(distance == 0):
                vehicle.speed = 0
            else:
                a_i = vehicle.calculate_acceleration(vehicles_lane2[i-1], distance)
                # Adjust speed based on acceleration
                vehicle.speed = max(0, vehicle.speed + a_i)

    for vehicle in vehicles_lane1:
        vehicle.move(enter_portal_1, exit_portal_1, 400, 400, ENTRY_LANE1_X, EXIT_LANE1_X, PARKING_ENTRY1_X, PARKING_EXIT1_X, PARKING_Y)
        enter_portal_1.update(vehicle, vehicles_lane1)
        exit_portal_1.update(vehicle, vehicles_lane1)
        vehicle.draw(win)
            
        # Remove vehicle if it reaches the exit lane
        if vehicle.x >= EXIT_LANE1_X and vehicle.y == 0:
            vehicles_lane1.remove(vehicle)
    
    for vehicle in vehicles_lane2:
        vehicle.move(enter_portal_2, exit_portal_2, 420, 420, ENTRY_LANE2_X, EXIT_LANE2_X, PARKING_ENTRY2_X, PARKING_EXIT2_X, PARKING_Y)
        enter_portal_2.update(vehicle, vehicles_lane2)
        exit_portal_2.update(vehicle, vehicles_lane2)
        vehicle.draw(win)
            
        # Remove vehicle if it reaches the exit lane
        if vehicle.x >= EXIT_LANE1_X and vehicle.y == 0:
            vehicles_lane2.remove(vehicle)

    # parking spot
    pygame.draw.rect(win, (255, 255, 255), (340, 340, 120, 60))

    queueing_vehicles_lane1 = enter_portal_1.count_queueing_vehicles(vehicles_lane1)
    queueing_vehicles_lane2 = enter_portal_2.count_queueing_vehicles(vehicles_lane2)
    
    text_queue_count1 = font.render('Queueing vehicles lane 1: ' + str(queueing_vehicles_lane1), True, (255, 255, 255))
    text_queue_count2 = font.render('Queueing vehicles lane 2: ' + str(queueing_vehicles_lane2), True, (255, 255, 255))
    win.blit(text_queue_count1, (50, 20))
    win.blit(text_queue_count2, (50, 40))

    count_parked = sum(vehicle.parked for vehicle in vehicles_lane1) + sum(vehicle.parked for vehicle in vehicles_lane2)
    text_parked = font.render('Parked vehicles: ' + str(count_parked), True, (0, 0, 0))
    win.blit(text_parked, (350, 350))

    exit_portal_1.draw(win)
    exit_portal_2.draw(win)
    enter_portal_1.draw(win)
    enter_portal_2.draw(win)
    pygame.display.update()

pygame.quit()