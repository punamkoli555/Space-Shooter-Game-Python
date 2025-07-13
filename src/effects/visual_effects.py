from pygame import Surface, Color, draw
import random

class VisualEffects:
    def __init__(self, screen: Surface):
        self.screen = screen
        self.width, self.height = screen.get_size()

    def screen_shake(self, intensity: int, duration: int):
        original_x, original_y = self.screen.get_rect().topleft
        for _ in range(duration):
            shake_x = random.randint(-intensity, intensity)
            shake_y = random.randint(-intensity, intensity)
            self.screen.blit(self.screen, (shake_x, shake_y))
            self.screen.blit(self.screen, (original_x, original_y))

    def color_flash(self, color: Color, duration: int):
        overlay = Surface(self.screen.get_size())
        overlay.fill(color)
        for _ in range(duration):
            self.screen.blit(overlay, (0, 0))
            draw.rect(self.screen, (0, 0, 0), (0, 0, self.width, self.height), 0)

    def draw_ripple(self, center: tuple, radius: int, color: Color):
        for r in range(radius, 0, -1):
            draw.circle(self.screen, color, center, r, 1)

    def draw_explosion_effect(self, position: tuple):
        explosion_color = Color(255, 165, 0)  # Orange color for explosion
        self.draw_ripple(position, 50, explosion_color)
        self.draw_ripple(position, 40, explosion_color)
        self.draw_ripple(position, 30, explosion_color)