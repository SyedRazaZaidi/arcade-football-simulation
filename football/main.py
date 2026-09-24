import pygame
import sys
from src.config import *
from src.entities import Ball, Player

pygame.init()
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("football")
CLOCK = pygame.time.Clock()

try:
    FONT_SCORE = pygame.font.SysFont("Trebuchet MS", 48, bold=True)
    FONT_UI = pygame.font.SysFont("Trebuchet MS", 24, bold=True)
    FONT_BIG = pygame.font.SysFont("Impact", 100)
except Exception:
    FONT_SCORE, FONT_UI = pygame.font.Font(None, 64), pygame.font.Font(None, 32)
    FONT_BIG = pygame.font.Font(None, 120)

class MatchEngine:
    def __init__(self):
        self.time_seconds = 0
        self.score_blue = 0
        self.score_red = 0
        self.state = "PLAYING"
        self.goal_timer = 0
        self.goal_scorer = ""
        
    def format_clock(self):
        mins = int((self.time_seconds / 60) * 15)
        return f"{min(mins, 90):02d}:{(int(self.time_seconds * 15) % 60):02d}"
        
    def trigger_goal(self, team):
        self.state = "GOAL"
        self.goal_timer = 3.0 
        self.goal_scorer = team
        if team == "BLUE":
            self.score_blue += 1
        else:
            self.score_red += 1
            
        if SND_WHISTLE: SND_WHISTLE.play()
        if SND_CROWD: SND_CROWD.play()

    def reset_kickoff(self):
        self.state = "PLAYING"
        if SND_WHISTLE: SND_WHISTLE.play()

def generate_team(is_red):
    team = []
    cx, cy = VIRTUAL_W // 2, VIRTUAL_H // 2
    formations = [
        (cx - 150, cy), (cx - 300, cy - 350), (cx - 300, cy + 350),
        (cx - 500, cy), (cx - 550, cy - 250), (cx - 550, cy + 250),
        (cx - 800, cy - 150), (cx - 800, cy + 150),
        (cx - 750, cy - 400), (cx - 750, cy + 400), (PITCH.left + 40, cy)
    ]
    for pos in formations:
        x = pos[0] if not is_red else VIRTUAL_W - pos[0]
        color, skin = (RED_TEAM, RED_SKIN) if is_red else (BLUE_TEAM, BLUE_SKIN)
        team.append(Player(x, pos[1], color, skin, is_cpu=True, formation_pos=(x, pos[1])))
    return team

def draw_minimap(surf, blue_team, red_team, ball):
    map_w, map_h = 300, 187
    map_surf = pygame.Surface((map_w, map_h), pygame.SRCALPHA)
    pygame.draw.rect(map_surf, (0, 0, 0, 180), (0, 0, map_w, map_h), border_radius=10)
    pygame.draw.rect(map_surf, WHITE, (0, 0, map_w, map_h), 2, border_radius=10)
    pygame.draw.line(map_surf, WHITE, (map_w//2, 0), (map_w//2, map_h), 1)

    def scale(pos):
        return (int((pos.x / VIRTUAL_W) * map_w), int((pos.y / VIRTUAL_H) * map_h))

    for p in blue_team: pygame.draw.circle(map_surf, BLUE_TEAM, scale(p.pos), 3)
    for p in red_team: pygame.draw.circle(map_surf, RED_TEAM, scale(p.pos), 3)
    pygame.draw.circle(map_surf, WHITE, scale(ball.pos), 4)
    surf.blit(map_surf, (WIDTH // 2 - map_w // 2, HEIGHT - map_h - 15))

def main():
    ball = Ball(VIRTUAL_W // 2, VIRTUAL_H // 2)
    blue_team = generate_team(is_red=False)
    red_team = generate_team(is_red=True)
    blue_team[0].is_cpu = False
    blue_team[0].is_active = True
    match = MatchEngine()

    while True:
        dt = CLOCK.tick(60) / 1000.0 * 60.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if match.state == "PLAYING":
            match.time_seconds += (CLOCK.get_time() / 1000.0)
            nearest_player = min(blue_team, key=lambda p: (p.pos - ball.pos).length())
            for p in blue_team:
                p.is_active = False
                p.is_cpu = True
            nearest_player.is_active = True
            nearest_player.is_cpu = False

            ball.update(dt)
            for p in blue_team: p.update(dt, ball, blue_team)
            for p in red_team: p.update(dt, ball, red_team)
            
            if GOAL_Y1 < ball.pos.y < GOAL_Y2:
                if ball.pos.x < PITCH.left: match.trigger_goal("RED")
                elif ball.pos.x > PITCH.right: match.trigger_goal("BLUE")
                    
        elif match.state == "GOAL":
            match.goal_timer -= (CLOCK.get_time() / 1000.0)
            if match.goal_timer <= 0:
                ball.reset()
                for p in blue_team + red_team: p.reset()
                match.reset_kickoff()

        # --- CAMERA ENGINE ---
        target_cam_x = WIDTH // 2 - ball.pos.x
        target_cam_y = HEIGHT // 2 - ball.pos.y
        cam_x = max(-(VIRTUAL_W - WIDTH) - 100, min(100, target_cam_x))
        cam_y = max(-(VIRTUAL_H - HEIGHT) - 100, min(100, target_cam_y))
        cam_offset = pygame.math.Vector2(cam_x, cam_y)

        # --- RENDERING ---
        SCREEN.fill(TURF_DARK)
        
        for x in range(PITCH.left, PITCH.right, 80):
            if (x // 80) % 2 == 0:
                stripe_rect = pygame.Rect(x + cam_x, PITCH.top + cam_y, 80, PITCH.height)
                pygame.draw.rect(SCREEN, TURF_LIGHT, stripe_rect)
                
        pitch_rect = PITCH.move(cam_x, cam_y)
        pygame.draw.rect(SCREEN, WHITE, pitch_rect, 4)
        pygame.draw.line(SCREEN, WHITE, (VIRTUAL_W//2 + cam_x, PITCH.top + cam_y), (VIRTUAL_W//2 + cam_x, PITCH.bottom + cam_y), 4)
        pygame.draw.circle(SCREEN, WHITE, (VIRTUAL_W//2 + cam_x, VIRTUAL_H//2 + cam_y), 100, 4)

        pygame.draw.rect(SCREEN, WHITE, (PITCH.left-60 + cam_x, GOAL_Y1 + cam_y, 60, 240), 4)
        pygame.draw.rect(SCREEN, WHITE, (PITCH.right + cam_x, GOAL_Y1 + cam_y, 60, 240), 4)

        for p in blue_team + red_team: p.draw_topdown_human(SCREEN, cam_offset)
        ball.draw(SCREEN, cam_offset)
        draw_minimap(SCREEN, blue_team, red_team, ball)

        hud_bg = pygame.Surface((WIDTH, 50), pygame.SRCALPHA)
        pygame.draw.rect(hud_bg, (0, 0, 0, 150), (0, 0, WIDTH, 50))
        SCREEN.blit(hud_bg, (0, 0))
        
        clock_txt = FONT_SCORE.render(match.format_clock(), True, WHITE)
        SCREEN.blit(clock_txt, (WIDTH//2 - clock_txt.get_width()//2, 2))
        score_txt = FONT_UI.render(f"BLUE {match.score_blue}  -  {match.score_red} RED", True, WHITE)
        SCREEN.blit(score_txt, (20, 12))

        if match.state == "GOAL":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(overlay, (0, 0, 0, 180), (0, HEIGHT//2 - 80, WIDTH, 160))
            SCREEN.blit(overlay, (0, 0))
            goal_color = BLUE_TEAM if match.goal_scorer == "BLUE" else RED_TEAM
            g_txt = FONT_BIG.render(f"{match.goal_scorer} SCORES!", True, goal_color)
            SCREEN.blit(g_txt, (WIDTH//2 - g_txt.get_width()//2, HEIGHT//2 - 50))

        pygame.display.flip()

if __name__ == "__main__":
    main()