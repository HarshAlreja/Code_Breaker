import pygame
from config import *

class Terminal:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = []
        self.font = pygame.font.Font(None, 24)
        self.pulse_time = pygame.time.get_ticks()  # For pulsing effect
        
    def add_message(self, message):
        self.text.append(message)
        if len(self.text) > 10:  # Keep only last 10 messages
            self.text.pop(0)
            
    def draw(self, screen):
        pygame.draw.rect(screen, BLACK, self.rect)
        
        # Pulsing border effect
        current_time = pygame.time.get_ticks()
        if current_time - self.pulse_time > PULSE_SPEED:
            self.pulse_time = current_time
        pulse_factor = (current_time % PULSE_SPEED) / PULSE_SPEED
        color = (0, int(255 * pulse_factor), 0)  # Fade from black to green
        pygame.draw.rect(screen, color, self.rect, 3)
        
        y_offset = 15
        for message in self.text:
            text_surface = self.font.render(message, True, GREEN)
            screen.blit(text_surface, (self.rect.x + 15, self.rect.y + y_offset))
            y_offset += 30