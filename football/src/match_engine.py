import pygame
from src.config import SND_WHISTLE, SND_CROWD

class MatchEngine:
    """Manages match timing, scoreboards, goal celebrations, and match state transitions."""
    def __init__(self):
        self.time_seconds = 0
        self.score_blue = 0
        self.score_red = 0
        self.state = "PLAYING" # States: "PLAYING", "GOAL"
        self.goal_timer = 0
        self.goal_scorer = ""
        
    def format_clock(self):
        mins = int((self.time_seconds / 60) * 15)
        return f"{min(mins, 90):02d}:{(int(self.time_seconds * 15) % 60):02d}"
        
    def trigger_goal(self, team):
        self.state = "GOAL"
        self.goal_timer = 3.0 # Pause duration for broadcast graphic
        self.goal_scorer = team
        
        if team == "BLUE":
            self.score_blue += 1
        else:
            self.score_red += 1
            
        if SND_WHISTLE: 
            SND_WHISTLE.play()
        if SND_CROWD: 
            SND_CROWD.play()

    def reset_kickoff(self):
        self.state = "PLAYING"
        if SND_WHISTLE: 
            SND_WHISTLE.play()

    def update(self, dt_seconds):
        if self.state == "PLAYING":
            self.time_seconds += dt_seconds