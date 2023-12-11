import pygame
from constant_values import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from random import uniform
import os

class Ball(pygame.sprite.Sprite):
    COLOR = 'Black'
    RADIUS = 10

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        ball_img = pygame.image.load(os.path.join('Assets/balls', 'basket-ball.png')).convert_alpha()
        ball_img_scaled = pygame.transform.scale_by(ball_img, 0.025)
        self.image = ball_img_scaled
        self.rect = self.image.get_rect(center=(x, y))
        self.vel = pygame.math.Vector2
        self.dvel = pygame.math.Vector2

    def def_rand_vel(self):
        self.vel = pygame.math.Vector2(uniform(1, 5), uniform(1, 5))
        self.dvel = pygame.math.Vector2(self.vel.x / (FPS ** 2), self.vel.y / (FPS ** 2))

    def draw(self, screen):
        pass
        #pygame.draw.circle(screen, Ball.COLOR, self.rect.center, Ball.RADIUS)

    def move(self):  # how we move the ball, always plus vel can be positive or negative
        self.rect.center += self.vel

    def check_collision_wall(self):
        if self.rect.bottom >= SCREEN_HEIGHT or self.rect.top <= 0:
            self.vel.y *= -1
        if self.rect.right >= SCREEN_WIDTH or self.rect.left <= 0:
            self.vel.x *= -1

    def check_collision_player(self, players_playing):
        collision = pygame.sprite.spritecollide(self, players_playing, False, pygame.sprite.collide_mask)
        if collision:
            player = collision[0]
            # self.vel.xy = (0, 0)
            player.bench = True
        return collision

    def check_collision_obstacle(self, obstacles):
        collision = pygame.sprite.spritecollide(self, obstacles, False, pygame.sprite.collide_mask)
        
        if collision:
            obstacle = collision[0]
            # Check left and right sides of the obstacle
            if (self.rect.bottom <= obstacle.rect.bottom + 2 * self.RADIUS and
                    self.rect.top >= obstacle.rect.top - 2 * self.RADIUS):

                if self.rect.right <= obstacle.rect.left:
                    self.rect.center -= (2 * self.dvel.x, 0)
                    self.vel.x *= -1
                elif self.rect.left >= obstacle.rect.right:
                    self.rect.x += 2 * self.dvel.x
                    self.vel.x *= -1
                self.vel.x *= -1

            if self.rect.x in range(obstacle.rect.left, obstacle.rect.right + 1):
                # Check top and bottom sides of the obstacle
                if self.rect.y >= obstacle.rect.centery:
                    self.rect.y += self.dvel.y
                    self.vel.y *= -1
                elif self.rect.y <= obstacle.rect.centery:
                    self.rect.y -= self.dvel.y
                    self.vel.y *= -1
