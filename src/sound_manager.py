import os
import pygame

class SoundManager:
    def __init__(self):
        self.sounds = {}
        self._load_sounds()
        
    def _load_sounds(self):
        sound_files = {
            'alert': 'alert.ogg',
            'success': 'success.ogg',
            'scan': 'scan.ogg',
            'hack': 'hack.ogg',
            'error': 'error.ogg',
            'portal': 'portal.ogg',
            'terminal': 'terminal.ogg',
            'ambient': 'success.ogg',
            'power_up': 'power_up.ogg'
        }
        
        # Get the absolute directory of the current script (sound_manager.py)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct path to assets/sounds, one level up from src
        for sound_name, file_name in sound_files.items():
            try:
                sound_path = os.path.join(current_dir, '..', 'assets', 'sounds', file_name)
                sound_path = os.path.normpath(sound_path)  # Normalize to resolve '..' correctly
                self.sounds[sound_name] = pygame.mixer.Sound(sound_path)
            except (pygame.error, FileNotFoundError) as e:
                print(f"Warning: Could not load sound {file_name}: {e}")
    
    def play(self, sound_name, volume=1.0):
        if sound_name in self.sounds:
            self.sounds[sound_name].set_volume(volume)
            self.sounds[sound_name].play()