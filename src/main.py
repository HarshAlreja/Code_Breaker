import pygame
import sys
import os

# Ensure correct path for imports
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

try:
    from config import *  # Import config.py
except ModuleNotFoundError as e:
    print(f"ERROR: Could not import config.py! ({e})")
    sys.exit(1) # Now this should work!
from game_state import GameState

from sound_manager import SoundManager
from levels.firewall_breach import FirewallBreach
from levels.encrypted_room import EncryptedRoom
from levels.ai_showdown import AIShowdown

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Code Breaker: Cyber Heist")
        
        self.clock = pygame.time.Clock()
        self.game_state = GameState()
        self.sound_manager = SoundManager()
        self.sound_manager.sounds['success'].set_volume(0.2)
        self.sound_manager.sounds['success'].play(loops=-1)  # Background ambiance
        
        self.levels = [FirewallBreach, EncryptedRoom, AIShowdown]
        self.current_level = None
        self.show_start_screen()
        
    def show_start_screen(self):
        self.screen.fill(BLACK)
        title_font = pygame.font.Font(None, 74)
        menu_font = pygame.font.Font(None, 36)
        
        title = title_font.render("Code Breaker: Cyber Heist", True, CYAN)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4))
        pulse_factor = (pygame.time.get_ticks() % PULSE_SPEED) / PULSE_SPEED
        title_rect.y += int(10 * pulse_factor)
        self.screen.blit(title, title_rect)
        
        difficulties = ['Easy', 'Medium', 'Hard']
        button_height = 50
        spacing = 20
        selected = difficulties.index(self.game_state.difficulty.title())
        
        for i, diff in enumerate(difficulties):
            button_rect = pygame.Rect(
                WINDOW_WIDTH // 4,
                WINDOW_HEIGHT // 2 + i * (button_height + spacing),
                WINDOW_WIDTH // 2,
                button_height
            )
            color = GREEN if i == selected else WHITE
            pygame.draw.rect(self.screen, color, button_rect, 2)
            
            text = menu_font.render(diff, True, color)
            text_rect = text.get_rect(center=button_rect.center)
            self.screen.blit(text, text_rect)
            
        start_text = menu_font.render("Press SPACE to Start", True, WHITE)
        start_rect = start_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT * 3 // 4))
        self.screen.blit(start_text, start_rect)
        
        pygame.display.flip()
        
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        waiting = False
                        self.init_level()
                    elif event.key == pygame.K_UP:
                        selected = (selected - 1) % len(difficulties)
                        self.game_state.difficulty = difficulties[selected].lower()
                        self.show_start_screen()
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(difficulties)
                        self.game_state.difficulty = difficulties[selected].lower()
                        self.show_start_screen()
                        
    def init_level(self):
        level_class = self.levels[self.game_state.current_level]
        self.current_level = level_class(self.game_state, self.sound_manager)
        self.sound_manager.play('portal')
        
    def show_game_over_screen(self):
        self.sound_manager.sounds['ambient'].stop()
        self.screen.fill(BLACK)
        
        title_font = pygame.font.Font(None, 64)
        if self.game_state.current_level == len(self.levels) - 1 and self.game_state.level_complete:
            text = title_font.render("Mission Complete!", True, GREEN)
            self.sound_manager.play('success')
        else:
            text = title_font.render("Mission Failed", True, RED)
            self.sound_manager.play('alert')
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3))
        self.screen.blit(text, text_rect)
        
        score_font = pygame.font.Font(None, 48)
        score_text = score_font.render(f"Score: {self.game_state.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.screen.blit(score_text, score_rect)
        
        inst_font = pygame.font.Font(None, 36)
        inst_text = inst_font.render("Press R to Restart or Q to Quit", True, WHITE)
        inst_rect = inst_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT * 2 // 3))
        self.screen.blit(inst_text, inst_rect)
        
        pygame.display.flip()
        
    def show_level_transition(self):
        self.screen.fill(BLACK)
        font = pygame.font.Font(None, 48)
        level_names = ["Firewall Breach", "Encrypted Room", "AI Showdown"]
        text = font.render(f"Level {self.game_state.current_level + 1}: {level_names[self.game_state.current_level]}", True, GREEN)
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        
        self.screen.blit(text, text_rect)
        self.sound_manager.play('hack')
        pygame.display.flip()
        pygame.time.wait(2000)  # Show transition for 2 seconds
        
    def run(self):
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN and (self.game_state.game_over or 
                    (self.game_state.current_level == len(self.levels) - 1 and self.game_state.level_complete)):
                    if event.key == pygame.K_r:
                        self.game_state = GameState()
                        self.sound_manager.sounds['ambient'].play(loops=-1)
                        self.show_start_screen()
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()
                        
            if self.game_state.game_over or (self.game_state.current_level == len(self.levels) - 1 and 
                self.game_state.level_complete):
                self.show_game_over_screen()
            else:
                # Update and draw current level
                self.current_level.update(events)
                self.current_level.draw(self.screen)
                
                # Handle level completion and transition
                if self.game_state.level_complete:
                    if self.game_state.current_level < len(self.levels) - 1:
                        self.show_level_transition()  # Show transition before incrementing
                        self.game_state.next_level()  # Move to next level
                        self.init_level()  # Initialize the new level
                    else:
                        # If on the last level and completed, show game over
                        self.game_state.level_complete = False  # Reset to avoid loop

            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()