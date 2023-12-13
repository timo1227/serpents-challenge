from OpenGL.GL import *
import math

from stats import game_stats


class Projectile:
    def __init__(self, x, y, vx, vy, size, color, damage):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = size
        self.color = color
        self.damage = damage

    def update(self):
        self.x += self.vx
        self.y += self.vy

    def draw(self):
        glColor3f(*self.color)
        glBegin(GL_TRIANGLES)
        glVertex2f(self.x - self.size, self.y - self.size)
        glVertex2f(self.x + self.size, self.y - self.size)
        glVertex2f(self.x, self.y + self.size)
        glEnd()


class ProjectileManager:
    def __init__(self, screen_leftx, screen_rightx, screen_topy, screen_bottomy):
        self.projectiles = []
        self.screen_leftx = screen_leftx
        self.screen_rightx = screen_rightx
        self.screen_topy = screen_topy
        self.screen_bottomy = screen_bottomy

    def fire(self, x, y, angle, speed, size, color, damage):
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        projectile = Projectile(x, y, vx, vy, size, color, damage)
        self.projectiles.append(projectile)

    def update_projectiles(self):
        for projectile in self.projectiles:
            projectile.update()

    def draw_projectiles(self):
        for projectile in self.projectiles:
            projectile.draw()

    def check_collisions(self, snake, enemy_manager):
        remaining_projectiles = []
        for projectile in self.projectiles:
            # Check collision with world borders
            if not (
                self.screen_leftx <= projectile.x <= self.screen_rightx
                and self.screen_topy <= projectile.y <= self.screen_bottomy
            ):
                continue  # Skip projectiles that are outside the world borders

            # Check collision with the snake
            if self.is_colliding_with_snake(projectile, snake):
                if projectile.color == (1, 0, 0):  # Red projectile
                    snake.shrink(projectile.damage)
                remaining_projectiles.append(projectile)
                continue  # Skip projectiles that collided with the snake

            # Check collision with enemies
            collided_with_enemy = False
            for enemy in enemy_manager.enemies:
                if self.is_colliding_with_enemy(projectile, enemy):
                    if projectile.color == (0, 0, 1):  # Blue projectile
                        enemy_manager.destroy_enemy(enemy)  # Remove the enemy
                        snake_len = snake.getSize
                        if snake_len < 5:
                            game_stats.add_score(1)
                        elif snake_len < 7:
                            game_stats.add_score(2)
                        else:
                            game_stats.add_score(3)

                    collided_with_enemy = True
                    break

            if not collided_with_enemy and projectile.color == (0, 0, 1):
                remaining_projectiles.append(projectile)
            elif projectile.color == (1, 0, 0):
                remaining_projectiles.append(projectile)

        self.projectiles = remaining_projectiles

    def is_colliding_with_snake(self, projectile, snake):
        for segment in snake.particles:
            distance = math.sqrt(
                (segment.x - projectile.x) ** 2 + (segment.y - projectile.y) ** 2
            )
            if distance < (segment.r + projectile.size):
                return True
        return False

    def is_colliding_with_enemy(self, projectile, enemy):
        distance = math.sqrt(
            (enemy.x - projectile.x) ** 2 + (enemy.y - projectile.y) ** 2
        )
        if distance < (enemy.size + projectile.size):
            return True
        return False
