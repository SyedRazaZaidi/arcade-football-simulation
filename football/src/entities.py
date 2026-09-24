import pygame
import math
import random
import os
from src.config import *

class Ball:
    def __init__(self, x, y):
        self.start_pos = pygame.math.Vector2(x, y)
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)
        self.radius = 9

    def reset(self):
        self.pos = pygame.math.Vector2(self.start_pos)
        self.vel = pygame.math.Vector2(0, 0)

    def update(self, dt):
        self.vel *= (0.97 ** dt) 
        self.pos += self.vel * dt

        if self.pos.y < PITCH.top or self.pos.y > PITCH.bottom:
            self.vel.y *= -0.8
            self.pos.y = max(PITCH.top, min(self.pos.y, PITCH.bottom))
        if self.pos.x < PITCH.left or self.pos.x > PITCH.right:
            if not (GOAL_Y1 < self.pos.y < GOAL_Y2):
                self.vel.x *= -0.8
                self.pos.x = max(PITCH.left, min(self.pos.x, PITCH.right))

    def draw(self, surf, cam_offset):
        render_pos = self.pos + cam_offset
        pygame.draw.circle(surf, (0, 0, 0, 100), (int(render_pos.x), int(render_pos.y + 6)), self.radius)
        
        pygame.draw.circle(surf, WHITE, (int(render_pos.x), int(render_pos.y)), self.radius)
        pygame.draw.circle(surf, (30, 30, 30), (int(render_pos.x), int(render_pos.y)), self.radius, 2)
        pygame.draw.circle(surf, (30, 30, 30), (int(render_pos.x), int(render_pos.y)), 3)

class Player:
    def __init__(self, x, y, team_color, skin_color, is_cpu=True, formation_pos=(0,0)):
        self.pos = pygame.math.Vector2(x, y)
        self.formation_base = pygame.math.Vector2(formation_pos)
        self.color = team_color
        self.is_cpu = is_cpu
        self.is_active = False 
        
        self.is_gk = (self.formation_base.x < PITCH.left + 150) or (self.formation_base.x > PITCH.right - 150)
        
        self.radius = 18
        self.speed = 5.2
        self.facing = pygame.math.Vector2(1, 0) if not is_cpu else pygame.math.Vector2(-1, 0)
        self.charge = 0
        self.kick_cooldown = 0
        self.dust_particles = []
        
        self.is_moving = False
        self.frame_index = 0
        self.anim_time = 0
        self.has_sprite = False
        self.frames_idle = []
        self.frames_run = []
        
        sprite_path = "assets/sprites/player_blue.png" if self.color == BLUE_TEAM else "assets/sprites/player_red.png"
        
        if os.path.exists(sprite_path):
            try:
                sheet = pygame.image.load(sprite_path).convert()
                bg_color = sheet.get_at((0, 0))
                sheet.set_colorkey(bg_color)
                
                FRAME_W, FRAME_H = 32, 32
                SCALE_SIZE = (48, 48) 
                
                idle_surface = sheet.subsurface((0, 0, FRAME_W, FRAME_H))
                self.frames_idle.append(pygame.transform.scale(idle_surface, SCALE_SIZE))
                
                for col in range(6):
                    run_surface = sheet.subsurface((col * FRAME_W, FRAME_H, FRAME_W, FRAME_H))
                    self.frames_run.append(pygame.transform.scale(run_surface, SCALE_SIZE))
                
                self.has_sprite = True
            except Exception as e:
                print(f"Error slicing sprite: {e}")

    def reset(self):
        self.pos = pygame.math.Vector2(self.formation_base)
        self.facing = pygame.math.Vector2(1, 0) if self.color == BLUE_TEAM else pygame.math.Vector2(-1, 0)
        self.charge = 0
        self.kick_cooldown = 0
        self.dust_particles.clear()

    def update(self, dt, ball, teammates):
        keys = pygame.key.get_pressed() 
        self.is_moving = False
        self.kick_cooldown = max(0, self.kick_cooldown - dt)
        
        if self.is_active and not self.is_cpu:
            move = pygame.math.Vector2(0, 0)
            if keys[pygame.K_w]: move.y -= 1
            if keys[pygame.K_s]: move.y += 1
            if keys[pygame.K_a]: move.x -= 1
            if keys[pygame.K_d]: move.x += 1

            if move.length() > 0:
                move = move.normalize()
                self.facing = move
                self.pos += move * self.speed * dt
                self.is_moving = True
                
            dist_to_ball = (ball.pos - self.pos).length()
            
            if keys[pygame.K_q] and dist_to_ball < 30:
                best_mate, best_dist = None, float('inf')
                for tm in teammates:
                    if tm != self:
                        to_tm = tm.pos - self.pos
                        if to_tm.length() < best_dist and to_tm.normalize().dot(self.facing) > 0.5:
                            best_dist = to_tm.length()
                            best_mate = tm
                if best_mate:
                    ball.vel = (best_mate.pos - ball.pos).normalize() * 22
                    if SND_KICK: SND_KICK.play()
                    
            if keys[pygame.K_SPACE]:
                self.charge = min(30, self.charge + 1.5 * dt)
            else:
                if self.charge > 0 and dist_to_ball < 30:
                    ball.vel = self.facing * (12 + self.charge)
                    if SND_KICK: SND_KICK.play()
                self.charge = 0
        else:
            dist_to_ball = (ball.pos - self.pos).length()
            base_move = pygame.math.Vector2(0, 0)
            
            closest_mate_dist = min([(ball.pos - tm.pos).length() for tm in teammates])
            is_primary_presser = (dist_to_ball <= closest_mate_dist + 5)

            if self.is_gk:
                if dist_to_ball < 200:
                    target_vec = (ball.pos - self.pos)
                    if target_vec.length() > 0:
                        base_move = target_vec.normalize() * (self.speed * 0.85)
                else:
                    target_y = max(GOAL_Y1, min(ball.pos.y, GOAL_Y2))
                    target_pos = pygame.math.Vector2(self.formation_base.x, target_y)
                    target_vec = (target_pos - self.pos)
                    if target_vec.length() > 5:
                        base_move = target_vec.normalize() * (self.speed * 0.7)
            else:
                if is_primary_presser and dist_to_ball < 400:
                    target_vec = (ball.pos - self.pos)
                    if target_vec.length() > 0:
                        base_move = target_vec.normalize() * (self.speed * 0.9)
                else:
                    target_vec = (self.formation_base - self.pos)
                    if target_vec.length() > 5:
                        base_move = target_vec.normalize() * (self.speed * 0.6)

            repulsion = pygame.math.Vector2(0, 0)
            for tm in teammates:
                if tm != self:
                    dist_to_tm = (self.pos - tm.pos).length()
                    if 0 < dist_to_tm < 50: 
                        push = (self.pos - tm.pos).normalize()
                        repulsion += push * (50 - dist_to_tm) * 0.2 
            
            final_move = base_move + repulsion
            if final_move.length() > 0:
                self.facing = final_move.normalize()
                if final_move.length() > self.speed:
                    final_move = final_move.normalize() * self.speed
                self.pos += final_move * dt
                self.is_moving = True

            if is_primary_presser and dist_to_ball < self.radius + ball.radius + 10 and self.kick_cooldown <= 0:
                target_x = PITCH.left if self.color == RED_TEAM else PITCH.right
                target_goal = pygame.math.Vector2(target_x, VIRTUAL_H // 2)
                dist_to_target = (target_goal - self.pos).length()

                if dist_to_target < 600: 
                    shot_target = target_goal + pygame.math.Vector2(0, random.uniform(-90, 90))
                    shoot_dir = (shot_target - ball.pos).normalize()
                    ball.vel = shoot_dir * 28 
                    self.kick_cooldown = 120 
                    if SND_KICK: SND_KICK.play()
                
                elif random.random() < 0.03: 
                    best_pass = None
                    best_forward_dist = 0
                    
                    for tm in teammates:
                        if tm != self and not tm.is_gk: 
                            tm_dist_to_target = (target_goal - tm.pos).length()
                            if tm_dist_to_target < dist_to_target - 100:
                                if dist_to_target - tm_dist_to_target > best_forward_dist:
                                    best_forward_dist = dist_to_target - tm_dist_to_target
                                    best_pass = tm
                                    
                    if best_pass:
                        pass_dir = (best_pass.pos - ball.pos).normalize()
                        ball.vel = pass_dir * 22
                        self.kick_cooldown = 60
                        if SND_KICK: SND_KICK.play()

        if self.has_sprite:
            self.anim_time += dt
            if self.is_moving:
                if self.anim_time > 0.08: 
                    self.frame_index = (self.frame_index + 1) % len(self.frames_run)
                    self.anim_time = 0
            else:
                self.frame_index = 0 

        if self.is_moving and random.random() < 0.15:
            dust_pos = self.pos - (self.facing * 10)
            self.dust_particles.append({
                "pos": pygame.math.Vector2(dust_pos),
                "radius": random.uniform(3, 6),
                "life": 255 
            })

        for dust in self.dust_particles[:]:
            dust["radius"] += 0.2 * dt
            dust["life"] -= 15 * dt
            if dust["life"] <= 0:
                self.dust_particles.remove(dust)

        is_charging_kick = self.is_active and (keys[pygame.K_SPACE] or keys[pygame.K_q])
        if not is_charging_kick:
            dist = (ball.pos - self.pos).length()
            if dist < self.radius + ball.radius:
                overlap = (self.radius + ball.radius) - dist
                if dist > 0:
                    push_dir = (ball.pos - self.pos).normalize()
                    ball.pos += push_dir * overlap
                    ball.vel = push_dir * self.speed * 1.8

    def draw_topdown_human(self, surf, cam_offset):
        for dust in self.dust_particles:
            d_pos = dust["pos"] + cam_offset
            dust_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(dust_surf, (255, 255, 255, max(0, int(dust["life"]))), (10, 10), int(dust["radius"]))
            surf.blit(dust_surf, (int(d_pos.x) - 10, int(d_pos.y) - 10))

        render_pos = self.pos + cam_offset
        center = (int(render_pos.x), int(render_pos.y))
        
        pygame.draw.ellipse(surf, (0, 0, 0, 90), (center[0] - 18, center[1] + 10, 36, 14))
        
        if self.has_sprite:
            current_img = self.frames_run[self.frame_index] if self.is_moving else self.frames_idle[0]
            if self.facing.x < 0:
                current_img = pygame.transform.flip(current_img, True, False)
            img_rect = current_img.get_rect(midbottom=(center[0], center[1] + 16))
            surf.blit(current_img, img_rect)
        else:
            rect = pygame.Rect(0, 0, 24, 36)
            rect.midbottom = (center[0], center[1] + 16)
            pygame.draw.rect(surf, self.color, rect, border_radius=6)
        
        if self.is_active:
            pygame.draw.polygon(surf, (255, 50, 50), [
                (center[0], center[1] - 35),
                (center[0] - 6, center[1] - 45),
                (center[0] + 6, center[1] - 45)
            ])
            pygame.draw.rect(surf, WHITE, (center[0]-7, center[1]-46, 14, 2))