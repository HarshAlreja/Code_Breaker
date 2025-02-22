WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Color constants
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)  # Added for visual variety

# Game settings
DIFFICULTY_LEVELS = {
    'easy': {'timer': 150, 'pattern_length': 4, 'score_reward': 100},
    'medium': {'timer': 100, 'pattern_length': 6, 'score_reward': 200},
    'hard': {'timer': 75, 'pattern_length': 8, 'score_reward': 300}
}

# Animation settings
PULSE_SPEED = 200  # Milliseconds for visual pulsing effects