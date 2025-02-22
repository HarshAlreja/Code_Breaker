import pygame
import random
import math
from levels.base_level import BaseLevel
from config import *

class CircuitPiece:
    def __init__(self, x, y, size):
        self.rect = pygame.Rect(x, y, size, size)
        self.connections = random.choice([
            [True, True, False, False],
            [True, False, True, False],
            [True, True, True, False],
            [True, True, True, True]
        ])
        self.rotation = 0
        self.connected = False
        self.pulse_offset = random.randint(0, PULSE_SPEED)
        self.locked = False
        self.lock_time = 0
        
    def rotate(self):
        if not self.locked:
            self.rotation = (self.rotation + 90) % 360
            self.connections = self.connections[1:] + [self.connections[0]]
        
    def draw(self, screen):
        pulse_factor = ((pygame.time.get_ticks() + self.pulse_offset) % PULSE_SPEED) / PULSE_SPEED
        size_offset = int(5 * pulse_factor) if not self.locked else 0
        draw_rect = self.rect.inflate(-size_offset, -size_offset)
        color = RED if self.locked else (BLUE if self.connected else WHITE)
        pygame.draw.rect(screen, color, draw_rect, 2)
        
        center = self.rect.centerx, self.rect.centery
        size = self.rect.width // 2
        
        for i, connected in enumerate(self.connections):
            if connected:
                angle = i * 90 + self.rotation
                end_x = center[0] + size * math.cos(math.radians(angle))
                end_y = center[1] - size * math.sin(math.radians(angle))
                line_color = CYAN if self.connected else (GREEN if not self.locked else RED)
                pygame.draw.line(screen, line_color, center, (end_x, end_y), 3 + int(2 * pulse_factor))

class EncryptedRoom(BaseLevel):
    def __init__(self, game_state, sound_manager):
        super().__init__(game_state, sound_manager)
        self.grid_size = 4
        self.piece_size = 80
        self.grid = self._create_grid()
        self.start_time = pygame.time.get_ticks()
        self.flash_time = 0
        self.show_instructions = True
        self.instruction_time = pygame.time.get_ticks()
        self.progress_flash = 0
        self.connected_count = 0
        # Hint system
        self.hint_button = pygame.Rect(WINDOW_WIDTH - 100, WINDOW_HEIGHT - 50, 80, 30)
        self.hint_count = 0
        self.max_hints = 3
        self.hint_active = False
        self.hint_text = ""
        self.hint_timer = 0
        self.hints = [
            "Start at the yellow piece (top-left). Connect its right and down lines first!",
            "Match green lines: right to left, up to down. Look for CYAN lines to see connections!",
            "Work row by row or column by column from the yellow piece. Adjust neighbors to link!",
            "If stuck, focus on the bottom-right corner. It must connect back to the chain!"
        ]
        # Initial instructions
        self.terminal.add_message(">> Welcome to Level 2: Circuit Puzzle!")
        self.terminal.add_message(">> Goal: Link all 16 pieces with lines.")
        self.terminal.add_message(">> Click to rotate. Match green lines side-by-side!")
        self.terminal.add_message(">> Start at yellow piece (top-left). Connect right & down.")
        self.terminal.add_message(">> Wrong moves lock pieces 1s. Tap 'HINT' if stuck!")
        
    def _create_grid(self):
        grid = []
        start_x = (WINDOW_WIDTH - (self.grid_size * self.piece_size)) // 2
        start_y = (WINDOW_HEIGHT - (self.grid_size * self.piece_size)) // 2 - 50
        
        for row in range(self.grid_size):
            grid_row = []
            for col in range(self.grid_size):
                x = start_x + col * self.piece_size
                y = start_y + row * self.piece_size
                piece = CircuitPiece(x, y, self.piece_size)
                if row == 0 and col == 0:
                    while not (piece.connections[1] and piece.connections[2]):
                        piece.rotate()
                elif row == 0 and col <= 1:
                    while not piece.connections[3]:
                        piece.rotate()
                elif col == 0 and row <= 1:
                    while not piece.connections[0]:
                        piece.rotate()
                grid_row.append(piece)
            grid.append(grid_row)
        return grid
        
    def check_connections(self):
        for row in self.grid:
            for piece in row:
                piece.connected = False
        connected_pieces = set()
        self._flood_fill(0, 0, connected_pieces)
        return len(connected_pieces), len(connected_pieces) == self.grid_size * self.grid_size
        
    def _flood_fill(self, row, col, connected_pieces):
        if (row, col) in connected_pieces:
            return
        current_piece = self.grid[row][col]
        current_piece.connected = True
        connected_pieces.add((row, col))
        
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        for i, (dr, dc) in enumerate(directions):
            new_row, new_col = row + dr, col + dc
            if (0 <= new_row < self.grid_size and 
                0 <= new_col < self.grid_size and 
                current_piece.connections[i]):
                next_piece = self.grid[new_row][new_col]
                opposite_dir = (i + 2) % 4
                if next_piece.connections[opposite_dir]:
                    self._flood_fill(new_row, new_col, connected_pieces)
    
    def update(self, events):
        current_time = pygame.time.get_ticks()
        
        if self.show_instructions:
            if current_time - self.instruction_time > 7000:
                self.show_instructions = False
                self.terminal.add_message(">> Start with yellow! Connect lines to win!")
            return
            
        # Handle hint popup timeout
        if self.hint_active and current_time - self.hint_timer > 5000:
            self.hint_active = False
        
        time_elapsed = (current_time - self.start_time) // 1000
        self.game_state.time_remaining = max(0, DIFFICULTY_LEVELS[self.game_state.difficulty]['timer'] - time_elapsed)
        
        if self.game_state.time_remaining == 0:
            self.sound_manager.play('alert')
            self.terminal.add_message(">> Time’s up! Security lockdown!")
            self.game_state.lose_life()
            self.terminal.add_message(f">> Lives remaining: {self.game_state.lives}")
            self.start_time = current_time
            return
            
        for row in self.grid:
            for piece in row:
                if piece.locked and current_time - piece.lock_time > 1000:
                    piece.locked = False
                    self.terminal.add_message(">> Piece unlocked!")
        
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and not self.show_instructions:
                if self.hint_button.collidepoint(event.pos) and self.hint_count < self.max_hints:
                    self.hint_count += 1
                    self.hint_active = True
                    self.hint_timer = current_time
                    self.hint_text = self.hints[min(self.hint_count - 1, len(self.hints) - 1)]
                    self.sound_manager.play('terminal')
                    self.terminal.add_message(f">> Hint {self.hint_count}/{self.max_hints}: {self.hint_text}")
                else:
                    for row in range(self.grid_size):
                        for col in range(self.grid_size):
                            piece = self.grid[row][col]
                            if piece.rect.collidepoint(event.pos) and not piece.locked:
                                old_count, _ = self.check_connections()
                                piece.rotate()
                                self.sound_manager.play('terminal')
                                new_count, is_complete = self.check_connections()
                                if is_complete:
                                    self.sound_manager.play('success')
                                    self.sound_manager.play('power_up')
                                    self.terminal.add_message(">> All connected! Vault unlocked!")
                                    self.game_state.update_score(DIFFICULTY_LEVELS[self.game_state.difficulty]['score_reward'])
                                    self.game_state.level_complete = True
                                    self.flash_time = current_time
                                elif new_count <= old_count:
                                    piece.locked = True
                                    piece.lock_time = current_time
                                    self.sound_manager.play('error')
                                    self.terminal.add_message(">> Oops! Piece locked for 1s.")
                                else:
                                    self.connected_count = new_count
                                    self.sound_manager.play('hack')
                                    self.terminal.add_message(f">> Nice! {new_count}/16 connected!")
                                    self.progress_flash = current_time
                            
    def draw(self, screen):
        screen.fill(BLACK)
        
        if self.game_state.level_complete and pygame.time.get_ticks() - self.flash_time < 500:
            screen.fill(GREEN)
        elif pygame.time.get_ticks() - self.progress_flash < 300:
            screen.fill((0, 50, 0))
        
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                piece = self.grid[row][col]
                if row == 0 and col == 0:
                    pygame.draw.rect(screen, YELLOW, piece.rect, 4)
                piece.draw(screen)
        
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                piece = self.grid[row][col]
                center = piece.rect.centerx, piece.rect.centery
                size = self.piece_size // 2
                for i, connected in enumerate(piece.connections):
                    if connected:
                        dr, dc = [(0, -1), (1, 0), (0, 1), (-1, 0)][i]
                        new_row, new_col = row + dr, col + dc
                        if (0 <= new_row < self.grid_size and 0 <= new_col < self.grid_size):
                            next_piece = self.grid[new_row][new_col]
                            opposite_dir = (i + 2) % 4
                            if next_piece.connections[opposite_dir]:
                                next_center = next_piece.rect.centerx, next_piece.rect.centery
                                pulse_factor = (pygame.time.get_ticks() % PULSE_SPEED) / PULSE_SPEED
                                pygame.draw.line(screen, CYAN, center, next_center, 5 + int(2 * pulse_factor))
        
        self.terminal.draw(screen)
        self.draw_score(screen)
        
        # Hint button
        pygame.draw.rect(screen, GREEN if self.hint_count < self.max_hints else RED, self.hint_button)
        pygame.draw.rect(screen, WHITE, self.hint_button, 2)
        font = pygame.font.Font(None, 24)
        hint_label = font.render("HINT", True, WHITE)
        screen.blit(hint_label, (self.hint_button.x + 15, self.hint_button.y + 5))
        
        # Hint popup
        if self.hint_active:
            popup_rect = pygame.Rect(WINDOW_WIDTH // 4, WINDOW_HEIGHT // 4, WINDOW_WIDTH // 2, 150)
            pygame.draw.rect(screen, (0, 0, 0, 180), popup_rect, 0, 10)  # Semi-transparent black
            pygame.draw.rect(screen, WHITE, popup_rect, 2)
            hint_font = pygame.font.Font(None, 28)
            lines = self.hint_text.split('. ')
            y_offset = popup_rect.y + 20
            for line in lines:
                if line:
                    text_surface = hint_font.render(line.strip() + '.', True, WHITE)
                    screen.blit(text_surface, (popup_rect.x + 20, y_offset))
                    y_offset += 30
        
        # Progress bar
        font = pygame.font.Font(None, 36)
        text = font.render(f"Level 2: Circuit Puzzle - Time: {self.game_state.time_remaining}s", True, YELLOW)
        screen.blit(text, (10, 10))
        progress_width = (WINDOW_WIDTH - 40) * (self.connected_count / (self.grid_size * self.grid_size))
        pygame.draw.rect(screen, GREEN, (20, WINDOW_HEIGHT - 20, progress_width, 10))
        pygame.draw.rect(screen, WHITE, (20, WINDOW_HEIGHT - 20, WINDOW_WIDTH - 40, 10), 2)