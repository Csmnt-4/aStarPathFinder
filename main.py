import numpy as np
import pygame
import random

from enemy import Enemy
from grid import TileGrid

# Constants
WIDTH, HEIGHT = 650, 700
GRID_SIZE = 20
TILE_SIZE = 20
TILE_OFFSET_X = 130
TILE_OFFSET_Y = 130

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)

# Initialize Pygame
pygame.init()

# Font
font = pygame.font.Font(None, 36)

# Labels
lives_label = font.render("Lives: 3", True, BLACK)
balance_label = font.render("Balance: 300", True, BLACK)
towers_label = font.render("Towers: 0", True, BLACK)

# Button dimensions
button_width, button_height = 150, 50

# Button colors
button_color = (100, 100, 255)
hover_color = (150, 150, 255)

# Button text
buy_tower_text = font.render("Buy Tower!", True, WHITE)
start_wave_text = font.render("New Enemy", True, WHITE)
restart_text = font.render("Restart", True, WHITE)

# Button positions
buy_tower_pos = (50, 600)
start_wave_pos = (250, 600)
restart_pos = (450, 600)

# Button rectangles
buy_tower_rect = pygame.Rect(buy_tower_pos[0], buy_tower_pos[1], button_width, button_height)
start_wave_rect = pygame.Rect(start_wave_pos[0], start_wave_pos[1], button_width, button_height)
restart_rect = pygame.Rect(restart_pos[0], restart_pos[1], button_width, button_height)


def get_clicked_tile(mouse_pos):
    x, y = mouse_pos
    tile_x = (x + TILE_OFFSET_X) // TILE_SIZE - 13
    tile_y = (y + TILE_OFFSET_Y) // TILE_SIZE - 13
    return tile_x, tile_y


def draw_grid(screen):
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            pygame.draw.rect(screen, GRAY,
                             (TILE_OFFSET_X + x * TILE_SIZE, TILE_OFFSET_Y + y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 1)


def update_grid(tile_grid, enemies):
    len(tile_grid.tiles)


def draw_tiles(screen, tile_grid):
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            pygame.draw.rect(screen, tile_grid.tiles[x][y].get_color(),
                             (TILE_OFFSET_X + x * TILE_SIZE, TILE_OFFSET_Y + y * TILE_SIZE, TILE_SIZE, TILE_SIZE))


def draw_enemies(screen, enemies):
    for enemy in enemies:
        pygame.draw.rect(screen, BLACK, (
            TILE_OFFSET_X + enemy.x * TILE_SIZE, TILE_OFFSET_Y + enemy.y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        FONT = pygame.font.Font(None, 24)  # Choose a font and size for the health text
        TEXT = FONT.render(str(enemy.health), True, WHITE)  # Render the health text
        RECT = TEXT.get_rect(center=(
            TILE_OFFSET_X + (enemy.x + 0.5) * TILE_SIZE,
            TILE_OFFSET_Y + (enemy.y + 0.5) * TILE_SIZE))  # Center the text
        screen.blit(TEXT, RECT)  # Draw the health text onto the screen


def draw_labels(screen):
    screen.blit(lives_label, (50, 50))
    screen.blit(balance_label, (250, 50))
    screen.blit(towers_label, (450, 50))

def game_over_message(screen):
    """
    Display a game over message on the screen.

    Args:
    - screen (pygame.Surface): The surface to draw the message on.
    """
    game_over_font = pygame.font.Font(None, 72)
    game_over_text = game_over_font.render("Game Over", True, BLACK)
    game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(game_over_text, game_over_rect)


def draw_button(screen, text, position, button_color, hover_color):
    rect = pygame.Rect(position[0], position[1], button_width, button_height)
    pygame.draw.rect(screen, button_color, rect)
    mouse_pos = pygame.mouse.get_pos()
    if rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, hover_color, rect)
    screen.blit(text, (position[0] + 10, position[1] + 10))


def buy_tower(balance, towers):
    global balance_label, towers_label
    balance = balance - 100
    towers = towers + 1
    balance_label = font.render(f"Balance: {balance}", True, BLACK)
    towers_label = font.render(f"Towers: {towers}", True, BLACK)
    return balance, towers


def start_wave(enemies, tile_grid):
    if tile_grid.base is not None:
        side = np.random.randint(0, 3)
        if side == 0:
            x = 0
            y = np.random.randint(0, 19)
        elif side == 1:
            x = np.random.randint(0, 19)
            y = 0
        elif side == 2:
            x = 19
            y = np.random.randint(0, 19)
        elif side == 3:
            x = np.random.randint(0, 19)
            y = 19

        enemy = Enemy(x, y, np.random.randint(2, 6), 1)
        enemy.path = enemy.find_path(tile_grid)
        enemies.append(enemy)
    return enemies


def restart():
    pass  # Implement restart logic


def hit_around_tower(screen, tower, enemies, balance):
    for y in range(-1, 2):
        for x in range(-1, 2):
            pygame.draw.rect(screen, WHITE,
                             (TILE_OFFSET_X + (tower[0] + x) * TILE_SIZE, TILE_OFFSET_Y + (tower[1] + y) * TILE_SIZE,
                              TILE_SIZE, TILE_SIZE))

    for enemy in enemies:
        if (tower[0] - 1 <= enemy.x <= tower[0] + 1) and (tower[1] - 1 <= enemy.y <= tower[1] + 1):
            print("hit")
            enemy.get_hit()
        if enemy.health == 0:
            balance += 20

    enemies = [enemy for enemy in enemies if enemy.health > 0]
    return enemies, balance


def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("B&WTD")

    lives = 3
    balance = 300
    towers = 1

    tile_grid = TileGrid(20, 20)
    enemies = []

    clock = pygame.time.Clock()
    running = True
    update_interval = 10  # milliseconds
    update_timer = 0

    hit_interval = 50  # milliseconds
    hit_timer = 0

    movement_interval = 75  # milliseconds
    movement_timer = 0

    while running:
        screen.fill(WHITE)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_pos = pygame.mouse.get_pos()
                    if buy_tower_rect.collidepoint(mouse_pos):
                        if balance >= 100:
                            balance, towers = buy_tower(balance, towers)
                    elif start_wave_rect.collidepoint(mouse_pos):
                        enemies = start_wave(enemies, tile_grid)
                    elif restart_rect.collidepoint(mouse_pos):
                        pygame.quit()
                    else:  # Set a base or a tower, if available
                        clicked_tile = get_clicked_tile(mouse_pos)
                        if 0 < clicked_tile[0] <= tile_grid.width and 0 < clicked_tile[1] <= tile_grid.height:
                            tile_grid.set_base_tower(clicked_tile[0], clicked_tile[1], towers)
                            if towers > 0:
                                towers -= 1
                                global balance_label, towers_label
                                balance_label = font.render(f"Balance: {balance}", True, BLACK)
                                towers_label = font.render(f"Towers: {towers}", True, BLACK)
                            print("Clicked tile:", clicked_tile)

        # Update
        update_timer += clock.get_rawtime()
        hit_timer += clock.get_rawtime()
        movement_timer += clock.get_rawtime()
        if lives > 0:
            # Draw
            draw_grid(screen)
            draw_tiles(screen, tile_grid)  # Placeholder
            draw_labels(screen)
            draw_button(screen, buy_tower_text, buy_tower_pos, button_color, hover_color)
            draw_button(screen, start_wave_text, start_wave_pos, button_color, hover_color)
            draw_button(screen, restart_text, restart_pos, button_color, hover_color)
            draw_enemies(screen, enemies)

            if enemies is None:
                enemies = []
            if update_timer >= update_interval:
                update_timer = 0
            if movement_timer >= movement_interval:
                for enemy in enemies:
                    enemy.update()
                    if (enemy.x == tile_grid.base[0] and enemy.y == tile_grid.base[1]) and lives > 0:
                        lives -= 1
                        global lives_label
                        lives_label = font.render(f"Lives: {lives}", True, BLACK)
                        enemies = [enemy for enemy in enemies if enemy.x != tile_grid.base[0] and enemy.y != tile_grid.base[1]]
                movement_timer = 0
            if hit_timer >= hit_interval:
                for tower in tile_grid.towers:
                    enemies, balance = hit_around_tower(screen, tower, enemies, balance)
                    balance_label = font.render(f"Balance: {balance}", True, BLACK)
                hit_timer = 0

            pygame.display.flip()
            clock.tick(30)
        else:
            game_over_message(screen)
            pygame.display.flip()
            pygame.time.wait(2000)  # Wait for 2 seconds before quitting the game
            running = False
    pygame.quit()


if __name__ == "__main__":
    main()
