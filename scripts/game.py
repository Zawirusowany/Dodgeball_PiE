import pygame
from random import randint, seed, uniform
from player import Player
from obstacle import Obstacle, Midline, DestroyableObstacle
from ball import Ball
from ball import Cue
from constant_values import (SCREEN_WIDTH, SCREEN_HEIGHT, BORDERS_PARAMETER, LEFT, RIGHT,
                             MAX_HEIGHT_OBSTACLE, MAX_WIDTH_OBSTACLE, BORDER_COLOR, SCOREBOARD)
from marker import Marker

pygame.init()

SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT + SCOREBOARD))
pygame.display.set_caption('Dodge-ball')
Player.load_player_images()

FPS = 60

MENU = 0
PREPARATION = 1
GAME = 2
ENDGAME = 3

hit_left = 0
hit_right = 0
catch_left = 0
catch_right = 0


def draw(walls, all_objects, all_players, ball, middle_line, marker):
   
    SCREEN.fill('Green')

    middle_line.draw(SCREEN)
    walls.draw(SCREEN)
    for obj in all_objects:
        obj.draw(SCREEN)
    all_players.draw(SCREEN)
    marker.draw(SCREEN)
    ball.draw(SCREEN)
    all_players.update()


def generate_obstacles(obstacles, all_players, map_obstacles):
    for _ in range(0, 3):
        x = randint(0, SCREEN_WIDTH - MAX_WIDTH_OBSTACLE)
        y = randint(0, SCREEN_HEIGHT - MAX_HEIGHT_OBSTACLE)
        new_obstacle = Obstacle(MAX_WIDTH_OBSTACLE, MAX_HEIGHT_OBSTACLE, x, y)
        collision_detection_group = pygame.sprite.Group()
        collision_detection_group.add(obstacles, all_players, map_obstacles)

        while pygame.sprite.spritecollide(new_obstacle, collision_detection_group, False):
            x = randint(0, SCREEN_WIDTH - MAX_WIDTH_OBSTACLE)
            y = randint(0, SCREEN_HEIGHT - MAX_HEIGHT_OBSTACLE)
            new_obstacle = Obstacle(MAX_WIDTH_OBSTACLE, MAX_HEIGHT_OBSTACLE, x, y)
        map_obstacles.add(new_obstacle)
        collision_detection_group.add(new_obstacle)

    for _ in range(0, 3):
        x = randint(0, SCREEN_WIDTH - MAX_WIDTH_OBSTACLE)
        y = randint(0, SCREEN_HEIGHT - MAX_HEIGHT_OBSTACLE)
        new_obstacle = DestroyableObstacle(MAX_WIDTH_OBSTACLE, MAX_HEIGHT_OBSTACLE, x, y)
        while pygame.sprite.spritecollide(new_obstacle, collision_detection_group, False):
            x = randint(0, SCREEN_WIDTH - MAX_WIDTH_OBSTACLE)
            y = randint(0, SCREEN_HEIGHT - MAX_HEIGHT_OBSTACLE)
            new_obstacle = DestroyableObstacle(MAX_WIDTH_OBSTACLE, MAX_HEIGHT_OBSTACLE, x, y)
        map_obstacles.add(new_obstacle)
        collision_detection_group.add(new_obstacle)


def check_benched(players_playing, bench_left, bench_right, team_left, team_right):
    for player in players_playing:
        if player.bench:
            players_playing.remove(player)
            if player.team == RIGHT:
                player.image = Player.player_images[1]
                team_right.remove(player)
                bench_right.append(player)
            if player.team == LEFT:
                player.image = Player.player_images[0]
                team_left.remove(player)
                bench_left.append(player)
            player.rect = player.image.get_rect()

    width = Player.player_img_left_direction.get_width()
    for count, player in enumerate(bench_left):
        player.rect.center = (SCOREBOARD / 2 + width * count, SCREEN_HEIGHT + SCOREBOARD / 2)
    for count, player in enumerate(bench_right):
        player.rect.center = (SCREEN_WIDTH - (SCOREBOARD / 2 + width * count), SCREEN_HEIGHT + SCOREBOARD / 2)


def endgame(winner):
    font = pygame.font.Font("freesansbold.ttf", 45)
    over_game = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT + SCOREBOARD)
    pygame.draw.rect(SCREEN, (0, 0, 0), over_game)
    over_game_text = font.render("Congratulations!", False, (255, 255, 255))
    over_game_text_rect = over_game_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 45))
    SCREEN.blit(over_game_text, over_game_text_rect)
    if winner:
        won = font.render(" Team Right WON!", False, (255, 255, 255))
    else:
        won = font.render("Team Left WON!", False, (255, 255, 255))
    won_rect = won.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 45))
    SCREEN.blit(won, won_rect)
    restart = font.render("To reset game click R", False, (255, 255, 255))
    SCREEN.blit(restart, restart.get_rect())
    pygame.display.flip()


def change_player(team, player_in_control, events, marker):
    if player_in_control is not None:
        if player_in_control.bench:
            marker.change_player(team[0])
            return team[0]
        for event in events:
            if event.type == pygame.KEYUP and event.key == pygame.K_z:
                index = team.index(player_in_control)
                if index + 1 >= len(team):
                    player = team[0]
                else:
                    player = team[index+1]
                marker.change_player(player)
                return player

        return player_in_control
    else:
        return team[0]


def main():
    running = True
    clock = pygame.time.Clock()

    games_won_left = 0
    games_won_right = 0

    seed()
    team_left = []
    team_right = []
    bench_left = []
    bench_right = []
    chosen_team = team_left  # tu docelowo bedzie funkcja do wybierania ktora druzyna chcesz grac(#kiedyssieprzyda)

    all_players = pygame.sprite.Group()
    players_playing = pygame.sprite.Group()
    walls = pygame.sprite.Group()
    map_obstacles = pygame.sprite.Group()
    obstacles_player = pygame.sprite.Group()
    ball_obstacles = pygame.sprite.Group()
    ball_sprite = pygame.sprite.GroupSingle()
    cue_sprite = pygame.sprite.GroupSingle()

    ball = Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    cue = Cue(ball.rect.center)
    ball_sprite.add(ball)
    cue_sprite.add(cue)
    
    players_right_offensive_coords = [(3 * SCREEN_WIDTH / 4, SCREEN_HEIGHT / 4),
                                      (7 * SCREEN_WIDTH / 10, SCREEN_HEIGHT / 2),
                                      (3 * SCREEN_WIDTH / 4, 3 * SCREEN_HEIGHT / 4)]
    players_left_defensive_coords = [(SCREEN_WIDTH / 4, SCREEN_HEIGHT / 4),
                                     (SCREEN_WIDTH / 10, SCREEN_HEIGHT / 2),
                                     (SCREEN_WIDTH / 4, 3 * SCREEN_HEIGHT / 4)]
    players_right_defensive_coords = [(3 * SCREEN_WIDTH / 4, SCREEN_HEIGHT / 4),
                                      (9 * SCREEN_WIDTH / 10, SCREEN_HEIGHT / 2),
                                      (3 * SCREEN_WIDTH / 4, 3 * SCREEN_HEIGHT / 4)]
    players_left_offensive_coords = [(SCREEN_WIDTH / 4, SCREEN_HEIGHT / 4),
                                     (3 * SCREEN_WIDTH / 10, SCREEN_HEIGHT / 2),
                                     (SCREEN_WIDTH / 4, 3 * SCREEN_HEIGHT / 4)]

    middle_line = Midline(BORDERS_PARAMETER, SCREEN_HEIGHT, SCREEN_WIDTH // 2 - BORDERS_PARAMETER // 2, 0, BORDER_COLOR)
    team_right_line = Obstacle(BORDERS_PARAMETER, SCREEN_HEIGHT, SCREEN_WIDTH - BORDERS_PARAMETER, 0, BORDER_COLOR)
    team_left_line = Obstacle(BORDERS_PARAMETER, SCREEN_HEIGHT, 0, 0, BORDER_COLOR)
    up_line = Obstacle(SCREEN_WIDTH, BORDERS_PARAMETER, 0, 0, BORDER_COLOR)
    down_line = Obstacle(SCREEN_WIDTH, BORDERS_PARAMETER, 0, SCREEN_HEIGHT - BORDERS_PARAMETER, BORDER_COLOR)

    walls.add(team_left_line, team_right_line, up_line, down_line)

    player_in_control = None

    marker_sprite = pygame.sprite.GroupSingle()
    marker = None

    stage = PREPARATION

    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
                break

        if stage == MENU:
            pass
        if stage == PREPARATION:
            team_with_ball = randint(LEFT, RIGHT)
            if team_with_ball == RIGHT:
                for xy in players_right_offensive_coords:
                    team_right.append(Player(RIGHT, xy[0], xy[1],uniform(3,5)))
                for xy in players_left_defensive_coords:
                    team_left.append(Player(LEFT, xy[0], xy[1],uniform(3,5)))
            else:
                for xy in players_left_offensive_coords:
                    team_left.append(Player(LEFT, xy[0], xy[1],uniform(3,5)))
                for xy in players_right_defensive_coords:
                    team_right.append(Player(RIGHT, xy[0], xy[1],uniform(3,5)))

            all_players.add(team_right, team_left)
            players_playing.add(all_players)

            obstacles_player.add(walls, middle_line)

            generate_obstacles(obstacles_player, all_players, map_obstacles)
            obstacles_player.add(map_obstacles)
            ball_obstacles.add(map_obstacles, walls)

            ball.def_vel(6, 2)

            marker = Marker(chosen_team[0])
            marker_sprite.add(marker)

            stage = GAME

        elif stage == GAME:
            draw(walls, obstacles_player, all_players, ball_sprite, middle_line, marker_sprite)

            player_in_control = change_player(chosen_team, player_in_control, events, marker)
            player_in_control.move(obstacles_player, players_playing, marker)
            player_in_control.catch_ball(ball, events)

            ball.move(cue)
            ball.maintain_collision_obstacle(ball_obstacles)

            if ball.check_collision_player(players_playing):
                check_benched(players_playing, bench_left, bench_right, team_left, team_right)
            if not team_left or not team_right:
                stage = ENDGAME

            cue.update(SCREEN, ball)
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    ball.throw_a_ball(cue)

        elif stage == ENDGAME:
            if not team_left:
                endgame(RIGHT)
                games_won_right += 1
            if not team_right:
                endgame(LEFT)
                games_won_left += 1
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                team_left.clear()
                team_right.clear()
                bench_left.clear()
                bench_right.clear()

                all_players.empty()
                players_playing.empty()
                map_obstacles.empty()
                obstacles_player.empty()
                ball_obstacles.empty()
                stage = PREPARATION

        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()


if __name__ == '__main__':
    main()
