import pygame
import random
from src.config import *

class AIAgent:
    """Encapsulates advanced AI behaviors including Boids separation,
    role-based tactical pressing, goalkeeper bounding, and attacking decision trees."""
    
    @staticmethod
    def calculate_ai_movement(player, ball, teammates, dt):
        dist_to_ball = (ball.pos - player.pos).length()
        base_move = pygame.math.Vector2(0, 0)
        
        closest_mate_dist = min([(ball.pos - tm.pos).length() for tm in teammates])
        is_primary_presser = (dist_to_ball <= closest_mate_dist + 5)

        if player.is_gk:
            # --- GOALKEEPER STATE MACHINE ---
            if dist_to_ball < 200:
                # Danger Zone: Charge down the ball
                target_vec = (ball.pos - player.pos)
                if target_vec.length() > 0:
                    base_move = target_vec.normalize() * (player.speed * 0.85)
            else:
                # Safe Zone: Strafe the goal line matching the ball's Y-coordinate
                target_y = max(GOAL_Y1, min(ball.pos.y, GOAL_Y2))
                target_pos = pygame.math.Vector2(player.formation_base.x, target_y)
                target_vec = (target_pos - player.pos)
                if target_vec.length() > 5:
                    base_move = target_vec.normalize() * (player.speed * 0.7)
        else:
            # --- OUTFIELD PLAYER STATE MACHINE ---
            if is_primary_presser and dist_to_ball < 400:
                target_vec = (ball.pos - player.pos)
                if target_vec.length() > 0:
                    base_move = target_vec.normalize() * (player.speed * 0.9)
            else:
                target_vec = (player.formation_base - player.pos)
                if target_vec.length() > 5:
                    base_move = target_vec.normalize() * (player.speed * 0.6)

        # --- BOIDS COLLISION AVOIDANCE (SEPARATION) ---
        repulsion = pygame.math.Vector2(0, 0)
        for tm in teammates:
            if tm != player:
                dist_to_tm = (player.pos - tm.pos).length()
                if 0 < dist_to_tm < 50: 
                    push = (player.pos - tm.pos).normalize()
                    repulsion += push * (50 - dist_to_tm) * 0.2 
        
        final_move = base_move + repulsion
        return final_move, is_primary_presser
        
    @staticmethod
    def evaluate_attacking_decisions(player, ball, teammates, is_primary_presser, dist_to_ball):
        if is_primary_presser and dist_to_ball < player.radius + ball.radius + 10 and player.kick_cooldown <= 0:
            target_x = PITCH.left if player.color == RED_TEAM else PITCH.right
            target_goal = pygame.math.Vector2(target_x, VIRTUAL_H // 2)
            dist_to_target = (target_goal - player.pos).length()

            # --- SHOOTING STATE ---
            if dist_to_target < 600: 
                shot_target = target_goal + pygame.math.Vector2(0, random.uniform(-90, 90))
                shoot_dir = (shot_target - ball.pos).normalize()
                ball.vel = shoot_dir * 28 
                player.kick_cooldown = 120 
                if SND_KICK: SND_KICK.play()
                return True
            
            # --- PASSING STATE ---
            elif random.random() < 0.03: 
                best_pass = None
                best_forward_dist = 0
                
                for tm in teammates:
                    if tm != player and not tm.is_gk: 
                        tm_dist_to_target = (target_goal - tm.pos).length()
                        if tm_dist_to_target < dist_to_target - 100:
                            if dist_to_target - tm_dist_to_target > best_forward_dist:
                                best_forward_dist = dist_to_target - tm_dist_to_target
                                best_pass = tm
                                
                if best_pass:
                    pass_dir = (best_pass.pos - ball.pos).normalize()
                    ball.vel = pass_dir * 22
                    player.kick_cooldown = 60
                    if SND_KICK: SND_KICK.play()
                    return True
                    
        return False