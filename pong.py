import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 900, 650
# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

# Define the paddle class
class Paddle(pygame.sprite.Sprite):
    def __init__(self, color, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()

    def move(self, y):
        self.rect.y = y
        if self.rect.y < 0:
            self.rect.y = 0
        elif self.rect.y > HEIGHT - self.rect.height:
            self.rect.y = HEIGHT - self.rect.height

# Define the ball class
class Ball(pygame.sprite.Sprite):
    def __init__(self, color, radius):
        super().__init__()
        self.image = pygame.Surface([radius * 2, radius * 2])
        self.image.fill(WHITE)
        self.image.set_colorkey(WHITE)
        pygame.draw.circle(self.image, color, (radius, radius), radius)
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH // 2
        self.rect.y = HEIGHT // 2
        self.velocity = [random.choice([-7, 7]), random.choice([-7, 7])]

    def move(self):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]

        # Collision with top and bottom edges
        if self.rect.y > HEIGHT - self.rect.height:
            self.rect.y = HEIGHT - self.rect.height
            self.velocity[1] = -self.velocity[1]
        elif self.rect.y < 0:
            self.rect.y = 0
            self.velocity[1] = -self.velocity[1]

        # Collision with right edges
        if self.rect.x > WIDTH - self.rect.width:
            self.rect.x = WIDTH - self.rect.width
            self.velocity[0] = -self.velocity[0]

# Define the button class
class Button(pygame.sprite.Sprite):
    def __init__(self, color, width, height, text):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        font = pygame.font.Font(None, 36)
        text_surface = font.render(text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        self.image.blit(text_surface, text_rect)

# Define the bricks class
class Brick(pygame.sprite.Sprite):
    def __init__(self, color, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.move_speed = 1  # Speed of movement

# Set up the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong")

# Load space background
background = pygame.image.load("7afb1dcd-849b-4c9a-9e9d-7625e328c5ac.JPG")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# Create paddles and ball
player_paddle = Paddle(WHITE, 10, 100)
ball = Ball(YELLOW, 10)

# Sprite group
all_sprites = pygame.sprite.Group()
all_sprites.add(player_paddle, ball)

# Create buttons
start_button = Button(BLACK, 200, 50, "Start")
start_button.rect.center = (WIDTH // 2, HEIGHT // 2 - 50)
exit_button = Button(BLACK, 200, 50, "Exit Game")
exit_button.rect.center = (WIDTH // 2, HEIGHT // 2 + 50)

button_sprites = pygame.sprite.Group()
button_sprites.add(start_button, exit_button)

# Font
font = pygame.font.Font(None, 36)

# Make a sound 
bounce_wall_sound = pygame.mixer.Sound('Hit wall.mp3')
bounce_paddle_sound = pygame.mixer.Sound('Hit paddle.mp3')
Game_over_sound = pygame.mixer.Sound('Game_over.mp3')
Checkpoint = pygame.mixer.Sound('10 points checkpoint.mp3')

# Function to generate random bricks
def generate_bricks():
    brick_sprites = pygame.sprite.Group()
    brick_width = 20
    brick_height = 40
    for i in range(14):
        brick = Brick(YELLOW, brick_width, brick_height)
        brick.rect.x = random.randint(600, 800)  # Randomize x position
        brick.rect.y = i * (brick_height + 7)
        brick_sprites.add(brick)
    all_sprites.add(brick_sprites)
    return brick_sprites

brick_sprites = generate_bricks()

# Game loop
clock = pygame.time.Clock()
running = True
brick_respawn_count = 0  # Count the number of times bricks are respawned

# Game variables
player_score = 0
game_over = False
ball_speed = 7
main_menu = True
paddle_collision_flag = False  # Flag to indicate paddle collision

# Game loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if main_menu:
                if start_button.rect.collidepoint(event.pos):
                    main_menu = False
                elif exit_button.rect.collidepoint(event.pos):
                    running = False

    if not main_menu:
        if not game_over:
            # Player control using mouse
            player_paddle.move(pygame.mouse.get_pos()[1])

            # Ball movement
            ball.move()

            # Collision detection
            if pygame.sprite.collide_rect(ball, player_paddle) and not paddle_collision_flag:
                ball.velocity[0] = -ball.velocity[0]
                player_score += 1
                ball_speed += 0.2
                pygame.mixer.Sound.play(bounce_paddle_sound)
                paddle_collision_flag = True  # Set collision flag

            # Reset collision flag if ball moves away from the paddle
            if not pygame.sprite.collide_rect(ball, player_paddle):
                paddle_collision_flag = False

            # Collision detection with bricks
            brick_collision = pygame.sprite.spritecollide(ball, brick_sprites, True)
            if brick_collision:
                ball.velocity[0] = -ball.velocity[0]
                player_score += 1
                ball_speed += 0.1
                pygame.mixer.Sound.play(bounce_wall_sound)

            # Check if game is over
            if ball.rect.x < 0:
                game_over = True

            # Set ball speed
            ball.velocity[0] = -ball_speed if ball.velocity[0] < 0 else ball_speed

            # Check if all bricks are destroyed
            if len(brick_sprites) == 0:
                brick_respawn_count += 1
                all_sprites.remove(brick_sprites)
                brick_sprites = generate_bricks()
                player_score += 10
                ball_speed += 1

            # Check if hits right wall
            if ball.rect.x > WIDTH - ball.rect.width:
                pygame.mixer.Sound.play(bounce_wall_sound)


    # Drawing
    screen.blit(background, (0, 0))  # Draw background
    all_sprites.draw(screen)

    if main_menu:
        button_sprites.draw(screen)

    # Display points
    score_text = font.render(f"Score: {player_score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    # Display "GAME OVER" message
    if game_over:
        game_over_text = font.render("GAME OVER", True, WHITE)
        pygame.mixer.Sound.play(Game_over_sound)
        screen.blit(game_over_text, (WIDTH // 2 - 100, HEIGHT // 2))

    pygame.display.flip()

    # Set the frame rate
    clock.tick(60)

pygame.quit()
sys.exit()




