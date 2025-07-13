from pygame import font, display, event, draw, KEYDOWN, K_RETURN, K_ESCAPE

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.font = font.Font(None, 74)
        self.title = self.font.render("Space Shooter", True, (255, 255, 255))
        self.start_text = self.font.render("Press Enter to Start", True, (255, 255, 255))
        self.quit_text = self.font.render("Press Esc to Quit", True, (255, 255, 255))
        self.running = True

    def display_menu(self):
        while self.running:
            for e in event.get():
                if e.type == KEYDOWN:
                    if e.key == K_RETURN:
                        return "start"
                    if e.key == K_ESCAPE:
                        self.running = False

            self.screen.fill((0, 0, 0))
            self.screen.blit(self.title, (self.screen.get_width() // 2 - self.title.get_width() // 2, 100))
            self.screen.blit(self.start_text, (self.screen.get_width() // 2 - self.start_text.get_width() // 2, 300))
            self.screen.blit(self.quit_text, (self.screen.get_width() // 2 - self.quit_text.get_width() // 2, 400))
            display.flip()