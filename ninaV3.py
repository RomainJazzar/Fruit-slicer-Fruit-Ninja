import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width = 1280
screen_height = 720
screen = pygame.display.set_mode((screen_width, screen_height))

# Load and scale background
background = pygame.image.load('images/fruit.jpg')
background = pygame.transform.scale(background, (screen_width, screen_height))

pygame.display.set_caption("FRUIT SLICER GAME")

# New image dimensions for all objects
new_width = 100
new_height = 100

# Colors
WHITE  = (255, 255, 255)
BLACK  = (0, 0, 0)
RED    = (255, 0, 0)
GREEN  = (0, 255, 0)
BLUE   = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
BROWN  = (165, 42, 42)
PINK   = (255, 192, 203)

# Fonts
FONT       = pygame.font.SysFont('Roboto', 50)
SMALL_FONT = pygame.font.SysFont('Roboto', 25)

# Sounds
son_tranche_fruit  = pygame.mixer.Sound('son/tranche_fruit.mp3')
son_tranche_glacon = pygame.mixer.Sound('son/tranche_glacon.mp3')
son_tranche_bombe  = pygame.mixer.Sound('son/tranche_bombe.mp3')

# Helper: load and resize images
def load_and_resize_image(file_name, width, height):
    image = pygame.image.load(file_name)
    return pygame.transform.scale(image, (width, height))

# === Slash effect image (adjust path/size as you see fit) ===
slash_image_original = load_and_resize_image("images/slash.png", 120, 120)

# Fruit images + slices
fruit_images = [
    load_and_resize_image("images/kiwi.png", new_width, new_height),
    load_and_resize_image("images/pomme.png", new_width, new_height),
    load_and_resize_image("images/orange.png", new_width, new_height)
]

fruit_slices = [
    [
        load_and_resize_image("images/kiwi-split1.png", new_width, new_height),
        load_and_resize_image("images/kiwi-split2.png", new_width, new_height)
    ],
    [
        load_and_resize_image("images/pomme-split1.png", new_width, new_height),
        load_and_resize_image("images/pomme-split2.png", new_width, new_height)
    ],
    [
        load_and_resize_image("images/orange-split1.png", new_width, new_height),
        load_and_resize_image("images/orange-split2.png", new_width, new_height)
    ]
]

# Ice & bomb images
ice_image  = load_and_resize_image("images/glacon.png", new_width, new_height)
bomb_image = load_and_resize_image("images/bombe.png", new_width, new_height)

# -------------------------------------------------------------------------
# CLASS: Fruit (or generic "object" in the game: fruit, ice, bomb, etc.)
# -------------------------------------------------------------------------
class Fruit:
    def __init__(self, image, slices, x, y, speed, letter=None, is_bomb=False, is_ice=False):
        self.image   = image
        self.slices  = slices   # list [slice1, slice2] for fruit; or duplicate images for ice/bomb
        self.x       = x
        self.y       = y
        self.speed   = speed
        self.letter  = letter
        self.sliced  = False
        self.is_bomb = is_bomb
        self.is_ice  = is_ice
        
        # For slice animation
        self.sliced_time = None
        self.slice_offset_left  = -40  # initial offset for left slice
        self.slice_offset_right =  40  # initial offset for right slice
        self.slice_vel_left  = -3  # horizontal velocity for left slice
        self.slice_vel_right =  3  # horizontal velocity for right slice
        self.slice_gravity   =  1  # how quickly slices fall
        self.slice_y_offset  =  0  # vertical offset for slices

    def draw(self, surface):
        """Draw either the whole object or the two slices if sliced."""
        if not self.sliced:
            # Draw the intact object
            surface.blit(self.image, (self.x, self.y))
            # If there's a letter, display it
            if self.letter:
                display_text(self.letter, FONT, WHITE,
                             self.x + new_width//2 - 20, 
                             self.y + new_height//2 - 20)
        else:
            # Draw slices with offsets
            # Left slice
            surface.blit(self.slices[0], 
                         (self.x + self.slice_offset_left, 
                          self.y + self.slice_y_offset))
            # Right slice
            surface.blit(self.slices[1], 
                         (self.x + self.slice_offset_right, 
                          self.y + self.slice_y_offset))

    def move(self, time_frozen=False):
        """Update position. If sliced, update slice offsets for a simple animation."""
        # If time is frozen, don't update y. (But we still animate sliced pieces.)
        if not time_frozen or self.sliced:
            self.y += self.speed
        
        if self.sliced:
            # Animate the separated slices horizontally + gravity
            self.slice_offset_left  += self.slice_vel_left
            self.slice_offset_right += self.slice_vel_right
            self.slice_y_offset    += self.slice_gravity

    def is_clicked(self, mouse_pos):
        """Check if the user clicked inside the object's rect or its slices."""
        fruit_rect = pygame.Rect(self.x, self.y, new_width, new_height)
        if self.sliced:
            # If already sliced, check the rects around the slices
            slice_rect1 = pygame.Rect(self.x + self.slice_offset_left, 
                                      self.y + self.slice_y_offset, 
                                      new_width, new_height)
            slice_rect2 = pygame.Rect(self.x + self.slice_offset_right, 
                                      self.y + self.slice_y_offset, 
                                      new_width, new_height)
            return slice_rect1.collidepoint(mouse_pos) or slice_rect2.collidepoint(mouse_pos)
        else:
            return fruit_rect.collidepoint(mouse_pos)

# -------------------------------------------------------------------------
# CLASS: SlashEffect
#  - A short-lived slash "sprite" displayed where a fruit is sliced
#  - Rotates randomly to give a slash look
# -------------------------------------------------------------------------
class SlashEffect:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.start_time = pygame.time.get_ticks()
        self.lifetime = 300  # 300 ms
        # Rotate slash image randomly for variety
        angle = random.randint(0, 360)
        self.image = pygame.transform.rotate(slash_image_original, angle)

    def draw(self, surface):
        surface.blit(self.image, (self.x - self.image.get_width()//2,
                                  self.y - self.image.get_height()//2))

    def is_expired(self):
        """Check if the slash effect's lifetime has ended."""
        return pygame.time.get_ticks() - self.start_time > self.lifetime

# -------------------------------------------------------------------------
# HELPER FUNCTIONS TO CREATE SPECIFIC OBJECT TYPES
# (We handle bombs/ice spawns separately for better control.)
# -------------------------------------------------------------------------
def create_fruit(objects):
    """Create a random fruit object with random letter."""
    x = random.randint(20, screen_width - new_width - 20)
    y = 0
    speed = random.uniform(1.0, 2.0)  # Adjust speed
    letter = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    
    index = random.randint(0, len(fruit_images) - 1)
    obj = Fruit(
        image   = fruit_images[index],
        slices  = fruit_slices[index],
        x       = x,
        y       = y,
        speed   = speed,
        letter  = letter,
        is_bomb = False,
        is_ice  = False
    )
    objects.append(obj)

def create_ice(objects):
    """Create an ice object (with random letter)."""
    x = random.randint(20, screen_width - new_width - 20)
    y = 0
    speed = random.uniform(1.0, 2.0)
    letter = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    
    obj = Fruit(
        image   = ice_image,
        slices  = [ice_image, ice_image],  # no real slice difference
        x       = x,
        y       = y,
        speed   = speed,
        letter  = letter,
        is_bomb = False,
        is_ice  = True
    )
    objects.append(obj)

def create_bomb(objects):
    """Create a bomb object (no letter)."""
    x = random.randint(20, screen_width - new_width - 20)
    y = 0
    speed = random.uniform(1.0, 2.0)
    
    obj = Fruit(
        image   = bomb_image,
        slices  = [bomb_image, bomb_image],  # no real slice difference
        x       = x,
        y       = y,
        speed   = speed,
        letter  = None,
        is_bomb = True,
        is_ice  = False
    )
    objects.append(obj)

# -------------------------------------------------------------------------
# DISPLAY TEXT
# -------------------------------------------------------------------------
def display_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))
    return pygame.Rect(x, y, img.get_width(), img.get_height())

# -------------------------------------------------------------------------
# MENU
# -------------------------------------------------------------------------
def afficher_menu():
    menu_running = True
    clock = pygame.time.Clock()
    
    while menu_running:
        screen.blit(background, (0, 0))  # Draw background

        display_text("Menu du jeu", FONT, BROWN, 540, 50)
        
        # Clickable rects
        play_rect = pygame.Rect(1280 // 2 - 100, 300, 200, 50)
        quit_rect = pygame.Rect(1280 // 2 - 100, 450, 200, 50)

        # Draw rects
        pygame.draw.rect(screen, BLACK, play_rect)
        pygame.draw.rect(screen, BLACK, quit_rect)

        # Text
        play_text = "1. Jouer"
        quit_text = "4. Quitter"

        play_text_surface = SMALL_FONT.render(play_text, True, GREEN)
        quit_text_surface = SMALL_FONT.render(quit_text, True, GREEN)

        # Center text inside rect
        play_text_rect = play_text_surface.get_rect(center=play_rect.center)
        quit_text_rect = quit_text_surface.get_rect(center=quit_rect.center)

        screen.blit(play_text_surface, play_text_rect)
        screen.blit(quit_text_surface, quit_text_rect)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return "quit"

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                if play_rect.collidepoint(mouse_pos):
                    return "play"
                elif quit_rect.collidepoint(mouse_pos):
                    pygame.quit()
                    return "quit"
        
        clock.tick(60)

# -------------------------------------------------------------------------
# GAME LOOP
# -------------------------------------------------------------------------
def game_loop():
    running = True
    clock = pygame.time.Clock()
    objects = []
    slash_effects = []  # store active slash effects

    score = 0
    strikes = 0  # how many fruits missed

    # Timers for object spawning
    fruit_creation_time = 0
    fruit_creation_interval = 1200  # spawn 1 fruit every 1.2 seconds

    ice_creation_time = 0
    ice_creation_interval = 8000  # spawn ice every 8 seconds

    bomb_creation_time = 0
    bomb_creation_interval = 15000  # spawn bomb every 15 seconds

    # Freeze logic
    time_frozen = False
    freeze_start_time = 0
    freeze_duration = 3000  # 3 seconds

    while running:
        screen.blit(background, (0, 0))

        current_time = pygame.time.get_ticks()

        # ----- EVENT HANDLING -----
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Return to menu or break
                return  # Goes back to main -> menu

            if event.type == pygame.KEYDOWN:
                key_pressed = pygame.key.name(event.key).upper()
                # Check if that letter matches an object
                for obj in objects:
                    if not obj.sliced and obj.letter == key_pressed:
                        slice_object(obj, slash_effects)
                        if obj.is_bomb:
                            return game_over_screen(score, strikes, bombed=True)
                        elif obj.is_ice:
                            # Trigger time freeze
                            time_frozen = True
                            freeze_start_time = current_time
                        else:
                            score += 1
                        break

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for obj in objects:
                    if not obj.sliced and obj.is_clicked(mouse_pos):
                        slice_object(obj, slash_effects)
                        if obj.is_bomb:
                            return game_over_screen(score, strikes, bombed=True)
                        elif obj.is_ice:
                            # Trigger time freeze
                            time_frozen = True
                            freeze_start_time = current_time
                        else:
                            score += 1
                        break

        # ----- TIME FREEZE LOGIC -----
        if time_frozen:
            # Check if freeze duration ended
            if current_time - freeze_start_time >= freeze_duration:
                time_frozen = False

        # ----- SPAWN LOGIC -----
        if not time_frozen:  # Only spawn new objects if time isn't frozen
            # Fruit spawn
            if current_time - fruit_creation_time >= fruit_creation_interval:
                create_fruit(objects)
                fruit_creation_time = current_time
            
            # Ice spawn
            if current_time - ice_creation_time >= ice_creation_interval:
                create_ice(objects)
                ice_creation_time = current_time
            
            # Bomb spawn
            if current_time - bomb_creation_time >= bomb_creation_interval:
                create_bomb(objects)
                bomb_creation_time = current_time

        # ----- UPDATE & DRAW OBJECTS -----
        to_remove = []
        for obj in objects:
            # Move objects normally, or keep them in place if time_frozen
            obj.move(time_frozen)

            obj.draw(screen)

            # If an object (fruit) has moved beyond screen => missed => +1 strike
            if obj.y > screen_height and not obj.sliced:
                strikes += 1
                to_remove.append(obj)
            
            # If sliced, remove after some time (e.g., 1 second) or if slices fell off-screen
            if obj.sliced:
                if obj.y + obj.slice_y_offset > screen_height:
                    to_remove.append(obj)
                else:
                    if obj.sliced_time and (current_time - obj.sliced_time) > 1000:  
                        # 1 second of slice "flying"
                        to_remove.append(obj)

        for rem in to_remove:
            if rem in objects:
                objects.remove(rem)

        # ----- UPDATE & DRAW SLASH EFFECTS -----
        expired_slashes = []
        for slash in slash_effects:
            if slash.is_expired():
                expired_slashes.append(slash)
            else:
                slash.draw(screen)

        for s in expired_slashes:
            if s in slash_effects:
                slash_effects.remove(s)

        # Check losing condition: 3 strikes
        if strikes >= 3:
            return game_over_screen(score, strikes, bombed=False)

        # Display score/strikes
        display_text(f"Score: {score}", FONT, WHITE, 10, 10)
        display_text(f"Strikes: {strikes}", FONT, WHITE, 10, 60)

        pygame.display.flip()
        clock.tick(60)

# -------------------------------------------------------------------------
# Slice object function: sets object to "sliced" state + plays correct sound
# Also spawns a slash effect at the object's center
# -------------------------------------------------------------------------
def slice_object(obj, slash_effects):
    obj.sliced = True
    obj.sliced_time = pygame.time.get_ticks()
    center_x = obj.x + new_width // 2
    center_y = obj.y + new_height // 2

    # Create a slash effect at the center of the fruit/bomb/ice
    slash_effects.append(SlashEffect(center_x, center_y))

    # Play appropriate sound
    if obj.is_ice:
        son_tranche_glacon.play()
    elif obj.is_bomb:
        son_tranche_bombe.play()
    else:
        son_tranche_fruit.play()

# -------------------------------------------------------------------------
# GAME OVER SCREEN (display info and return to menu)
# -------------------------------------------------------------------------
def game_over_screen(score, strikes, bombed=False):
    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks()
    duration = 3000  # 3 seconds
    
    while True:
        screen.blit(background, (0, 0))
        
        if bombed:
            display_text("Vous avez frappé une bombe! GAME OVER", FONT, RED, 300, screen_height // 2 - 50)
        else:
            display_text("Vous avez atteint 3 strikes! GAME OVER", FONT, RED, 300, screen_height // 2 - 50)

        display_text(f"Score Final: {score}", FONT, WHITE, 300, screen_height // 2 + 20)

        pygame.display.flip()

        if pygame.time.get_ticks() - start_time > duration:
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        clock.tick(60)

    # After showing game over, return to menu
    return

# -------------------------------------------------------------------------
# MAIN
# -------------------------------------------------------------------------
def main():
    while True:
        menu_choice = afficher_menu()
        
        if menu_choice == "play":
            game_loop()  # Go into the game
        elif menu_choice == "quit":
            pygame.quit()
            break

if __name__ == "__main__":
    main()
