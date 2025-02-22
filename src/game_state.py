from config import DIFFICULTY_LEVELS

class GameState:
    def __init__(self):
        self.current_level = 0
        self.score = 0
        self.lives = 3  # Added lives for more forgiving gameplay
        self.difficulty = 'medium'
        self.time_remaining = DIFFICULTY_LEVELS[self.difficulty]['timer']
        self.game_over = False
        self.level_complete = False
        
    def update_score(self, points):
        self.score += points
        
    def lose_life(self):
        self.lives -= 1
        if self.lives <= 0:
            self.game_over = True
            
    def next_level(self):
        self.current_level += 1
        self.time_remaining = DIFFICULTY_LEVELS[self.difficulty]['timer']
        self.level_complete = False