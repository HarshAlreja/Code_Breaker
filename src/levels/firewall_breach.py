import pygame
import random
from levels.base_level import BaseLevel
from config import *

class FirewallBreach(BaseLevel):
    def __init__(self, game_state, sound_manager):
        super().__init__(game_state, sound_manager)
        self.pattern = []
        self.player_sequence = []
        self.generating_pattern = False
        self.display_time = 0
        self.current_pattern_index = 0
        self.buttons = self._create_buttons()
        self.show_instructions = True
        self.instruction_time = pygame.time.get_ticks()
        self.correct_attempts = 0  # Track correct pattern entries
        
    def _create_buttons(self):
        buttons = []
        colors = [RED, GREEN, BLUE, CYAN]
        button_size = 100
        start_x = (WINDOW_WIDTH - (2 * button_size + 20)) // 2
        start_y = (WINDOW_HEIGHT - (2 * button_size + 20)) // 2 - 50
        
        for i in range(4):
            x = start_x + (i % 2) * (button_size + 20)
            y = start_y + (i // 2) * (button_size + 20)
            buttons.append({
                'rect': pygame.Rect(x, y, button_size, button_size),
                'color': colors[i],
                'index': i
            })
        return buttons
        
    def generate_pattern(self):
        pattern_length = DIFFICULTY_LEVELS[self.game_state.difficulty]['pattern_length']
        self.pattern = [random.randint(0, 3) for _ in range(pattern_length)]
        self.display_time = pygame.time.get_ticks()
        self.current_pattern_index = 0
        self.terminal.add_message(f">> Pattern length: {pattern_length}. Watch carefully!")
        self.sound_manager.play('scan')
        
    def update(self, events):
        current_time = pygame.time.get_ticks()
        
        if self.show_instructions:
            if current_time - self.instruction_time > 7000:
                self.show_instructions = False
                self.terminal.add_message(">> Watch the boxes blink. Click them in order 3 times to win!")
                self.generating_pattern = True
                self.generate_pattern()
            return
            
        if self.generating_pattern:
            if self.current_pattern_index < len(self.pattern):
                if current_time - self.display_time > 1500:  # Slower blink (1.5s)
                    self.current_pattern_index += 1
                    self.sound_manager.play('terminal')
                    self.display_time = current_time
            else:
                self.generating_pattern = False
                self.terminal.add_message(f">> Your turn! Match the pattern ({self.correct_attempts + 1}/3).")
            return
                
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and not self.generating_pattern:
                for button in self.buttons:
                    if button['rect'].collidepoint(event.pos):
                        self.player_sequence.append(button['index'])
                        self.sound_manager.play('terminal')
                        self.terminal.add_message(f">> Tap {len(self.player_sequence)}/{len(self.pattern)}")
                        
                        if len(self.player_sequence) == len(self.pattern):
                            if self.player_sequence == self.pattern:
                                self.correct_attempts += 1
                                self.sound_manager.play('success')
                                self.terminal.add_message(f">> Correct! ({self.correct_attempts}/3)")
                                if self.correct_attempts >= 3:
                                    self.sound_manager.play('hack')
                                    self.terminal.add_message(">> Firewall breached! On to Level 2!")
                                    self.game_state.update_score(DIFFICULTY_LEVELS[self.game_state.difficulty]['score_reward'] * 3)
                                    self.game_state.level_complete = True
                                else:
                                    self.player_sequence = []
                                    self.generating_pattern = True
                                    self.generate_pattern()
                            else:
                                self.sound_manager.play('error')
                                self.terminal.add_message(">> Wrong! Try again.")
                                self.player_sequence = []
                                self.game_state.lose_life()
                                self.terminal.add_message(f">> Lives remaining: {self.game_state.lives}")
                                self.generating_pattern = True
                                self.display_time = current_time
                                self.current_pattern_index = 0
                                self.generate_pattern()
                                
    def draw(self, screen):
        screen.fill(BLACK)
        
        for i, button in enumerate(self.buttons):
            base_color = button['color']
            base_rect = button['rect']
            
            if self.generating_pattern and self.current_pattern_index > 0 and i == self.pattern[self.current_pattern_index - 1]:
                pulse_factor = (pygame.time.get_ticks() % 800) / 800  # Slower pulse (800ms)
                brightness_boost = int(150 * pulse_factor)
                color = tuple(min(255, c + brightness_boost) for c in base_color)
                enlarged_rect = base_rect.inflate(int(30 * pulse_factor), int(30 * pulse_factor))
                pygame.draw.rect(screen, color, enlarged_rect)
                pygame.draw.rect(screen, WHITE, enlarged_rect, 3)
                pygame.draw.rect(screen, YELLOW, enlarged_rect, 5)
            else:
                pygame.draw.rect(screen, base_color, base_rect)
                pygame.draw.rect(screen, WHITE, base_rect, 2)
            
        self.terminal.draw(screen)
        self.draw_score(screen)
        
        font = pygame.font.Font(None, 36)
        text = font.render("Level 1: Firewall Breach", True, YELLOW)
        screen.blit(text, (10, 10))
        
        if self.generating_pattern and self.current_pattern_index > 0:
            progress_text = font.render(f"Blink {self.current_pattern_index}/{len(self.pattern)}", True, WHITE)
            screen.blit(progress_text, (WINDOW_WIDTH - 200, 10))