import pygame
import random
from levels.base_level import BaseLevel
from config import *

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.speed = 6
        self.visible = True
        self.cloak_time = 0
        self.can_cloak = True
        
    def move(self, dx, dy, walls):
        original_x = self.rect.x
        original_y = self.rect.y
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed
        for wall in walls:
            if self.rect.colliderect(wall):
                self.rect.x = original_x
                self.rect.y = original_y
                break
                
    def toggle_cloak(self, current_time):
        if self.can_cloak:
            self.visible = not self.visible
            self.cloak_time = current_time
            self.can_cloak = False
            return True
        return False

class AI:
    def __init__(self, x, y, patrol_points):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.speed = 5
        self.patrol_points = patrol_points
        self.current_point = 0
        self.alert = False
        self.alert_time = 0
        
    def update(self, player, current_time, walls):
        if self.alert and current_time - self.alert_time > 3000:
            self.alert = False
            
        if self.alert and player.visible:
            dx = player.rect.x - self.rect.x
            dy = player.rect.y - self.rect.y
            dist = pygame.math.Vector2(dx, dy).length()
            if dist > 0:
                dx, dy = dx/dist, dy/dist
                self.move(dx, dy, walls)
        else:
            if self.patrol_points:
                target = self.patrol_points[self.current_point]
                dx = target[0] - self.rect.x
                dy = target[1] - self.rect.y
                dist = pygame.math.Vector2(dx, dy).length()
                if dist < 10:
                    self.current_point = (self.current_point + 1) % len(self.patrol_points)
                else:
                    dx, dy = dx/dist, dy/dist
                    self.move(dx, dy, walls)
                    
        if player.visible and self.rect.colliderect(player.rect.inflate(150, 150)):
            self.alert = True
            self.alert_time = current_time
                    
    def move(self, dx, dy, walls):
        original_x = self.rect.x
        original_y = self.rect.y
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed
        for wall in walls:
            if self.rect.colliderect(wall):
                self.rect.x = original_x
                self.rect.y = original_y
                break

class AIShowdown(BaseLevel):
    def __init__(self, game_state, sound_manager):
        super().__init__(game_state, sound_manager)
        self.walls = self._create_maze()
        self.player = Player(50, 50)
        self.ais = [
            AI(WINDOW_WIDTH - 100, WINDOW_HEIGHT - 100, [
                (WINDOW_WIDTH - 100, WINDOW_HEIGHT - 100),
                (WINDOW_WIDTH - 100, 100),
                (100, 100),
                (100, WINDOW_HEIGHT - 100)
            ]),
            AI(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, [
                (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2),
                (WINDOW_WIDTH // 2, 50),
                (50, WINDOW_HEIGHT // 2),
                (WINDOW_WIDTH - 50, WINDOW_HEIGHT - 50)
            ])
        ]
        self.override_switch = pygame.Rect(WINDOW_WIDTH - 80, 50, 30, 30)
        self.show_instructions = True
        self.instruction_time = pygame.time.get_ticks()
        # Precise instructions
        self.terminal.add_message(">> Welcome to Level 3: AI Chase!")
        self.terminal.add_message(">> Goal: Reach the pulsing red switch (top-right).")
        self.terminal.add_message(">> Move with W/A/S/D. Avoid 2 AIs (cyan/red boxes).")
        self.terminal.add_message(">> SPACE to cloak (2s, 5s cooldown) when near AIs.")
        self.terminal.add_message(">> If caught, reset. Navigate blue walls carefully!")
        
    def _create_maze(self):
        walls = []
        wall_rects = [
            (200, 100, 20, 400),
            (400, 100, 20, 300),
            (600, 200, 20, 400),
            (100, 200, 200, 20),
            (300, 300, 200, 20),
            (500, 400, 200, 20),
            (100, 500, 400, 20),
            (300, 150, 100, 20)
        ]
        for rect in wall_rects:
            walls.append(pygame.Rect(rect))
        return walls
        
    def update(self, events):
        current_time = pygame.time.get_ticks()
        
        if self.show_instructions:
            if current_time - self.instruction_time > 7000:
                self.show_instructions = False
                self.terminal.add_message(">> Start moving! Cloak to dodge AIs, reach the switch!")
            return
            
        keys = pygame.key.get_pressed()
        dx = keys[pygame.K_d] - keys[pygame.K_a]
        dy = keys[pygame.K_s] - keys[pygame.K_w]
        self.player.move(dx, dy, self.walls)
        
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if self.player.toggle_cloak(current_time):
                    self.sound_manager.play('power_up')
                    self.terminal.add_message(">> Cloaking active (2s)!")
                    if any(ai.alert for ai in self.ais):
                        self.game_state.update_score(50)
                        self.terminal.add_message(">> +50 for stealth!")
        
        for ai in self.ais:
            ai.update(self.player, current_time, self.walls)
        
        if self.player.rect.colliderect(self.override_switch):
            self.sound_manager.play('success')
            self.terminal.add_message(">> Switch reached! AIs neutralized!")
            self.game_state.update_score(DIFFICULTY_LEVELS[self.game_state.difficulty]['score_reward'])
            self.game_state.level_complete = True
            
        for ai in self.ais:
            if self.player.visible and self.player.rect.colliderect(ai.rect):
                self.sound_manager.play('alert')
                self.terminal.add_message(">> Caught by AI! Back to start.")
                self.game_state.lose_life()
                self.terminal.add_message(f">> Lives remaining: {self.game_state.lives}")
                self.player.rect.topleft = (50, 50)
            
            if ai.alert and current_time - ai.alert_time < 1000:
                self.sound_manager.play('alert', volume=0.5)
        
        if not self.player.can_cloak and current_time - self.player.cloak_time > 2000:
            self.player.can_cloak = True
            self.player.visible = True
            self.terminal.add_message(">> Cloak recharged (5s cooldown)!")
            
    def draw(self, screen):
        screen.fill(BLACK)
        for wall in self.walls:
            pygame.draw.rect(screen, BLUE, wall)
        
        pulse_factor = (pygame.time.get_ticks() % PULSE_SPEED) / PULSE_SPEED
        switch_rect = self.override_switch.inflate(int(10 * pulse_factor), int(10 * pulse_factor))
        pygame.draw.rect(screen, RED, switch_rect)
        pygame.draw.rect(screen, YELLOW, switch_rect, 3)  # Highlight switch
        
        if self.player.visible:
            pygame.draw.rect(screen, GREEN, self.player.rect)
            for ai in self.ais:
                if ai.alert:
                    pygame.draw.rect(screen, RED, self.player.rect.inflate(150, 150), 1)  # Danger zone
        
        for ai in self.ais:
            ai_color = RED if ai.alert else CYAN
            if ai.alert:
                pulse_factor = (pygame.time.get_ticks() % PULSE_SPEED) / PULSE_SPEED
                ai_size = ai.rect.inflate(int(10 * pulse_factor), int(10 * pulse_factor))
                pygame.draw.rect(screen, ai_color, ai_size)
            else:
                pygame.draw.rect(screen, ai_color, ai.rect)
            
        self.terminal.draw(screen)
        self.draw_score(screen)
        
        font = pygame.font.Font(None, 36)
        text = font.render("Level 3: AI Chase - Space to cloak", True, YELLOW)
        screen.blit(text, (10, 10))