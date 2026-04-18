import pygame
import sys
import math
from physics import create_basic, create_intermediate, create_formula_one

# Colors
BLACK = (20, 20, 20)
WHITE = (240, 240, 240)
GRAY = (100, 100, 100)
DARK_GRAY = (40, 40, 40)
RED = (220, 50, 50)
BLUE = (50, 150, 220)
GREEN = (50, 220, 50)
YELLOW = (220, 200, 50)
CYAN = (50, 220, 220)
ORANGE = (255, 165, 0)

class Simulator:
    def __init__(self):
        pygame.init()
        self.width = 1200
        self.height = 800
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Pull-Back Car Physics Simulation")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.SysFont("Segoe UI", 48, bold=True)
        self.font_medium = pygame.font.SysFont("Segoe UI", 28)
        self.font_small = pygame.font.SysFont("Segoe UI", 18)
        
        self.cars = [create_basic(), create_intermediate(), create_formula_one()]
        self.current_car_idx = 0
        self.car = self.cars[self.current_car_idx]
        
        self.paused = False
        self.camera_x = 0.0
        
    def switch_car(self):
        self.current_car_idx = (self.current_car_idx + 1) % len(self.cars)
        self.car = self.cars[self.current_car_idx]
        self.car.distance = 0.0
        self.car.velocity = 0.0
        self.car.stored_energy = 0.0
        self.camera_x = 0.0
        
    def draw_car_top_down(self, x, y, width, height, type_name):
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        # Draw base drop shadow
        pygame.draw.rect(surface, (0,0,0,100), (4, 4, width, height), border_radius=10)
        
        if type_name == "Basic Car": # Yellow
            # Boxy, flat front
            pygame.draw.rect(surface, YELLOW, (0, 0, width, height))
            # Windshield
            pygame.draw.rect(surface, DARK_GRAY, (width*0.6, 5, 20, height-10))
            # Roof
            pygame.draw.rect(surface, (180, 160, 40), (width*0.2, 5, width*0.4, height-10))
        elif type_name == "Intermediate Car": # White
            # Smooth teardrop
            pygame.draw.ellipse(surface, WHITE, (0, 0, width, height))
            # Windshield curve
            pygame.draw.ellipse(surface, DARK_GRAY, (width*0.4, height*0.1, width*0.3, height*0.8))
        elif type_name == "Formula One": # Red
            # Open wheel, narrow body
            # body
            pygame.draw.ellipse(surface, RED, (width*0.1, height*0.3, width*0.8, height*0.4))
            # front wing
            pygame.draw.rect(surface, BLACK, (width*0.8, height*0.1, 10, height*0.8))
            pygame.draw.rect(surface, (200, 30, 30), (width*0.8, height*0.4, width*0.2, height*0.2))
            # rear wing
            pygame.draw.rect(surface, BLACK, (5, height*0.1, 20, height*0.8))
            # tires
            pygame.draw.rect(surface, BLACK, (width*0.7, 0, 30, height*0.2), border_radius=5)
            pygame.draw.rect(surface, BLACK, (width*0.7, height*0.8, 30, height*0.2), border_radius=5)
            pygame.draw.rect(surface, BLACK, (20, 0, 35, height*0.2), border_radius=5)
            pygame.draw.rect(surface, BLACK, (20, height*0.8, 35, height*0.2), border_radius=5)
            
        self.screen.blit(surface, (x, y))

    def draw_dashboard(self):
        # Dashboard Background
        dash_rect = pygame.Rect(0, self.height - 250, self.width, 250)
        pygame.draw.rect(self.screen, DARK_GRAY, dash_rect)
        pygame.draw.line(self.screen, GRAY, (0, self.height - 250), (self.width, self.height - 250), 4)

        # 1. Stored Energy Bar (Left/Center)
        energy_x, energy_y = 50, self.height - 180
        energy_w, energy_h = 600, 60
        
        pygame.draw.rect(self.screen, BLACK, (energy_x, energy_y, energy_w, energy_h), border_radius=5)
        
        ratio = self.car.stored_energy / self.car.max_energy
        if ratio > 1.0: ratio = 1.0
        
        # Color based on wound up state
        if ratio < 0.33:
            bar_color = GREEN
        elif ratio < 0.66:
            bar_color = YELLOW
        else:
            bar_color = RED
            
        current_w = energy_w * ratio
        if current_w > 0:
            pygame.draw.rect(self.screen, bar_color, (energy_x, energy_y, current_w, energy_h), border_radius=5)
            
        energy_txt = self.font_medium.render(f"Stored Energy: {int(ratio*100)}%", True, WHITE)
        self.screen.blit(energy_txt, (energy_x, energy_y - 40))
        
        # 2. Speedometer
        speed_txt = self.font_large.render(f"{self.car.velocity:.1f} m/s", True, CYAN)
        self.screen.blit(speed_txt, (energy_x, energy_y + 80))


        
    def run(self):
        running = True
        
        while running:
            dt = min(self.clock.tick(60) / 1000.0, 0.1)
            
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.paused = not self.paused
                    elif event.key == pygame.K_c:
                        self.switch_car()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.paused:
                        self.paused = False
                    self.car.pulling_back = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.car.pulling_back = False
            
            # Physics Update
            if not self.paused:
                self.car.update(dt)
                self.camera_x += self.car.velocity * dt * 50 # scale velocity for visual scrolling
            
            # Rendering
            # Road background
            self.screen.fill((50, 50, 50))
            
            # Draw moving road lines
            line_spacing = 200
            offset = -(self.camera_x % line_spacing)
            for i in range(10):
                pygame.draw.rect(self.screen, WHITE, (offset + i * line_spacing, self.height//2 - 130, 100, 10))
            
            # Car Stats info on top
            car_info = self.font_medium.render(f"Vehicle: {self.car.name}", True, WHITE)
            self.screen.blit(car_info, (20, 20))
            distance_info = self.font_medium.render(f"Distance: {self.car.distance:.1f} m", True, YELLOW)
            self.screen.blit(distance_info, (20, 60))
            
            if self.paused:
                pause_info = self.font_large.render("PAUSED (Press P to Resume)", True, RED)
                self.screen.blit(pause_info, (self.width//2 - pause_info.get_width()//2, 100))
                
            controls_txt = self.font_small.render("Controls: HOLD MOUSE=Pull Back, RELEASE=Go, C=Change Car, P=Pause", True, GRAY)
            self.screen.blit(controls_txt, (self.width - controls_txt.get_width() - 20, 20))

            # Draw Car
            car_w, car_h = 240, 120
            # If pulling back, maybe add a visual shake or offset
            car_draw_x = 200
            if self.car.pulling_back:
                # small shake effect based on energy
                shake = (self.car.stored_energy / self.car.max_energy) * 5
                car_draw_x += math.sin(pygame.time.get_ticks() * 0.1) * shake
                
            self.draw_car_top_down(car_draw_x, self.height//2 - 180, car_w, car_h, self.car.name)

            # Draw Dashboard
            self.draw_dashboard()

            pygame.display.flip()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    sim = Simulator()
    sim.run()
