class Score:
    def __init__(self):
        self.score = 0
        self.font = None  # Placeholder for font object
        self.position = (10, 10)  # Default position for score display

    def load_font(self, font_path, size):
        import pygame
        self.font = pygame.font.Font(font_path, size)

    def increase_score(self, amount):
        self.score += amount

    def reset_score(self):
        self.score = 0

    def draw(self, surface):
        if self.font:
            score_surface = self.font.render(f'Score: {self.score}', True, (255, 255, 255))
            surface.blit(score_surface, self.position)