from utils import Constraint
from utils import Particle
from OpenGL.GL import *

from OpenGL.GLUT import *
from math import sqrt as sqrt
from math import atan2 as atan2

import time


class SnakePhysics:
    def __init__(self, particles, distance_constraints, time_delta):
        self.particles = particles
        self.distance_constraints = distance_constraints
        self.time_delta = time_delta

    def apply_physics(self, snake_direction):
        head_speed = 0.1
        friction = 0.94
        for index, particle in enumerate(self.particles):
            if index == 0:  # Apply direction movement to the head
                particle.px += snake_direction[0] * head_speed
                particle.py += snake_direction[1] * head_speed
            else:  # Apply friction to other particles
                particle.vx *= friction
                particle.vy *= friction
                particle.px = particle.x + particle.vx * self.time_delta
                particle.py = particle.y + particle.vy * self.time_delta

        self.resolve_collision_constraints()
        self.apply_distance_constraints()

        # Update positions and velocities
        for particle in self.particles:
            particle.vx = (particle.px - particle.x) / self.time_delta
            particle.vy = (particle.py - particle.y) / self.time_delta
            particle.x = particle.px
            particle.y = particle.py

        # Redraw the scene
        glutPostRedisplay()

    def apply_distance_constraints(self):
        i = 1
        while i < 4:
            # Apply distance constraints
            for constraint in self.distance_constraints:
                stiffness = 1 - (1 - constraint.stiffness) ** (1 / i)
                delta_x1, delta_y1, delta_x2, delta_y2 = self.distance_constraint(
                    self.particles[constraint.id1],
                    self.particles[constraint.id2],
                    constraint.distance,
                )
                self.particles[constraint.id1].px += stiffness * delta_x1
                self.particles[constraint.id1].py += stiffness * delta_y1
                self.particles[constraint.id2].px += stiffness * delta_x2
                self.particles[constraint.id2].py += stiffness * delta_y2
            i += 1

    def distance_constraint(
        self, particle1, particle2, constraint_distance, stiffness=0.8, damping=0.1
    ):
        current_distance = self.distance(
            particle1.x, particle1.y, particle2.x, particle2.y
        )

        difference = current_distance - constraint_distance

        if current_distance == 0:
            direction = (0, 0)
        else:
            direction = (
                (particle1.x - particle2.x) / current_distance,
                (particle1.y - particle2.y) / current_distance,
            )

        inv_mass1 = particle1.inv_mass
        inv_mass2 = particle2.inv_mass
        total_inv_mass = inv_mass1 + inv_mass2

        if total_inv_mass == 0:
            return (0.0, 0.0, 0.0, 0.0)

        correction_x1 = (
            -inv_mass1
            / total_inv_mass
            * difference
            * direction[0]
            * stiffness
            * (1 - damping)
        )
        correction_y1 = (
            -inv_mass1
            / total_inv_mass
            * difference
            * direction[1]
            * stiffness
            * (1 - damping)
        )
        correction_x2 = (
            inv_mass2
            / total_inv_mass
            * difference
            * direction[0]
            * stiffness
            * (1 - damping)
        )
        correction_y2 = (
            inv_mass2
            / total_inv_mass
            * difference
            * direction[1]
            * stiffness
            * (1 - damping)
        )

        return (correction_x1, correction_y1, correction_x2, correction_y2)

    def collision_constraint(self, particle1, particle2, damping=0.2):
        current_distance = self.distance(
            particle1.x, particle1.y, particle2.x, particle2.y
        )
        radii_sum = particle1.r + particle2.r

        # Check if the particles are overlapping
        if current_distance < radii_sum:
            overlap = radii_sum - current_distance

            # Normalize the direction vector between the two particles
            if current_distance == 0:
                direction = (1, 0)
            else:
                direction = (
                    (particle1.x - particle2.x) / current_distance,
                    (particle1.y - particle2.y) / current_distance,
                )

            # Calculate the mass coefficients based on inverse masses
            inv_mass1 = particle1.inv_mass
            inv_mass2 = particle2.inv_mass
            total_inv_mass = inv_mass1 + inv_mass2

            if total_inv_mass == 0:
                return (0.0, 0.0, 0.0, 0.0)

            # Calculate the correction for each particle based on their inverse mass
            correction = damping * overlap * (1 / total_inv_mass)
            correction_x1 = inv_mass1 * correction * direction[0]
            correction_y1 = inv_mass1 * correction * direction[1]
            correction_x2 = -inv_mass2 * correction * direction[0]
            correction_y2 = -inv_mass2 * correction * direction[1]

            return (correction_x1, correction_y1, correction_x2, correction_y2)
        else:
            return (0.0, 0.0, 0.0, 0.0)

    def resolve_collision_constraints(self):
        for p1 in self.particles:
            for p2 in self.particles:
                delta_x1, delta_y1, delta_x2, delta_y2 = self.collision_constraint(
                    p1, p2
                )
                self.collision_constraint(p1, p2)
                p1.px += delta_x1
                p1.py += delta_y1
                p2.px += delta_x2
                p2.py += delta_y2

    @staticmethod
    def distance(x1, y1, x2, y2):
        return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


class Snake:
    def __init__(
        self,
        projectile_manager,
        initial_length=5,
        screen_leftx=-5,
        screen_rightx=5,
        screen_topy=-5,
        screen_bottomy=5,
    ):
        self.deadFlag = False
        self.particle_radii = 0.1
        self.particle_distance = self.particle_radii * 2.5
        self.screen_topy = screen_topy
        self.particles = []
        self.snake_direction = [0, 0]  # [x, y]
        self.time_delta = 1 / 64.0
        self.distance_constraints = [
            Constraint(i, i + 1, self.particle_distance)
            for i in range(initial_length - 1)
        ]
        self.physics = SnakePhysics(
            self.particles, self.distance_constraints, self.time_delta
        )
        self.initialize_snake(initial_length)
        self.last_fire_time = time.time()
        self.bulllets = []
        self.fire_rate = 0.15  # One bullet every 1.75 seconds
        self.bullet_speed = 0.025
        self.projectile_manager = projectile_manager

    @property
    def getSize(self):
        return len(self.particles)

    @property
    def getHead(self):
        return self.particles[0]

    def initialize_snake(self, length):
        for i in range(length):
            x = i * self.particle_radii * 2.1
            y = self.screen_topy + 3 * self.particle_radii
            self.particles.append(Particle(x, y, self.particle_radii))

    def draw(self):
        self.draw_particles()
        self.draw_snake()

    def draw_snake(self):
        for i in range(len(self.particles) - 1):
            p1 = self.particles[i]
            p2 = self.particles[i + 1]

            # Calculate the direction from p1 to p2
            direction = (p2.x - p1.x, p2.y - p1.y)

            # Calculate the normal to this direction (to get the perpendicular vector)
            normal = (-direction[1], direction[0])

            # Normalize the normal vector
            length = sqrt(normal[0] ** 2 + normal[1] ** 2)
            if length != 0:
                normal = (normal[0] / length, normal[1] / length)

            # The half width of the rectangle
            half_width = self.particle_radii

            # Calculate the four corners of the rectangle
            corner1 = (p1.x + normal[0] * half_width, p1.y + normal[1] * half_width)
            corner2 = (p1.x - normal[0] * half_width, p1.y - normal[1] * half_width)
            corner3 = (p2.x - normal[0] * half_width, p2.y - normal[1] * half_width)
            corner4 = (p2.x + normal[0] * half_width, p2.y + normal[1] * half_width)

            # Draw the rectangle (quad)
            glBegin(GL_QUADS)
            glVertex2f(*corner1)
            glVertex2f(*corner2)
            glVertex2f(*corner3)
            glVertex2f(*corner4)
            glEnd()

    def draw_particles(self):
        glColor3f(1.0, 1.0, 1.0)
        for particle in self.particles:
            particle.draw()

    def move(self, direction):
        if direction == "up":
            self.snake_direction = [0, -0.25]
        elif direction == "down":
            self.snake_direction = [0, 0.25]
        elif direction == "left":
            self.snake_direction = [-0.25, 0]
        elif direction == "right":
            self.snake_direction = [0.25, 0]

    def check_self_collision(self):
        head = self.particles[0]
        for segment in self.particles[2:]:  # Check head against all other segments
            dist = SnakePhysics.distance(head.x, head.y, segment.x, segment.y)
            if dist < (head.r + segment.r):
                return True  # Collision detected
        return False  # No collision

    def check_food_collision(self, food_pos):
        head = self.particles[0]
        dist = SnakePhysics.distance(head.x, head.y, food_pos[0], food_pos[1])
        if dist < (head.r + self.particle_radii):
            return True  # Collision detected
        return False  # No collision

    def check_wall_collision(self):
        head = self.particles[0]
        if head.x < -5 or head.x > 5 or head.y < -5 or head.y > 5:
            return True
        return False

    def check_collision(self, x, y, r):
        for particle in self.particles:
            dist = SnakePhysics.distance(x, y, particle.x, particle.y)
            if dist < (r + particle.r):
                return True
        return False

    def grow(self):
        last_particle = self.particles[-1]
        new_particle = Particle(last_particle.x, last_particle.y, last_particle.r)
        self.particles.append(new_particle)

        new_constraint = Constraint(
            len(self.particles) - 2, len(self.particles) - 1, self.particle_distance
        )
        self.distance_constraints.append(new_constraint)

    def shrink(self, damage):
        snake_len = self.getSize
        if snake_len > 1 and snake_len > damage:
            for i in range(damage):
                self.particles.pop()
                self.distance_constraints.pop()
        elif snake_len <= damage:
            self.deadFlag = True

    def update(self):
        self.physics.apply_physics(self.snake_direction)
        if self.check_self_collision() or self.check_wall_collision():
            self.deadFlag = True

    def shoot(self, target_x, target_y):
        head = self.particles[0]
        direction_x = target_x - head.x
        direction_y = target_y - head.y

        # Calculate the angle to the target
        angle_to_target = atan2(direction_y, direction_x)

        # Fire a bullet if the cooldown has expired
        current_time = time.time()
        if current_time - self.last_fire_time >= self.fire_rate:
            self.last_fire_time = current_time
            self.projectile_manager.fire(
                head.x + direction_x * 0.1,
                head.y + direction_y * 0.1,
                angle_to_target,
                self.bullet_speed,
                size=0.1,
                color=(0, 0, 1),
                damage=1,
            )
