import pygame
import pygame_blank
import asteroid_collision
from math import sin, cos, pi
import random


def generate_asteroid(size: int):
    return [
        (lambda d: (cos(x / size) * d, sin(x / size) * d))(random.randint(10 + 10 * size, 20 + 10 * size))
        for x in range(0, int(2 * pi * size), 1)
    ]


def draw_polygon_wrapped(screen, color, polygon, position):
    for edge in range(len(polygon)):
        a, b = polygon[edge - 1], polygon[edge]

        a_new, b_new = (a[0] + position[0], a[1] + position[1]), (b[0] + position[0], b[1] + position[1])

        pygame.draw.line(screen, color, a_new, b_new)

        if a_new[0] > SCREEN_SIZE[0] or b_new[0] > SCREEN_SIZE[0]:
            pygame.draw.line(screen, color, (a_new[0] - SCREEN_SIZE[0], a_new[1]), (b_new[0] - SCREEN_SIZE[0], b_new[1]))

        if a_new[0] < 0 or b_new[0] < 0:
            pygame.draw.line(screen, color, (a_new[0] + SCREEN_SIZE[0], a_new[1]), (b_new[0] + SCREEN_SIZE[0], b_new[1]))

        if a_new[1] > SCREEN_SIZE[1] or b_new[1] > SCREEN_SIZE[1]:
            pygame.draw.line(screen, color, (a_new[0], a_new[1] - SCREEN_SIZE[1]), (b_new[0], b_new[1] - SCREEN_SIZE[1]))

        if a_new[1] < 0 or b_new[1] < 0:
            pygame.draw.line(screen, color, (a_new[0], a_new[1] + SCREEN_SIZE[1]), (b_new[0], b_new[1] + SCREEN_SIZE[1]))


def polygon_offc(polygon, offc):
    return [(_[0] + offc[0], _[1] + offc[1]) for _ in polygon]


class Entity:
    def __init__(self, x, y, direction=None, speed=None):
        self.dir = random.random() * 2 * pi if direction is None else direction
        self.speed = 1 if speed is None else speed

        self.x, self.y = x, y

    @property
    def pos(self):
        return self.x, self.y

    def update_position(self, fd):
        self.x += cos(self.dir) * self.speed * fd * 300
        self.y += sin(self.dir) * self.speed * fd * 300

        self.x %= SCREEN_SIZE[0]
        self.y %= SCREEN_SIZE[1]


class Asteroid(Entity):
    def __init__(self, size, x, y, direction=None):
        super(Asteroid, self).__init__(x, y, direction=random.random() * 2 * pi if direction is None else direction, speed=1 / size)
        self.size = size
        self.polygon = generate_asteroid(size)

    def draw(self, screen):
        draw_polygon_wrapped(screen, (255, 255, 255), self.polygon, self.pos)


class Player(Entity):
    @property
    def polygon(self):
        return [
            (cos(self.dir) * 10, sin(self.dir) * 10),
            (cos(self.dir + 0.75 * pi) * 10, sin(self.dir + 0.75 * pi) * 10),
            (cos(self.dir + pi) * 5, sin(self.dir + pi) * 5),
            (cos(self.dir - 0.75 * pi) * 10, sin(self.dir - 0.75 * pi) * 10)
        ]

    def draw(self, screen):
        draw_polygon_wrapped(screen, (255, 255, 255), self.polygon, self.pos)


class Bullet(Entity):
    def draw(self, screen):
        draw_polygon_wrapped(screen, (255, 255, 255), CIRCLE, self.pos)


class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        pygame.joystick.init()

        self.display = pygame.display.set_mode(SCREEN_SIZE)
        pygame_blank.transparentify()

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(pygame.font.get_default_font(), 32)

        self.joystick_mode = False

        try:
            self.js = pygame.joystick.Joystick(0)
            self.js.get_axis(0)  # axis 1
            self.js.get_axis(1)  # axis 2
            self.js.get_button(7)  # fire
            self.joystick_mode = True

        except pygame.error:  # no joystick connected
            ...

        self.running = True
        self.bullet_cooldown = 0
        self._post_dead_timer = 0
        self.dead = False
        self.mode = 0
        self.difficulty = 0
        self.menu_state = 0

        self.asteroids = []  # handled in re_init()
        self.bullets = []

        self.player = Player(1000, 256, direction=-pi / 2, speed=0)

    def re_init(self):
        self.asteroids = [
            Asteroid(random.randint(1, [5, 7][self.difficulty >= 2]), cos(_ / ((self.difficulty + 1) * 3)) * 100, sin(_ / ((self.difficulty + 1) * 3)) * 100) for _ in range(0, int(2 * pi) * ((self.difficulty + 1) * 3), 1)
        ]

    def run(self):
        modes = [
            "normal",
            "mad ex"
        ]
        dificulties = [
            "hard",
            "harder",
            "hardly",
            "not"
        ]
        menu_drop_state = -50

        while self.running:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.running = False

                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        self.running = False

                    if self.menu_state == 0:
                        if e.key == pygame.K_1:
                            self.mode = (self.mode + 1) % len(modes)
                        if e.key == pygame.K_2:
                            self.difficulty = (self.difficulty + 1) % len(dificulties)
                        if e.key == pygame.K_3:
                            self.menu_state = 1

                            self.re_init()

            pygame_blank.fill_transparent(self.display)

            if self.menu_state == 0:
                pygame.draw.rect(self.display, (0, 0, 0), (100, menu_drop_state-20, 100, 50), border_radius=20)
                pygame.draw.rect(self.display, (255, 255, 255), (100, menu_drop_state-20, 100, 50), 1, border_radius=20)

                pygame.draw.rect(self.display, (0, 0, 0), (210, menu_drop_state-20, 100, 50), border_radius=20)
                pygame.draw.rect(self.display, (255, 255, 255), (210, menu_drop_state-20, 100, 50), 1, border_radius=20)

                pygame.draw.rect(self.display, (0, 0, 0), (320, menu_drop_state - 20, 100, 50), border_radius=20)
                pygame.draw.rect(self.display, (255, 255, 255), (320, menu_drop_state - 20, 100, 50), 1, border_radius=20)

                t = self.font.render(modes[self.mode], True, (255, 255, 255))
                self.display.blit(t, (150 - t.get_width() // 2, 2 + menu_drop_state))

                t = self.font.render(dificulties[self.difficulty], True, (255, 255, 255))
                self.display.blit(t, (260 - t.get_width() // 2, 2 + menu_drop_state))

                t = self.font.render("go!", True, (255, 255, 255))
                self.display.blit(t, (370 - t.get_width() // 2, 2 + menu_drop_state))

                if self.difficulty >= 2:
                    t = self.font.render("possible", True, (255, 255, 255))
                    self.display.blit(t, (480 - t.get_width() // 2, 2 + menu_drop_state))

                menu_drop_state = min(0, menu_drop_state + 1)

            elif self.menu_state == 1:
                if self.dead:
                    self._post_dead_timer += 1
                else:
                    self.update_all()

                if self._post_dead_timer > 50:  # about 2s after death
                    return

                for ast in self.asteroids:
                    ast.draw(self.display)

                for bullet in self.bullets:
                    bullet.draw(self.display)

                self.player.draw(self.display)

            pygame.display.update()
            self.clock.tick(60)

    def update_all(self):
        keys = pygame.key.get_pressed()

        # movement
        fps = self.clock.get_fps()
        frame_delta = 1 / (fps if fps != 0 else 30)

        # rotation_allowance = 5 * frame_delta * (1 / ((player.speed ** 2) + 1))
        rotation_allowance = frame_delta * 5

        if self.joystick_mode:
            self.player.dir += self.js.get_axis(0) * rotation_allowance

            throttle = - self.js.get_axis(1)

            if throttle > 0 or self.mode == NO_SLOW:
                self.player.speed = min(self.player.speed + (1 if self.mode == NO_SLOW else throttle) * frame_delta, 1)

            else:
                self.player.speed = max(self.player.speed - (max(throttle / 2, 0.1)) * frame_delta, 0)

        else:
            if keys[pygame.K_a]:
                self.player.dir -= rotation_allowance

            if keys[pygame.K_d]:
                self.player.dir += rotation_allowance

            if self.mode == NO_SLOW:
                self.player.speed = min(self.player.speed + 1 * frame_delta, 1)

            else:
                if keys[pygame.K_w]:
                    self.player.speed = min(self.player.speed + 1 * frame_delta, 1)

                else:
                    self.player.speed = max(self.player.speed - 0.1 * frame_delta, 0)

                if keys[pygame.K_s]:
                    self.player.speed = max(self.player.speed - 0.5 * frame_delta, 0)

        self.bullet_cooldown = max(self.bullet_cooldown - frame_delta * 5, 0)

        if (
                keys[pygame.K_SPACE] or
                (self.js.get_button(7) if self.joystick_mode else False)) \
                and self.bullet_cooldown == 0 and len(self.bullets) < 5 + self.difficulty:
            self.bullet_cooldown = 1

            self.bullets.append(Bullet(self.player.x, self.player.y, direction=self.player.dir, speed=1 + self.player.speed))

        for ast in self.asteroids:
            ast.update_position(frame_delta)

        for bullet in self.bullets:
            bullet.update_position(frame_delta)

        self.player.update_position(frame_delta)

        bad_bullets = []
        bad_asteroids = []

        # collisions
        for bullet in self.bullets:
            for asteroid in self.asteroids:
                if asteroid_collision.collide(polygon_offc(asteroid.polygon, asteroid.pos), bullet.pos):
                    bad_bullets.append(bullet)
                    bad_asteroids.append(asteroid)

        for bullet in bad_bullets:
            if bullet in self.bullets:
                self.bullets.remove(bullet)

        for asteroid in bad_asteroids:
            if asteroid in self.asteroids:
                self.asteroids.remove(asteroid)

                if asteroid.size > 1:
                    self.asteroids.append(Asteroid(asteroid.size - 1, asteroid.x, asteroid.y, direction=asteroid.dir + 3 * (random.random() - 0.5)))
                    self.asteroids.append(Asteroid(asteroid.size - 1, asteroid.x, asteroid.y, direction=asteroid.dir + 3 * (random.random() - 0.5)))

        for point in polygon_offc(self.player.polygon, self.player.pos) + \
                     polygon_offc(self.player.polygon, (self.player.pos[0] + SCREEN_SIZE[0], self.player.pos[1])) + \
                     polygon_offc(self.player.polygon, (self.player.pos[0] - SCREEN_SIZE[0], self.player.pos[1])) + \
                     polygon_offc(self.player.polygon, (self.player.pos[0], self.player.pos[1] + SCREEN_SIZE[1])) + \
                     polygon_offc(self.player.polygon, (self.player.pos[0], self.player.pos[1] - SCREEN_SIZE[1])):
            # only equates to 20 items so not to bad, should precompute polygon for optimisation

            for asteroid in self.asteroids:
                if asteroid_collision.collide(polygon_offc(asteroid.polygon, asteroid.pos), point):
                    self.dead = True
                    return


NORMAL = 0
NO_SLOW = 1


SCREEN_SIZE = 1920, 1080
CIRCLE = [(cos(_) * 2, sin(_) * 2) for _ in range(0, int(2 * pi), 1)]

game = Game()
game.run()
