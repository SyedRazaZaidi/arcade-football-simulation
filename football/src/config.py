import pygame

# Initialize Pygame Audio Mixer globally
pygame.mixer.init()

# --- SETTINGS ---
WIDTH, HEIGHT = 1200, 800
VIRTUAL_W, VIRTUAL_H = 2400, 1500

PITCH = pygame.Rect(100, 100, VIRTUAL_W - 200, VIRTUAL_H - 200)
GOAL_Y1 = VIRTUAL_H // 2 - 120
GOAL_Y2 = VIRTUAL_H // 2 + 120

TURF_DARK = (34, 139, 34)
TURF_LIGHT = (46, 154, 46)
WHITE = (255, 255, 255)
BLUE_TEAM = (25, 118, 210)
BLUE_SKIN = (255, 204, 153)
RED_TEAM = (211, 47, 47)
RED_SKIN = (141, 85, 36)

# --- AUDIO ASSETS (MP3 FORMAT) ---
try:
    SND_KICK = pygame.mixer.Sound("assets/sounds/kick.mp3")
    SND_WHISTLE = pygame.mixer.Sound("assets/sounds/whistle.mp3")
    SND_CROWD = pygame.mixer.Sound("assets/sounds/crowd.mp3")
    
    # Adjust volumes so the crowd doesn't blow out your speakers
    SND_KICK.set_volume(0.6)
    SND_WHISTLE.set_volume(0.8)
    SND_CROWD.set_volume(0.5)
except Exception as e:
    print(f"Audio files missing or failed to load: {e}")
    SND_KICK = SND_WHISTLE = SND_CROWD = None