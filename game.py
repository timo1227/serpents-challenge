import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from snake import Snake
from food import Food
from enemy import EnemyManager
from projectile import ProjectileManager
from stats import game_stats
from math import floor as floor


class Game:
    def __init__(
        self,
        width=800,
        height=800,
        screen_leftx=-5,
        screen_rightx=5,
        screen_topy=-5,
        screen_bottomy=5,
    ):
        self.width = width
        self.height = height
        self.window = None
        self.leftx = screen_leftx
        self.rightx = screen_rightx
        self.topy = screen_topy
        self.bottomy = screen_bottomy
        self.projectile_manager = ProjectileManager(
            screen_leftx=self.leftx,
            screen_rightx=self.rightx,
            screen_topy=self.topy,
            screen_bottomy=self.bottomy,
        )
        self.snake = Snake(
            projectile_manager=self.projectile_manager,
            initial_length=3,
            screen_leftx=self.leftx,
            screen_rightx=self.rightx,
            screen_topy=self.topy,
            screen_bottomy=self.bottomy,
        )
        self.food = Food(
            screen_leftx=self.leftx,
            screen_rightx=self.rightx,
            screen_topy=self.topy,
            screen_bottomy=self.bottomy,
        )
        self.enemy_manager = EnemyManager(
            screen_leftx=self.leftx,
            screen_rightx=self.rightx,
            screen_topy=self.topy,
            screen_bottomy=self.bottomy,
            projectile_manager=self.projectile_manager,
        )
        self.initialize_game()

    def key_callback(self, window, key, scancode, action, mods):
        if action == glfw.PRESS:
            if key == glfw.KEY_ESCAPE:
                glfw.set_window_should_close(window, True)
            elif key == glfw.KEY_W or key == glfw.KEY_UP:
                self.snake.move("up")
            elif key == glfw.KEY_S or key == glfw.KEY_DOWN:
                self.snake.move("down")
            elif key == glfw.KEY_A or key == glfw.KEY_LEFT:
                self.snake.move("left")
            elif key == glfw.KEY_D or key == glfw.KEY_RIGHT:
                self.snake.move("right")

    def mouse_button_callback(self, window, button, action, mods):
        screen_x, screen_y = glfw.get_cursor_pos(window)
        game_x, game_y = self.convert_screen_to_game_coordinates(screen_x, screen_y)

        if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS:
            self.snake.shoot(game_x, game_y)

    def convert_screen_to_game_coordinates(self, screen_x, screen_y):
        game_x = (screen_x / self.width) * (self.rightx - self.leftx) + self.leftx
        game_y = (screen_y / self.height) * (self.bottomy - self.topy) + self.topy
        return game_x, game_y

    def initialize_game(self):
        # Initialize GLFW and other settings
        if not glfw.init():
            raise Exception("GLFW can't be initialized")

        # Create a windowed mode window and its OpenGL context
        self.window = glfw.create_window(
            self.width, self.height, "Serpent's Challenge", None, None
        )
        if not self.window:
            glfw.terminate()
            raise Exception("GLFW window can't be created")

        # Set the keyboard callback function
        glfw.set_key_callback(self.window, self.key_callback)

        # Set the mouse button callback function
        glfw.set_mouse_button_callback(self.window, self.mouse_button_callback)

        # Make the window's context current
        glfw.make_context_current(self.window)

        game_stats.start_timer()

        gluOrtho2D(self.leftx, self.rightx, self.bottomy, self.topy)

    def check_collisions(self):
        # Check for food collision
        if self.snake.check_food_collision(self.food.get_position):
            self.snake.grow()
            self.food.reset()

        # Check projectile collision
        self.projectile_manager.check_collisions(self.snake, self.enemy_manager)

    def update(self):
        # Update game time
        game_stats.update_time()

        # Update the snake's position
        self.snake.update()

        self.projectile_manager.update_projectiles()

        # Enemy Track Snake
        self.enemy_manager.update(self.snake)

        # Check for collisions
        self.check_collisions()

    def run(self):
        # Main game loop
        while not glfw.window_should_close(self.window) and not self.snake.deadFlag:
            # Render the game elements
            self.render()

            # Update the game elements
            self.update()

            # Swap front and back buffers
            glfw.swap_buffers(self.window)

            # Poll for and process events
            glfw.poll_events()

        self.terminate()

    def render(self):
        # Clear the screen
        glClear(GL_COLOR_BUFFER_BIT)

        # Draw the snake
        self.snake.draw()

        # Draw the food
        self.food.draw()

        # Draw the enemy
        self.enemy_manager.draw_enemies()

        # Draw the projectiles
        self.projectile_manager.draw_projectiles()

        # Flush OpenGL commands
        glFlush()

    def terminate(self):
        # Terminate GLFW
        print("Game Over!\n")
        print("Final Stats:")
        print("--------------------")
        print("Score: " + str(game_stats.get_score))
        print("Time Alive: " + str(floor(game_stats.get_time * 100) / 100))
        glfw.terminate()


# Main execution
if __name__ == "__main__":
    game = Game()
    game.run()
