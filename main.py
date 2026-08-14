# main.py
import pygame
import sys
from settings import *
from game_data import GameData
from game_logic import GameLogic
from ui import UI


class LunarDeliveryGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("🚀 Лунная доставка")
        self.clock = pygame.time.Clock()
        self.data = GameData()
        self.logic = GameLogic(self.data)
        self.ui = UI(self.screen, self.data)
        self.running = True
        self.message = ""
        self.message_timer = 0

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(60)
        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                result = self.ui.handle_click(event.pos)
                if result == "next_day":
                    self.advance_day()
                elif result == "rover_selected":
                    self.show_message(
                        f"✅ Выбран ровер: {self.data.rovers[self.ui.selected_rover]['name']}"
                    )
                elif result == "order_selected":
                    self.show_message(
                        f"✅ Выбран заказ: {self.data.orders[self.ui.selected_order]['title']}"
                    )
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.try_delivery()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False

    def try_delivery(self):
        if not self.ui.selected_rover or not self.ui.selected_order:
            self.show_message("❌ Сначала выбери ровер и заказ!")
            return
        rover_id = self.ui.selected_rover
        order_id = self.ui.selected_order
        success, message = self.logic.start_delivery_animation(rover_id, order_id)
        if success:
            self.show_message(f"🚀 {message}")
            self.ui.selected_rover = None
            self.ui.selected_order = None
        else:
            self.show_message(f"❌ {message}")

    def advance_day(self):
        result, message = self.logic.advance_day()
        self.show_message(f"📅 День {self.data.game_state['day']}")
        if result == "game_over":
            self.show_message(f"💀 {message}")
            self.running = False
        elif result == "victory":
            self.show_message(f"🏆 {message}")
            self.running = False

    def show_message(self, text):
        self.message = text
        self.message_timer = 180

    def update(self):
        self.logic.update_animations()
        if self.message_timer > 0:
            self.message_timer -= 1

    def render(self):
        self.ui.draw()
        if self.message_timer > 0 and self.message:
            # ---- ИСПРАВЛЕНИЕ: используем метод render_text из ui ----
            text_surf = self.ui.render_text(
                self.message, font=self.ui.font_medium, color=WHITE
            )
            # --------------------------------------------------------
            text_rect = text_surf.get_rect()
            bg_x = MAP_LEFT + 20
            bg_y = MAP_TOP + 40
            bg_width = text_rect.width + 40
            bg_height = text_rect.height + 20
            s = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
            s.fill((0, 0, 0, 180))
            self.screen.blit(s, (bg_x, bg_y))
            self.screen.blit(text_surf, (bg_x + 20, bg_y + 10))
        fps_text = self.ui.font_small.render(
            f"FPS: {int(self.clock.get_fps())}", True, WHITE
        )
        self.screen.blit(fps_text, (SCREEN_WIDTH - 100, 10))
        pygame.display.flip()


if __name__ == "__main__":
    game = LunarDeliveryGame()
    game.run()
