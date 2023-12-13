class GameStats:
    def __init__(self):
        self.score = 0
        self.start_time = None
        self.elapsed_time = 0

    def start_timer(self):
        import time

        self.start_time = time.time()

    def update_time(self):
        import time

        if self.start_time is not None:
            self.elapsed_time = time.time() - self.start_time

    def add_score(self, points):
        self.score += points

    def reset(self):
        self.score = 0
        self.start_time = None
        self.elapsed_time = 0

    @property
    def get_score(self):
        return self.score

    @property
    def get_time(self):
        return self.elapsed_time


game_stats = GameStats()
