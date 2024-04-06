import pygame
import os
import random
from queue import PriorityQueue

pygame.init()

# Constantes Globais
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Carregando imagens
RUNNING = [pygame.image.load(os.path.join("Assets/Dino", "DinoRun1.png")),
           pygame.image.load(os.path.join("Assets/Dino", "DinoRun2.png"))]
JUMPING = pygame.image.load(os.path.join("Assets/Dino", "DinoJump.png"))
DUCKING = [pygame.image.load(os.path.join("Assets/Dino", "DinoDuck1.png")),
           pygame.image.load(os.path.join("Assets/Dino", "DinoDuck2.png"))]

SMALL_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus1.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus2.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus3.png"))]
LARGE_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus1.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus2.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus3.png"))]

BIRD = [pygame.image.load(os.path.join("Assets/Bird", "Bird1.png")),
        pygame.image.load(os.path.join("Assets/Bird", "Bird2.png"))]

CLOUD = pygame.image.load(os.path.join("Assets/Other", "Cloud.png"))

BG = pygame.image.load(os.path.join("Assets/Other", "Track.png"))

font = pygame.font.Font('freesansbold.ttf', 20)  # Definindo a fonte globalmente


class Dinosaur:
    X_POS = 80
    Y_POS = 310
    Y_POS_DUCK = 340
    JUMP_VEL = 8.5

    def __init__(self):
        self.duck_img = DUCKING
        self.run_img = RUNNING
        self.jump_img = JUMPING

        self.dino_duck = False
        self.dino_run = True
        self.dino_jump = False

        self.step_index = 0
        self.jump_vel = self.JUMP_VEL
        self.image = self.run_img[0]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS

    def update(self, obstacles):
        # Automaticamente pula se houver um obstáculo na frente
        closest_obstacle = None
        min_distance = float('inf')
        for obstacle in obstacles:
            distance = obstacle.rect.x - self.dino_rect.x
            if 0 < distance < min_distance:
                min_distance = distance
                closest_obstacle = obstacle

        if closest_obstacle:
            if closest_obstacle.rect.x < self.X_POS:
                self.jump()

    def duck(self):
        self.image = self.duck_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS_DUCK
        self.step_index += 1

    def run(self):
        self.image = self.run_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS
        self.step_index += 1

    def jump(self):
        self.image = self.jump_img
        if self.dino_jump:
            self.dino_rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8
        if self.jump_vel < - self.JUMP_VEL:
            self.dino_jump = False
            self.jump_vel = self.JUMP_VEL

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.dino_rect.x, self.dino_rect.y))


class Cloud:
    def __init__(self):
        self.x = SCREEN_WIDTH + random.randint(800, 1000)
        self.y = random.randint(50, 100)
        self.image = CLOUD
        self.width = self.image.get_width()

    def update(self):
        self.x -= game_speed
        if self.x < -self.width:
            self.x = SCREEN_WIDTH + random.randint(2500, 3000)
            self.y = random.randint(50, 100)

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.x, self.y))


class Obstacle:
    def __init__(self, image, type):
        self.image = image
        self.type = type
        self.rect = self.image[self.type].get_rect()
        self.rect.x = SCREEN_WIDTH

    def update(self):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            obstacles.pop()

    def draw(self, SCREEN):
        SCREEN.blit(self.image[self.type], self.rect)


class SmallCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 325


class LargeCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 300


class Bird(Obstacle):
    def __init__(self, image):
        self.type = 0
        super().__init__(image, self.type)
        self.rect.y = 250
        self.index = 0

    def draw(self, SCREEN):
        if self.index >= 9:
            self.index = 0
        SCREEN.blit(self.image[self.index // 5], self.rect)
        self.index += 1


class GameState:
    def __init__(self, dino_pos, obstacles):
        self.dino_pos = dino_pos
        self.obstacles = obstacles

    def successors(self):
        successors = []
        for obstacle in self.obstacles:
            new_dino_pos = obstacle.rect.x
            new_obstacles = self.obstacles.copy()
            new_obstacles.remove(obstacle)
            successors.append(GameState(new_dino_pos, new_obstacles))
        return successors

    def goal_test(self):
        return len(self.obstacles) == 0

    def cost(self, next_state):
        return next_state.dino_pos - self.dino_pos

    def heuristic(self):
        if len(self.obstacles) == 0:
            return 0
        else:
            return sum([obstacle.rect.x - self.dino_pos for obstacle in self.obstacles]) / len(self.obstacles)


def astar_search(initial_state):
    frontier = PriorityQueue()
    frontier.put(initial_state, 0)
    came_from = {}
    cost_so_far = {}
    came_from[initial_state] = None
    cost_so_far[initial_state] = 0

    while not frontier.empty():
        current_state = frontier.get()

        if current_state.goal_test():
            break

        for next_state in current_state.successors():
            new_cost = cost_so_far[current_state] + current_state.cost(next_state)
            if next_state not in cost_so_far or new_cost < cost_so_far[next_state]:
                cost_so_far[next_state] = new_cost
                priority = new_cost + next_state.heuristic()
                frontier.put(next_state, priority)
                came_from[next_state] = current_state

    return came_from


def main_game():
    global game_speed, x_pos_bg, y_pos_bg, points, obstacles
    run = True
    clock = pygame.time.Clock()
    player = Dinosaur()
    cloud = Cloud()
    game_speed = 20
    x_pos_bg = 0
    y_pos_bg = 380
    points = 0
    obstacles = []
    death_count = 0

    initial_dino_pos = 0
    initial_obstacles = []

    # Definindo o estado inicial do jogo
    initial_state = GameState(initial_dino_pos, initial_obstacles)

    # Chamando a função de busca A* para encontrar a sequência de ações ótima
    came_from = astar_search(initial_state)

    # Inicializando o estado atual com o estado inicial do jogo
    current_state = initial_state

    while current_state is not None:
        # Capturando os resultados da busca A*
        next_state = came_from[current_state]
        if next_state is None:
            break
        # Salvando a próxima ação para a reprodução ou análise posterior
        # Action.append(current_state.get_action_to(next_state))
        # Atualizando para o próximo estado
        current_state = next_state

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        SCREEN.fill((255, 255, 255))

        player.update(obstacles)  # Atualiza automaticamente o dinossauro

        player.draw(SCREEN)

        if len(obstacles) == 0:
            if random.randint(0, 2) == 0:
                obstacles.append(SmallCactus(SMALL_CACTUS))
            elif random.randint(0, 2) == 1:
                obstacles.append(LargeCactus(LARGE_CACTUS))
            elif random.randint(0, 2) == 2:
                obstacles.append(Bird(BIRD))

        for obstacle in obstacles:
            obstacle.draw(SCREEN)
            obstacle.update()
            if player.dino_rect.colliderect(obstacle.rect):
                pygame.time.delay(2000)
                death_count += 1
                # menu(death_count)

        cloud.draw(SCREEN)
        cloud.update()

        score()

        clock.tick(30)
        pygame.display.update()


def menu(death_count):
    global points
    run = True
    while run:
        SCREEN.fill((255, 255, 255))
        font = pygame.font.Font('freesansbold.ttf', 30)

        if death_count == 0:
            text = font.render("Pressione uma tecla para começar", True, (0, 0, 0))
        elif death_count > 0:
            text = font.render("Pressione uma tecla para reiniciar", True, (0, 0, 0))
            score = font.render("Sua Pontuação: " + str(points), True, (0, 0, 0))
            scoreRect = score.get_rect()
            scoreRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
            SCREEN.blit(score, scoreRect)
        textRect = text.get_rect()
        textRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        SCREEN.blit(text, textRect)
        SCREEN.blit(RUNNING[0], (SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2 - 140))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
            if event.type == pygame.KEYDOWN:
                main_game()


def score():
    global points, game_speed
    points += 1
    if points % 100 == 0:
        game_speed += 1

    text = font.render("Points: " + str(points), True, (0, 0, 0))
    textRect = text.get_rect()
    textRect.center = (1000, 40)
    SCREEN.blit(text, textRect)

    if points >= 5000:
        end_game()


def end_game():
    global points, obstacles
    run = False
    print("Game Over - You reached 5000 points!")
    print("Total points:", points)

    # Calcular a heurística uma última vez antes de exibir
    heuristics = []
    for obstacle in obstacles:
        heuristics.append(GameState(obstacle.rect.x, obstacles).heuristic())
    avg_heuristic = sum(heuristics) / len(heuristics)
    print("Average heuristic:", avg_heuristic)

    menu(death_count)


if __name__ == "__main__":
    menu(death_count=0)