import pygame
import os
import random
import time

pygame.init()
width, height = 700, 700
display = pygame.display.set_mode((width, height))
pygame.display.set_caption('Space Invaders - Saurabh Aherkar')

clock = pygame.time.Clock()

# Load Images
yellow_ship = pygame.image.load('yellow_ship.png')
white_ship = pygame.image.load('white_ship.png')
orange_ship = pygame.image.load('orange_ship.png')

# Main Player Ship
user_ship = pygame.image.load('user_ship.png')

# Load Laser
yellow_laser = pygame.image.load('yellow_laser.png')
white_laser = pygame.image.load('white_laser.png')
orange_laser = pygame.image.load('orange_laser.png')

# Main Player Laser
red_laser = pygame.image.load('red_laser.png')

# Background
bg = pygame.transform.scale(pygame.image.load('background.png'), (width, height))


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(height >= self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship:
    COOL_DOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cool_down()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(height):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cool_down(self):
        if self.cool_down_counter >= self.COOL_DOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x + 45, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = user_ship
        self.laser_img = red_laser
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cool_down()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(height):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.health_bar(window)

    def health_bar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health // self.max_health), 10))


class Enemy (Ship):
    color_map = {
        'yellow': (yellow_ship, yellow_laser),
        'white': (white_ship, white_laser),
        'orange': (orange_ship, orange_laser)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.color_map[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x + 45, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None


def main():
    run = True
    fps = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont('monospace', 25)
    lost_font = pygame.font.SysFont('monospace', 50)

    enemies = []
    wave_length = 5
    enemy_vel = 1

    lost = False
    lost_count = 0
    player_vel = 5
    laser_vel = 5

    player = Player(300, 600)

    def redraw_window():
        display.blit(bg, (0, 0))

        lives_label = main_font.render('Lives : {}'.format(lives), 1, (255, 255, 255))
        level_label = main_font.render('Levels : {}'.format(level), 1, (255, 255, 255))

        display.blit(lives_label, (10, 10))
        display.blit(level_label, (width - level_label.get_width () - 10, 10))

        for enemy in enemies:
            enemy.draw(display)

        if lost:
            lost_label = lost_font.render('You Lost!!', 1, (255, 255, 255))
            display.blit(lost_label, (width // 2 - lost_label.get_width() // 2, 350))

        player.draw(display)
        pygame.display.update()

    while run:
        clock.tick(fps)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count >= fps * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, width - 100), random.randrange(-1500, -100), random.choice(['yellow', 'white', 'orange']))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - player_vel > 0:
            player.x -= player_vel
        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < width:
            player.x += player_vel
        if keys[pygame.K_UP] and player.y - player_vel > 0:
            player.y -= player_vel
        if keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() + 15 < height:
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > height:
                lives -= 1
                enemies.remove(enemy)



        player.move_lasers(-laser_vel, enemies)


def main_menu():
    title_font = pygame.font.SysFont('monospace', 50)
    run = True
    while run:
        display.blit(bg, (0, 0))
        title_label = title_font.render('Press Mouse To Begin', 1, (255, 255, 255))
        display.blit(title_label, (width//2 - title_label.get_width()//2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()

    pygame.quit()


if __name__ == '__main__':
    main_menu()
