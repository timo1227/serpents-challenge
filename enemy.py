from OpenGL.GL import *
import random
import math
import time
from stats import game_stats


class Enemy:
    def __init__(
        self,
        screen_leftx,
        screen_rightx,
        screen_topy,
        screen_bottomy,
        projectile_manager,
        size=0.45,
    ):
        self.screen_leftx = screen_leftx
        self.screen_rightx = screen_rightx
        self.screen_topy = screen_topy
        self.screen_bottomy = screen_bottomy
        self.size = size
        self.inPosition = False
        self.init_x, self.init_y = 0, self.screen_topy - (2 * self.size)
        self.x, self.y = self.generate_cords()
        self.last_fire_time = time.time()
        self.bulllets = []
        self.fire_rate = 1.75  # One bullet every 1.75 seconds
        self.bullet_speed = 0.025
        self.projectile_manager = projectile_manager

    def generate_cords(self):
        x = random.uniform(
            self.screen_leftx + self.size, self.screen_rightx - self.size
        )
        y = random.uniform(
            self.screen_topy + self.size, self.screen_bottomy - self.size
        )

        return x, y

    def update_position(self, speed=0.02):
        # Calculate the direction vector towards the target position
        direction_x = self.x - self.init_x
        direction_y = self.y - self.init_y
        distance = (direction_x**2 + direction_y**2) ** 0.5

        # Normalize the direction vector
        if distance != 0:
            direction_x /= distance
            direction_y /= distance

        # Update the position with the normalized direction vector and speed
        self.init_x += direction_x * speed
        self.init_y += direction_y * speed

        # Check if the ship has reached close to the target position
        if abs(self.init_x - self.x) < speed and abs(self.init_y - self.y) < speed:
            self.init_x, self.init_y = self.x, self.y  # Snap to the target position
            self.inPosition = True

    def draw(self):
        if self.inPosition:
            return

        # Draw the main body of the ship as a triangle
        glPushMatrix()
        glTranslatef(self.init_x, self.init_y, 0)
        glScalef(self.size, self.size, 1.0)

        glBegin(GL_TRIANGLES)
        glColor3f(1.0, 0.0, 0.0)  # Red color for the ship
        glVertex2f(-0.5, -0.5)  # Left vertex
        glVertex2f(0.5, -0.5)  # Right vertex
        glVertex2f(0.0, 0.5)  # Top vertex
        glEnd()

        # Draw a circle for the ship's cockpit
        glPopMatrix()

        self.update_position()

    def draw_ship(self):
        # Draw the main body of the ship as a triangle
        glPushMatrix()
        glScalef(self.size, self.size, 1.0)

        glBegin(GL_TRIANGLES)
        glColor3f(1.0, 0.0, 0.0)  # Red color for the ship
        glVertex2f(-0.5, -0.5)  # Left vertex
        glVertex2f(0.5, -0.5)  # Right vertex
        glVertex2f(0.0, 0.5)  # Top vertex (tip of the ship)
        glEnd()

        glPopMatrix()

    def track_target(self, snake_cords):
        if not self.inPosition:
            return

        target_x, target_y = snake_cords.x, snake_cords.y
        direction_x = target_x - self.x
        direction_y = target_y - self.y

        # Calculate the angle to the target
        angle_to_target = math.atan2(direction_y, direction_x)

        # Rotate the ship to face the target
        self.rotate_to_target(angle_to_target)

        # Fire a bullet if the cooldown has expired
        current_time = time.time()
        if current_time - self.last_fire_time >= self.fire_rate:
            self.last_fire_time = current_time
            self.projectile_manager.fire(
                self.x,
                self.y,
                angle_to_target,
                self.bullet_speed,
                size=0.1,
                color=(1, 0, 0),
                damage=1,
            )

    def rotate_to_target(self, angle):
        # Perform rotation to face the target angle
        glPushMatrix()

        # First, translate to the ship's position
        glTranslatef(self.x, self.y, 0)

        # Then, rotate around the Z-axis at the ship's position
        glRotatef(math.degrees(angle), 0, 0, 1)

        # Draw the ship here in the rotated orientation
        self.draw_ship()

        glPopMatrix()


class EnemyManager:
    def __init__(
        self,
        screen_leftx,
        screen_rightx,
        screen_topy,
        screen_bottomy,
        projectile_manager,
        max_enemies=3,
    ):
        self.enemies = []
        self.max_enemies = max_enemies
        self.screen_bounds = (screen_leftx, screen_rightx, screen_topy, screen_bottomy)
        self.projectile_manager = projectile_manager
        self.spawn_rate = 3  # Time in seconds to spawn a new enemy
        self.last_spawn_time = time.time()

    def update(self, snake):
        # Spawn new enemies if needed
        if (
            len(self.enemies) < self.max_enemies
            and time.time() - self.last_spawn_time > self.spawn_rate
        ):
            self.spawn_enemy()
            self.last_spawn_time = time.time()

        # Update existing enemies
        for enemy in self.enemies:
            enemy.update_position()
            enemy.track_target(snake.getHead)
            enemy.draw()

        # Check for collisions
        self.check_collision(snake)

    def spawn_enemy(self):
        new_enemy = Enemy(*self.screen_bounds, self.projectile_manager)
        self.enemies.append(new_enemy)

    def draw_enemies(self):
        for enemy in self.enemies:
            enemy.draw()

    def destroy_enemy(self, enemy):
        if enemy in self.enemies:
            self.enemies.remove(enemy)

    def check_collision(self, snake):
        for enemy in self.enemies:
            if enemy.inPosition:
                if snake.check_collision(enemy.x, enemy.y, enemy.size):
                    snake.shrink(2)
                    self.destroy_enemy(enemy)

                    snake_len = snake.getSize
                    if snake_len < 5:
                        game_stats.add_score(0.5)
                    elif snake_len < 7:
                        game_stats.add_score(1)
                    else:
                        game_stats.add_score(1.75)
