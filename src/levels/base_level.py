from abc import ABC, abstractmethod
import pygame
from config import *
from ui_elements import Terminal  # Add this import

class BaseLevel(ABC):
    def __init__(self, game_state, sound_manager):
        self.game_state = game_state
        self.sound_manager = sound_manager
        self.terminal = Terminal(10, WINDOW_HEIGHT - 150, WINDOW_WIDTH - 20, 140)
        
    @abstractmethod
    def update(self, events):
        pass
        
    @abstractmethod
    def draw(self, screen):
        pass
        
    def draw_score(self, screen):
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.game_state.score} | Lives: {self.game_state.lives}", True, WHITE)
        screen.blit(score_text, (10, 50))