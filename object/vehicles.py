import pygame
import configs.variables as var


class Vehicle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = var.VEHICLE_SPEED

    def draw(self, win):
        pygame.draw.rect(win, (255, 0, 0), (self.x, self.y, var.VEHICLE_SIZE, var.VEHICLE_SIZE))

    def move(self,win):
        # Movement logic as defined in the original code
        if self.x == var.ENTRY_LANE_X and self.y < var.CIRCUIT_Y:
            self.y += self.speed
        elif self.y >= var.CIRCUIT_Y and self.x > var.CIRCUIT_X and self.x < var.EXIT_LANE_X and self.y < var.CIRCUIT_Y + var.CIRCUIT_HEIGHT - var.VEHICLE_SIZE:
            self.x -= self.speed
        elif self.x <= var.CIRCUIT_X and self.y >= var.CIRCUIT_Y and self.y < var.CIRCUIT_Y + var.CIRCUIT_HEIGHT - var.VEHICLE_SIZE:
            self.y += self.speed
        elif self.y >= var.CIRCUIT_Y + var.CIRCUIT_HEIGHT - var.VEHICLE_SIZE and self.x < var.CIRCUIT_X + var.CIRCUIT_WIDTH - var.VEHICLE_SIZE:
            self.x += self.speed
        elif self.x >= var.CIRCUIT_X + var.CIRCUIT_WIDTH - var.VEHICLE_SIZE and self.y >= var.CIRCUIT_Y:
            self.y -= self.speed
        elif self.y <= var.CIRCUIT_Y and self.x >= var.EXIT_LANE_X:
            self.x -= self.speed
        elif self.x <= var.EXIT_LANE_X + var.VEHICLE_SIZE and self.y <= var.CIRCUIT_Y:
           self.y -= self.speed
           
    def calculate_acceleration(self, front_vehicle, s):
        # IDM parameters
        v0 = 2  # Desired speed in pixels per frame
        a = 0.3  # Comfortable acceleration in pixels per frame per frame   
        b = 0.2  # Comfortable deceleration in pixels per frame per frame
        T = 1.5  # Headway time in seconds
        s0 = 5  # Minimum safe distance in pixels
        delta = 4

        # Convert time headway to frames
        fps = 60
        T_d = T * fps
        s_star = s0 + self.speed * T_d + (self.speed * front_vehicle.speed) / (2 * (a * b)**0.5)
        acceleration = a * (1 - (self.speed / v0)**delta - (s_star / s)**2)
        return acceleration

