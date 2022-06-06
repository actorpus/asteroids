import pygame
from math import sin, cos, pi
import random


def dist(a, b, /):
    return ((a[0] - b[0]) ** 2 + (a[1]-b[1]) ** 2) ** 0.5


def collide(polygon, point):
    colisions = 0

    for _edge in range(len(polygon)):
        edge = polygon[_edge - 1], polygon[_edge]

        (ax, ay), (bx, by) = edge

        if ay == by or ax == bx:
            print("improper shape")

        else:
            m = (ax - bx) / (ay - by)

            intersection_x = (point[1] - ay) * m + ax
            intersection_y = (intersection_x - ax) * (1 / m) + ay

            max_dist = dist((ax, ay), (bx, by))

            if dist((ax, ay), (intersection_x, intersection_y)) <= max_dist and dist((bx, by), (intersection_x, intersection_y)) < max_dist and intersection_x > point[0]:

                # pygame.draw.circle(display, (0, 0, 255), (intersection_x, intersection_y), 4)
                colisions += 1

    return colisions % 2 == 1


if __name__ == '__main__':
    display = pygame.display.set_mode((512, 512))
    clock = pygame.time.Clock()
    running = True

    points = [
        (lambda d: (cos(x / 2) * d + 256, sin(x / 2) * d + 256))(random.randint(50, 150))
        for x in range(0, int(4 * pi), 1)
    ]
    x, y = 255, 255

    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE:
                    points = [
                        (lambda d: (cos(x / 2) * d + 256, sin(x / 2) * d + 256))(random.randint(50, 150))
                        for x in range(0, int(4 * pi), 1)
                    ]

        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]: y -= 1
        if keys[pygame.K_s]: y += 1
        if keys[pygame.K_a]: x -= 1
        if keys[pygame.K_d]: x += 1

        display.fill((0, 0, 0))

        pygame.draw.circle(display, (0, 255, 0), (x, y), 4)
        pygame.draw.line(display, (0, 50, 0), (x, y), (512, y))

        if collide(points, (x, y)):
            pygame.draw.polygon(display, (255, 0, 0), points)
        else:
            pygame.draw.polygon(display, (255, 0, 0), points, 1)

        pygame.display.update()
        clock.tick(60)
