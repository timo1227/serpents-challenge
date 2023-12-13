import random
from utils import Particle


class Food:
    def __init__(
        self, screen_leftx, screen_rightx, screen_topy, screen_bottomy, food_size=0.12
    ):
        self.screen_leftx = screen_leftx
        self.screen_rightx = screen_rightx
        self.screen_topy = screen_topy
        self.screen_bottomy = screen_bottomy
        self.food_size = food_size
        self.food_particle = self.spawn_food()

    @property
    def get_position(self):
        return self.food_particle.x, self.food_particle.y

    def spawn_food(self):
        # Randomly place the food within the game boundaries
        x = random.uniform(
            self.screen_leftx + self.food_size, self.screen_rightx - self.food_size
        )
        y = random.uniform(
            self.screen_topy + self.food_size, self.screen_bottomy - self.food_size
        )
        return Particle(x, y, self.food_size)

    def draw(self):
        self.food_particle.draw()

    def reset(self):
        # Respawn the food at a new location
        self.food_particle = self.spawn_food()
