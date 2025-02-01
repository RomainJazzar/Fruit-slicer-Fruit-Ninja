import pygame
import random

# Initialise Pygame
pygame.init()

# Définir les dimensions de la fenêtre
screen_width = 1280
screen_height = 720
screen = pygame.display.set_mode((screen_width, screen_height))
# Charger et redimensionner l'image de fond
background = pygame.image.load('images/fruit.jpg')
background = pygame.transform.scale(background, (screen_width, screen_height))

# Titre de la fenêtre :
pygame.display.set_caption("FRUIT SLICER GAME")

# Définir les nouvelles dimensions pour les images
new_width = 120
new_height = 120

# Chargement des sons
son_tranche_fruit = pygame.mixer.Sound('son/tranche_fruit.mp3')
son_tranche_glacon = pygame.mixer.Sound('son/tranche_glacon.mp3')
son_tranche_bombe = pygame.mixer.Sound('son/tranche_bombe.mp3')

# Fonction pour charger et redimensionner les images
def load_and_resize_image(file_name, width, height):
    image = pygame.image.load(file_name)
    return pygame.transform.scale(image, (width, height))

# Charger et redimensionner les images des fruits
fruit_images = [
    load_and_resize_image("images/banane.png", new_width, new_height),
    load_and_resize_image("images/cerise.png", new_width, new_height),
    load_and_resize_image("images/fraise.png", new_width, new_height),
    load_and_resize_image("images/kiwi.png", new_width, new_height),
    load_and_resize_image("images/pomme.png", new_width, new_height),
    load_and_resize_image("images/orange.png", new_width, new_height)
]

fruit_slices = [
    [load_and_resize_image("images/banane-split1.png", new_width, new_height),
     load_and_resize_image("images/banane-split2.png", new_width, new_height)],
    [load_and_resize_image("images/cerise-split1.png", new_width, new_height),
     load_and_resize_image("images/cerise-split2.png", new_width, new_height)],
    [load_and_resize_image("images/fraise-split1.png", new_width, new_height),
     load_and_resize_image("images/fraise-split2.png", new_width, new_height)],
    [load_and_resize_image("images/kiwi-split1.png", new_width, new_height),
     load_and_resize_image("images/kiwi-split2.png", new_width, new_height)],
    [load_and_resize_image("images/pomme-split1.png", new_width, new_height),
     load_and_resize_image("images/pomme-split2.png", new_width, new_height)],
    [load_and_resize_image("images/orange-split1.png", new_width, new_height),
     load_and_resize_image("images/orange-split2.png", new_width, new_height)]
]

# Images de la bombe et du glaçon
ice_image = load_and_resize_image("images/glacon.png", new_width, new_height)
bomb_image = load_and_resize_image("images/bombe.png", new_width, new_height)

# Tranches de la bombe (même image de la bombe pour l'exemple)
bomb_slices = [bomb_image, bomb_image]

# Tranches du glaçon (même image de glaçon)
ice_slices = [ice_image, ice_image]

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Initialiser la police
font = pygame.font.SysFont(None, 36)

# Classe pour le Fruit
class Fruit:
    def __init__(self, image, slices, x, y, speed):
        self.image = image
        self.slices = slices  # Les deux tranches
        self.x = x
        self.y = y
        self.speed = speed
        self.sliced = False  # Si le fruit a été tranché

    def draw(self):
        if self.sliced:
            # Si le fruit est tranché, afficher les deux tranches
            screen.blit(self.slices[0], (self.x - 90, self.y))  # Première tranche légèrement à gauche
            screen.blit(self.slices[1], (self.x + 90, self.y))  # Deuxième tranche légèrement à droite
        else:
            # Sinon, afficher l'image du fruit entier
            screen.blit(self.image, (self.x, self.y))

    def move(self):
        # Déplacer le fruit vers le bas
        self.y += self.speed

    def is_clicked(self, mouse_pos):
        # Vérifie si le fruit a été cliqué
        fruit_rect = pygame.Rect(self.x, self.y, new_width, new_height)
        if self.sliced:
            # Si le fruit est tranché, les tranches doivent être vérifiées
            slice_rect1 = pygame.Rect(self.x - 40, self.y, new_width, new_height)
            slice_rect2 = pygame.Rect(self.x + 40, self.y, new_width, new_height)
            return slice_rect1.collidepoint(mouse_pos) or slice_rect2.collidepoint(mouse_pos)
        else:
            return fruit_rect.collidepoint(mouse_pos)



# Fonction pour afficher le texte à l'écran
def display_text(text, x, y, size=36, color=(255, 0, 0)):
    font = pygame.font.SysFont(None, size)
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

# Fonction pour créer des objets (fruits, glaçon, bombe)
def create_object(objects):
    x = random.randint(20, screen_width - 20)
    y = 0
    speed = random.randint(1, 3)

    obj_type = random.choice(["fruit", "ice", "bomb"])
    if obj_type == "fruit":
        index = random.randint(0, len(fruit_images) - 1)
        obj = Fruit(fruit_images[index], fruit_slices[index], x, y, speed)
    elif obj_type == "ice":
        obj = Fruit(ice_image, ice_slices, x, y, speed)
    elif obj_type == "bomb":
        obj = Fruit(bomb_image, bomb_slices, x, y, speed)

    objects.append(obj)

# Fonction principale du jeu
def game_loop():
    running = True
    clock = pygame.time.Clock()
    objects = []
    score = 0
    strikes = 0
    pause_time = 0
    paused = False

    while running:
        screen.blit(background, (0, 0))  # Toujours redessiner l'arrière-plan

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break  # Sortir immédiatement de la boucle si la fenêtre est fermée
            if event.type == pygame.MOUSEBUTTONDOWN and not paused:
                mouse_pos = pygame.mouse.get_pos()

                for obj in objects:
                    if not obj.sliced and obj.is_clicked(mouse_pos):
                        obj.sliced = True
                        son_tranche_fruit.play()  # Ajouter un son lors du tranchage

                        if obj.image == ice_image:
                            paused = True
                            pause_time = pygame.time.get_ticks()  # Enregistrer l'heure actuelle pour la pause
                        elif obj.image == bomb_image:
                            running = False  # Arrêter le jeu si la bombe est touchée
                            display_text("Vous avez frappé une bombe ! Jeu terminé", screen_width // 2 - 350, screen_height // 2 - 50, 64, (255, 0, 0))
                            pygame.display.flip()  # Afficher le message avant de quitter
                            pygame.time.wait(3000)  # Attendre quelques secondes avant de quitter
                            break  # Quitter la boucle du jeu
                        else:
                            score += 1

                        # Retirer l'objet après un court délai pour afficher les tranches
                        pygame.time.set_timer(pygame.USEREVENT, 500)  # Timer pour la suppression après 500ms
                        break  # Sortir de la boucle après avoir traité un clic


        # Si le jeu est en pause
        if paused:
            if pygame.time.get_ticks() - pause_time >= 3000:  # 3 secondes de pause
                paused = False  # Reprendre le jeu

        if not paused:
            for obj in objects:
                obj.move()
                obj.draw()

                if obj.y > screen_height:
                    strikes += 1
                    objects.remove(obj)

            if random.randint(1, 20) == 1:
                create_object(objects)

            if strikes >= 3:
                running = False

        # Afficher le score et les strikes
        display_text(f"Score: {score}", 10, 10)
        display_text(f"Strikes: {strikes}", 10, 50)

        # Vérifier la fin du jeu
        if not running:
            if score >= 10:
                display_text("Vous avez gagné !", screen_width // 2 - 100, screen_height // 2 - 50, 64, (0, 255, 0))
            elif strikes >= 3:
                display_text("Jeu terminé !", screen_width // 2 - 100, screen_height // 2 - 50, 64, (255, 0, 0))

            pygame.display.flip()
            pygame.time.wait(3000)
            return False
        
        pygame.display.flip()
        clock.tick(30)

    return True

# Fonction pour démarrer le jeu
def main():
    while True:
        if not game_loop():
            break
    pygame.quit()

# Exécution du programme
if __name__ == "__main__":
    main()
