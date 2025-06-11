import pygame
import random
import sys

# Инициализация
pygame.init()

# Параметры экрана
cell_size = 40
maze_width = 15
maze_height = 15
screen_width = maze_width * cell_size
screen_height = maze_height * cell_size
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Лабиринт")

# Цвета
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
blue = (0, 0, 255)
green = (0, 255, 0)
yellow = (255, 255, 0)

# Игровые параметры
player_speed = 4
enemy_move_delays = [1000, 700, 500]  # мс между движением врагов по уровням
level_time_limits = [90, 60, 45]
max_levels = 3

# Шрифты
font = pygame.font.SysFont(None, 36)

# Сердце
heart_image = pygame.Surface((30, 30))
pygame.draw.polygon(heart_image, red, [(15, 5), (25, 15), (15, 28), (5, 15)])
heart_image.set_colorkey(black)

# Класс для игрока
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.lives = 3

    def draw(self):
        pygame.draw.circle(screen, red, (self.x * cell_size + cell_size // 2, self.y * cell_size + cell_size // 2), cell_size // 3)

    def move(self, dx, dy, maze):
        new_x = self.x + dx
        new_y = self.y + dy
        if can_move(maze, new_x, new_y):
            self.x = new_x
            self.y = new_y

# Класс для врагов
class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dx, self.dy = random.choice([(1,0), (-1,0), (0,1), (0,-1)])

    def draw(self):
        pygame.draw.circle(screen, yellow, (self.x * cell_size + cell_size // 2, self.y * cell_size + cell_size // 2), cell_size // 4)

    def move(self, maze):
        new_x = self.x + self.dx
        new_y = self.y + self.dy
        if can_move(maze, new_x, new_y):
            self.x = new_x
            self.y = new_y
        else:
            self.dx, self.dy = random.choice([(1,0), (-1,0), (0,1), (0,-1)])

# Генерация лабиринта
def generate_maze(w, h):
    maze = [[1 for _ in range(w)] for _ in range(h)]
    stack = []
    visited = [[False for _ in range(w)] for _ in range(h)]

    start_x, start_y = 0, 0
    stack.append((start_x, start_y))
    visited[start_y][start_x] = True
    maze[start_y][start_x] = 0

    dirs = [(-2, 0), (2, 0), (0, -2), (0, 2)]

    while stack:
        x, y = stack[-1]
        random.shuffle(dirs)
        moved = False
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and not visited[ny][nx]:
                maze[ny][nx] = 0
                maze[y + dy // 2][x + dx // 2] = 0
                visited[ny][nx] = True
                stack.append((nx, ny))
                moved = True
                break
        if not moved:
            stack.pop()

    # Добавляем случайные проходы (чтобы было больше ходов)
    extra_openings = (w * h) // 5  # 20% клеток

    for _ in range(extra_openings):
        x = random.randint(0, w - 1)
        y = random.randint(0, h - 1)
        maze[y][x] = 0

    return maze


def can_move(maze, x, y):
    if 0 <= x < maze_width and 0 <= y < maze_height:
        return maze[y][x] == 0
    return False

def draw_maze(maze):
    for y in range(maze_height):
        for x in range(maze_width):
            if maze[y][x] == 1:
                pygame.draw.rect(screen, blue, (x * cell_size, y * cell_size, cell_size, cell_size))

def draw_hearts(lives):
    for i in range(lives):
        screen.blit(heart_image, (10 + i*35, 10))

def button(rect, text):
    pygame.draw.rect(screen, green, rect)
    text_render = font.render(text, True, black)
    screen.blit(text_render, (rect.x + (rect.width - text_render.get_width()) // 2, rect.y + 10))

# Главное меню
def main_menu():
    while True:
        screen.fill(black)
        title = font.render("Выбери уровень:", True, white)
        screen.blit(title, (screen_width//2 - title.get_width()//2, 100))

        easy_button = pygame.Rect(screen_width//2 - 100, 200, 200, 50)
        medium_button = pygame.Rect(screen_width//2 - 100, 300, 200, 50)
        hard_button = pygame.Rect(screen_width//2 - 100, 400, 200, 50)

        button(easy_button, "Легкий")
        button(medium_button, "Средний")
        button(hard_button, "Тяжелый")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if easy_button.collidepoint(event.pos):
                    game_loop(1)
                elif medium_button.collidepoint(event.pos):
                    game_loop(2)
                elif hard_button.collidepoint(event.pos):
                    game_loop(3)

        pygame.display.update()

# Игровой цикл
def game_loop(level):
    maze = generate_maze(maze_width, maze_height)
    player = Player(0, 0)
    finish = (maze_width-1, maze_height-1)

    enemies = []
    for _ in range(level+1):
        while True:
            ex = random.randint(0, maze_width-1)
            ey = random.randint(0, maze_height-1)
            if maze[ey][ex] == 0 and (ex, ey) != (0,0) and (ex, ey) != finish:
                enemies.append(Enemy(ex, ey))
                break

    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks()
    last_enemy_move = pygame.time.get_ticks()
    game_over = False
    win = False

    while True:
        screen.fill(black)
        elapsed_time = (pygame.time.get_ticks() - start_time) // 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if not game_over:
            if keys[pygame.K_LEFT]:
                player.move(-1, 0, maze)
            if keys[pygame.K_RIGHT]:
                player.move(1, 0, maze)
            if keys[pygame.K_UP]:
                player.move(0, -1, maze)
            if keys[pygame.K_DOWN]:
                player.move(0, 1, maze)

            now = pygame.time.get_ticks()
            if now - last_enemy_move > enemy_move_delays[level-1]:
                for enemy in enemies:
                    enemy.move(maze)
                last_enemy_move = now

            for enemy in enemies:
                if player.x == enemy.x and player.y == enemy.y:
                    player.lives -= 1
                    if player.lives <= 0:
                        game_over = True

            if (player.x, player.y) == finish:
                win = True
                game_over = True

            if elapsed_time > level_time_limits[level-1]:
                game_over = True

        draw_maze(maze)
        pygame.draw.rect(screen, green, (finish[0]*cell_size, finish[1]*cell_size, cell_size, cell_size))
        player.draw()
        for enemy in enemies:
            enemy.draw()
        draw_hearts(player.lives)

        time_text = font.render(f"Time: {level_time_limits[level-1] - elapsed_time}s", True, white)
        screen.blit(time_text, (screen_width-200, 10))

        if game_over:
            msg = "Победа!" if win else "Проигрыш!"
            label = font.render(msg, True, white)
            screen.blit(label, (screen_width//2 - label.get_width()//2, screen_height//2 - 100))

            restart_button = pygame.Rect(screen_width//2 - 100, screen_height//2, 200, 50)
            button(restart_button, "Рестарт")

            if win and level < max_levels:
                next_button = pygame.Rect(screen_width//2 - 100, screen_height//2 + 70, 200, 50)
                button(next_button, "Следующий")
            else:
                next_button = None

            pygame.display.update()

            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if restart_button.collidepoint(event.pos):
                            game_loop(level)
                        if next_button and next_button.collidepoint(event.pos):
                            game_loop(level + 1)

                clock.tick(30)

        pygame.display.update()
        clock.tick(30)

main_menu()
