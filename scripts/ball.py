import pygame
import os
import math
from constant_values import FPS


class Ball(pygame.sprite.Sprite):
    DIAMETER = 20
    DECELERATION = 0.995

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)

        ball_img = pygame.image.load(os.path.join('Assets', 'balls', 'basket-ball.png')).convert_alpha()
        ball_img_scaled = pygame.transform.scale(ball_img, (self.DIAMETER, self.DIAMETER))
        self.image = ball_img_scaled
        self.rect = self.image.get_rect(center=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
        self.mask_image = self.mask.to_surface()
        self.vel = pygame.math.Vector2
        self.speed = 3
        self.dvel = pygame.math.Vector2
        self.danger = True
        self.caught_by_player = None
        self.throw_force=5

    def def_vel(self, x_vel, y_vel):
        self.vel = pygame.math.Vector2(x_vel, y_vel)
        self.dvel = pygame.math.Vector2(self.vel.x / (FPS ** 2), self.vel.y / (FPS ** 2))

    def maintain_collision_obstacle(self, obstacles):
        collision = pygame.sprite.spritecollide(self, obstacles, False, pygame.sprite.collide_mask)
        if collision:
            obstacle = collision[0]
            if obstacle.destroyable:
                obstacle.update_hp()
            if (self.rect.bottom <= obstacle.rect.bottom + self.DIAMETER and
                    self.rect.top >= obstacle.rect.top - self.DIAMETER):
                if self.rect.right <= obstacle.rect.left:
                    self.rect.center -= (2 * self.dvel.x, 0)
                    self.vel.x *= -1
                elif self.rect.left >= obstacle.rect.right:
                    self.rect.x += 2 * self.dvel.x
                    self.vel.x *= -1
                self.vel.x *= -1
            if self.rect.x in range(obstacle.rect.left - 1, obstacle.rect.right + 1):
                if self.rect.y >= obstacle.rect.centery:
                    self.rect.y += self.dvel.y
                elif self.rect.y <= obstacle.rect.centery:
                    self.rect.y -= self.dvel.y
                self.vel.y *= -1
                self.vel.x *= -1

    def check_collision_player(self, players_playing):
        collision = None
        if self.caught_by_player is None:
            collision = pygame.sprite.spritecollide(self, players_playing, False, pygame.sprite.collide_mask)
        if collision:
            player = collision[0]
            if not self.danger:
                self.caught_by_player = player
                self.throw_force=player.force
                player.bench = False
            else:
                self.caught_by_player = None
                player.bench = True
        return collision

    def move(self, cue):
        if self.caught_by_player:
            cue.visible = True
            self.rect.center = self.caught_by_player.rect.center
        else:
            self.vel *= self.DECELERATION
            self.rect.center += self.vel
            self.speed = pygame.math.Vector2.length(self.vel)
            if self.speed < 3:
                self.danger = False
            else:
                self.danger = True

    def throw_a_ball(self, stick):
        throwing_x_vel = -math.cos(math.radians(stick.angle)) * self.throw_force
        throwing_y_vel = math.sin(math.radians(stick.angle)) * self.throw_force
        # can be force*x_impulse, y_impulse depending on a player
        self.def_vel(throwing_x_vel, throwing_y_vel)
        self.caught_by_player = None
        self.danger = True
        stick.visible = False


class Stick(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.stick_original_img = pygame.image.load(os.path.join('Assets', 'players', 'cue.png')).convert_alpha()
        self.angle = 0
        self.image = pygame.transform.rotate(self.stick_original_img, self.angle)
        self.rect = self.image.get_rect(center=pos)
        self.visible = False

    def update(self, surface, ball):
        mouse_pos = pygame.mouse.get_pos()
        self.rect.center = ball.rect.center
        if self.visible:
            x_dist = ball.rect.center[0] - mouse_pos[0]
            y_dist = ball.rect.center[1] - mouse_pos[1]
            self.angle = -math.degrees(math.atan2(y_dist, x_dist))

            self.image = pygame.transform.rotate(self.stick_original_img, self.angle)
            surface.blit(self.image, (self.rect.centerx - self.image.get_width() / 2,
                                      self.rect.centery - self.image.get_height() / 2))
