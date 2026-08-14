# ui.py
import pygame
import math
import random
import re
from settings import *


class UI:
    def __init__(self, screen, game_data):
        self.screen = screen
        self.data = game_data

        # Уменьшим шрифты, чтобы больше текста влезало в меню
        self.font_small = self.get_font("Arial", 18, fallback="Segoe UI")  # было 20
        self.font_medium = self.get_font("Arial", 22, fallback="Segoe UI")  # было 26
        self.font_large = self.get_font("Arial", 30, fallback="Segoe UI")  # было 36
        self.font_title = self.get_font("Arial", 40, fallback="Segoe UI")  # было 48

        # Загружаем шрифт с эмодзи (те же размеры)
        self.font_emoji_small = self.get_emoji_font(18) or self.font_small
        self.font_emoji_medium = self.get_emoji_font(22) or self.font_medium

        self.selected_rover = None
        self.selected_order = None
        self.buttons = {}
        self.create_buttons()

    def get_font(self, name, size, fallback=None):
        """Загружает шрифт по имени, если не получается – использует стандартный."""
        try:
            return pygame.font.SysFont(name, size)
        except:
            if fallback:
                try:
                    return pygame.font.SysFont(fallback, size)
                except:
                    pass
            return pygame.font.Font(None, size)

    def get_emoji_font(self, size):
        """Возвращает шрифт с поддержкой эмодзи или None."""
        candidates = [
            "Segoe UI Emoji",  # Windows
            "Apple Color Emoji",  # macOS
            "Noto Color Emoji",  # Linux
            "EmojiOne Color",
            "Symbola",
        ]
        for name in candidates:
            try:
                font = pygame.font.SysFont(name, size)
                test_surf = font.render("😊", True, (255, 255, 255))
                if test_surf.get_width() > 0:
                    return font
            except:
                continue
        return None

    def render_text(self, text, font=None, color=WHITE, use_emoji=True):
        """
        Рендерит текст, автоматически разбивая на части: обычный текст и эмодзи.
        Если use_emoji=True, то эмодзи рисуются шрифтом с эмодзи, иначе – основным.
        Возвращает поверхность с нарисованным текстом.
        """
        if not text:
            return pygame.Surface((0, 0), pygame.SRCALPHA)

        if font is None:
            font = self.font_medium

        # Если не нужно использовать эмодзи – просто рендерим основным шрифтом
        if not use_emoji:
            return font.render(text, True, color)

        # Регулярное выражение для поиска эмодзи (диапазон Unicode)
        # Берём все символы из блоков эмодзи (U+1F600–U+1F64F и т.д.) и простые смайлы типа ☀️⭐
        # Для упрощения будем искать любые символы вне ASCII (кроме кириллицы, её мы оставляем)
        # Это неидеально, но для наших целей подойдёт.
        # Проще: будем считать эмодзи все символы, которые не входят в базовый латинский и кириллицу.
        # Можно использовать более точное регулярное выражение, но для игры достаточно.
        # Определим функцию is_emoji(c):
        #   код >= 0x1F600 (Emoticons) или некоторые другие.
        # Возьмём упрощённый подход: ищем символы, которые не являются буквами/цифрами/пробелами/знаками препинания.
        # Но это может захватить иероглифы и др. – для нашей игры это не критично.

        # Вместо сложного парсинга, просто разделим строку на части, где встречаются символы эмодзи.
        # Для этого пройдём по строке и будем собирать группы.
        parts = []
        current_text = ""
        for char in text:
            # Проверяем, является ли символ эмодзи (по коду)
            if self.is_emoji(char):
                # Если есть накопленный текст – сохраняем его
                if current_text:
                    parts.append(("text", current_text))
                    current_text = ""
                parts.append(("emoji", char))
            else:
                current_text += char
        if current_text:
            parts.append(("text", current_text))

        # Теперь рендерим каждую часть и объединяем
        surfaces = []
        total_width = 0
        for kind, chunk in parts:
            if kind == "text":
                surf = font.render(chunk, True, color)
            else:  # emoji
                surf = self.font_emoji_small.render(chunk, True, color)
            surfaces.append(surf)
            total_width += surf.get_width()

        # Создаём итоговую поверхность
        result = pygame.Surface(
            (total_width, max(s.get_height() for s in surfaces)), pygame.SRCALPHA
        )
        x_offset = 0
        for surf in surfaces:
            result.blit(surf, (x_offset, 0))
            x_offset += surf.get_width()
        return result

    def is_emoji(self, char):
        """Проверяет, является ли символ эмодзи (по диапазонам Unicode)."""
        code = ord(char)
        # Основные диапазоны эмодзи
        if (
            (0x1F600 <= code <= 0x1F64F)
            or (0x1F300 <= code <= 0x1F5FF)
            or (0x1F680 <= code <= 0x1F6FF)
            or (0x1F700 <= code <= 0x1F77F)
            or (0x1F780 <= code <= 0x1F7FF)
            or (0x1F800 <= code <= 0x1F8FF)
            or (0x1F900 <= code <= 0x1F9FF)
            or (0x1FA00 <= code <= 0x1FA6F)
            or (0x1FA70 <= code <= 0x1FAFF)
            or (0x2600 <= code <= 0x26FF)
            or (0x2700 <= code <= 0x27BF)
            or (0x2300 <= code <= 0x23FF)
            or (0x2B50 <= code <= 0x2B55)
            or (0x203C <= code <= 0x3299)
        ):  # Other
            return True
        return False

    def create_buttons(self):
        self.buttons = {
            "next_day": pygame.Rect(MENU_LEFT + 20, 700, 160, 40),
        }

    def draw(self):
        self.screen.fill(DARK_GRAY)
        self.draw_menu()
        self.draw_map()
        self.draw_risk_zones()
        self.draw_orders()
        self.draw_rovers()
        self.draw_stats_on_map()
        self.draw_instructions()

    def draw_menu(self):
        pygame.draw.rect(self.screen, (30, 30, 40), (0, 0, MENU_WIDTH, SCREEN_HEIGHT))
        pygame.draw.rect(self.screen, GRAY, (0, 0, MENU_WIDTH, SCREEN_HEIGHT), 2)

        # Заголовок – сдвинем чуть вправо
        title_surf = self.render_text("🚀 ЛУНА", font=self.font_title, color=GOLD)
        self.screen.blit(title_surf, (MENU_LEFT + 40, 20))  # было 30

        title2_surf = self.render_text("ДОСТАВКА", font=self.font_medium, color=WHITE)
        self.screen.blit(title2_surf, (MENU_LEFT + 50, 60))  # было 40

        pygame.draw.line(
            self.screen, GRAY, (MENU_LEFT, 90), (MENU_LEFT + 220, 90), 2
        )  # ширина линии увеличена

        y = 110

        info = [
            f"День: {self.data.game_state['day']}/{self.data.game_state['days_to_survive']}",
            f"💰 ${self.data.game_state['money']}",
            f"⭐ Рейтинг: {self.data.game_state['rating']}/100",
        ]
        for line in info:
            surf = self.render_text(line, font=self.font_medium, color=WHITE)
            self.screen.blit(surf, (MENU_LEFT + 10, y))
            y += 28

        pygame.draw.line(
            self.screen, GRAY, (MENU_LEFT, y + 10), (MENU_LEFT + 180, y + 10), 2
        )
        y += 25

        header = self.render_text("📡 РОВЕРЫ", font=self.font_medium, color=SILVER)
        self.screen.blit(header, (MENU_LEFT + 10, y))
        y += 30

        for rover_id, rover in self.data.rovers.items():
            status_color = (
                GREEN
                if rover["status"] == "idle"
                else YELLOW if rover["status"] == "busy" else RED
            )
            status_text = (
                "🟢"
                if rover["status"] == "idle"
                else "🟡" if rover["status"] == "busy" else "🔴"
            )
            text = self.render_text(
                f"{status_text} {rover['name']}",
                font=self.font_small,
                color=status_color,
            )
            self.screen.blit(text, (MENU_LEFT + 10, y))

            batt_percent = rover["battery"] / rover["max_battery"]
            batt_color = (
                GREEN if batt_percent > 0.5 else ORANGE if batt_percent > 0.2 else RED
            )
            pygame.draw.rect(self.screen, DARK_GRAY, (MENU_LEFT + 100, y + 5, 80, 10))
            pygame.draw.rect(
                self.screen,
                batt_color,
                (MENU_LEFT + 100, y + 5, int(80 * batt_percent), 10),
            )

            if rover.get("has_cargo", False):
                cargo = self.render_text("📦", font=self.font_small, color=YELLOW)
                self.screen.blit(cargo, (MENU_LEFT + 185, y))
            y += 25

        pygame.draw.line(
            self.screen, GRAY, (MENU_LEFT, y + 10), (MENU_LEFT + 180, y + 10), 2
        )
        y += 25

        header2 = self.render_text("📦 ЗАКАЗЫ", font=self.font_medium, color=SILVER)
        self.screen.blit(header2, (MENU_LEFT + 10, y))
        y += 30

        pending_orders = [
            o for o in self.data.orders.values() if o["status"] == "pending"
        ]
        for order in pending_orders[:5]:
            urgency_color = (
                RED
                if order["urgency"] >= 4
                else ORANGE if order["urgency"] >= 3 else YELLOW
            )
            line = (
                f"#{order['id'].split('_')[1]} {order['weight']}кг 💰${order['reward']}"
            )
            surf = self.render_text(line, font=self.font_small, color=urgency_color)
            self.screen.blit(surf, (MENU_LEFT + 10, y))
            y += 22

        if len(pending_orders) > 5:
            more = self.render_text(
                f"...и еще {len(pending_orders) - 5}", font=self.font_small, color=GRAY
            )
            self.screen.blit(more, (MENU_LEFT + 10, y))
            y += 22

        button = self.buttons["next_day"]
        button.y = 700
        pygame.draw.rect(self.screen, DARK_BLUE, button)
        pygame.draw.rect(self.screen, GOLD, button, 2)
        btn_text = self.render_text("➡️ СЛЕД. ДЕНЬ", font=self.font_medium, color=WHITE)
        btn_rect = btn_text.get_rect(center=button.center)
        self.screen.blit(btn_text, btn_rect)

        y = 760
        tips = ["1. Кликни ровер", "2. Кликни заказ", "3. ПРОБЕЛ → доставка"]
        for tip in tips:
            surf = self.render_text(tip, font=self.font_small, color=LIGHT_GRAY)
            self.screen.blit(surf, (MENU_LEFT + 10, y))
            y += 18

    def draw_map(self):
        """Рисует карту Луны"""
        # Фон
        pygame.draw.rect(
            self.screen, LUNAR_GRAY, (MAP_LEFT, MAP_TOP, MAP_WIDTH, MAP_HEIGHT)
        )
        # Кратеры
        craters = [
            (MAP_LEFT + 150, MAP_TOP + 150, 60),
            (MAP_LEFT + 400, MAP_TOP + 200, 40),
            (MAP_LEFT + 850, MAP_TOP + 150, 80),
            (MAP_LEFT + 200, MAP_TOP + 500, 50),
            (MAP_LEFT + 900, MAP_TOP + 600, 70),
            (MAP_LEFT + 600, MAP_TOP + 650, 45),
            (MAP_LEFT + 300, MAP_TOP + 300, 35),
            (MAP_LEFT + 750, MAP_TOP + 400, 55),
        ]
        for x, y, r in craters:
            pygame.draw.circle(self.screen, CRATER_COLOR, (x, y), r)
            pygame.draw.circle(self.screen, DARK_GRAY, (x, y), r, 2)

    def draw_risk_zones(self):
        for zone in RISK_ZONES:
            x, y, w, h, risk = zone
            surface = pygame.Surface((w, h), pygame.SRCALPHA)
            surface.fill((255, 0, 0, 50))
            self.screen.blit(surface, (x, y))
            pygame.draw.rect(self.screen, RED, (x, y, w, h), 2)
            text = self.render_text(f"⚠️ Риск x{risk}", font=self.font_small, color=RED)
            self.screen.blit(text, (x + 10, y + 10))

    def draw_orders(self):
        for order_id, order in self.data.orders.items():
            if order["status"] != "pending":
                continue
            x, y = order["position"]

            if order["urgency"] >= 4:
                color = RED
            elif order["urgency"] >= 3:
                color = ORANGE
            else:
                color = YELLOW

            pulse = (
                abs(math.sin(pygame.time.get_ticks() / 500)) * 3
                if order["urgency"] >= 4
                else 0
            )
            pygame.draw.circle(self.screen, color, (x, y), 15 + pulse)
            pygame.draw.circle(self.screen, WHITE, (x, y), 15 + pulse, 2)

            # Иконка заказа
            icon = self.render_text("📦", font=self.font_small, color=WHITE)
            self.screen.blit(icon, (x - 8, y - 10))
            weight = self.render_text(
                f"{order['weight']}кг", font=self.font_small, color=WHITE
            )
            self.screen.blit(weight, (x - 12, y - 32))
            reward = self.render_text(
                f"${order['reward']}", font=self.font_small, color=GOLD
            )
            self.screen.blit(reward, (x - 12, y + 20))

            if self.selected_order == order_id:
                pygame.draw.circle(self.screen, GREEN, (x, y), 25, 3)
                details = [
                    f"Вес: {order['weight']}кг",
                    f"Награда: ${order['reward']}",
                    f"Риск: {order['risk']:.1f}x",
                    f"Срочность: {order['urgency']}/5",
                ]
                for i, line in enumerate(details):
                    surf = self.render_text(line, font=self.font_small, color=WHITE)
                    self.screen.blit(surf, (x + 30, y - 20 + i * 20))

    def draw_rovers(self):
        for rover_id, rover in self.data.rovers.items():
            x, y = rover["position"]
            if x < MAP_LEFT or x > MAP_RIGHT or y < MAP_TOP or y > MAP_BOTTOM:
                continue

            angle = 0
            if rover.get("is_moving", False) and rover.get("target_position"):
                target_x, target_y = rover["target_position"]
                dx = target_x - x
                dy = target_y - y
                angle = -math.degrees(math.atan2(dy, dx))

            color = rover["color"] if rover["status"] != "broken" else RED
            self.draw_rover_body(
                x + 4, y + 4, angle, ROVER_SHADOW, alpha=100, rover=rover
            )
            self.draw_rover_body(x, y, angle, color, rover=rover)

            name = self.render_text(rover["name"], font=self.font_small, color=WHITE)
            self.screen.blit(name, (x - 20, y - 50))
            self.draw_battery_indicator(x, y, rover)

            if rover.get("is_moving", False):
                self.draw_dust_effect(x, y, angle)

            if rover.get("is_moving", False):
                progress = rover.get("animation_progress", 0)
                bar_width = 40
                bar_height = 4
                bar_x = x - bar_width // 2
                bar_y = y + 25
                pygame.draw.rect(
                    self.screen, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height)
                )
                color_progress = (
                    GREEN if progress < 0.5 else ORANGE if progress < 0.8 else RED
                )
                pygame.draw.rect(
                    self.screen,
                    color_progress,
                    (bar_x, bar_y, int(bar_width * progress), bar_height),
                )

            # === ИЗМЕНЕНИЕ: информация о выбранном ровере теперь слева ===
            if self.selected_rover == rover_id:
                pygame.draw.circle(self.screen, GREEN, (x, y), 35, 3)
                details = [
                    f"Батарея: {rover['battery']:.0f}/{rover['max_battery']}",
                    f"Грузоподъемность: {rover['capacity']}кг",
                    f"Статус: {rover['status']}",
                    f"Доставок: {rover['deliveries_done']}",
                ]
                # Рендерим все строки и вычисляем максимальную ширину
                rendered_lines = []
                max_width = 0
                for line in details:
                    surf = self.render_text(line, font=self.font_small, color=WHITE)
                    rendered_lines.append(surf)
                    max_width = max(max_width, surf.get_width())

                # Определяем позицию: для "Кузя" слева, для остальных справа
                if rover["name"] == "Кузя":
                    # Слева от ровера с отступом 10 пикселей
                    block_x = x - max_width - 10
                    # Если вылезает за левую границу карты – прижимаем к краю
                    if block_x < MAP_LEFT + 5:
                        block_x = MAP_LEFT + 5
                else:
                    # Справа от ровера (как было раньше)
                    block_x = x + 40
                    # Чтобы не вылезало за правую границу (опционально)
                    if block_x + max_width > MAP_RIGHT - 5:
                        block_x = MAP_RIGHT - max_width - 5

                # Отрисовываем строки вертикально
                for i, surf in enumerate(rendered_lines):
                    self.screen.blit(surf, (block_x, y - 20 + i * 20))

    def draw_rover_body(self, x, y, angle, color, alpha=255, rover=None):
        rover_surface = pygame.Surface((60, 50), pygame.SRCALPHA)

        # Корпус
        body_rect = pygame.Rect(10, 15, 40, 20)
        pygame.draw.rect(rover_surface, color, body_rect, border_radius=6)
        pygame.draw.rect(rover_surface, WHITE, body_rect, 1, border_radius=6)

        # Солнечные батареи
        panel_color = (50, 150, 255)
        pygame.draw.rect(rover_surface, panel_color, (8, 8, 44, 8), border_radius=2)
        pygame.draw.rect(rover_surface, panel_color, (8, 34, 44, 8), border_radius=2)
        for i in range(3):
            pygame.draw.line(
                rover_surface, (30, 100, 200), (12 + i * 15, 8), (12 + i * 15, 16), 1
            )
            pygame.draw.line(
                rover_surface, (30, 100, 200), (12 + i * 15, 34), (12 + i * 15, 42), 1
            )

        # Камера
        pygame.draw.circle(rover_surface, (100, 100, 200), (30, 25), 8)
        pygame.draw.circle(rover_surface, (50, 50, 150), (30, 25), 5)
        pygame.draw.circle(rover_surface, (200, 200, 255), (28, 23), 2)

        # Антенна
        pygame.draw.line(rover_surface, ROVER_ANTENNA, (30, 15), (30, 0), 2)
        pygame.draw.circle(rover_surface, ROVER_ANTENNA, (30, 0), 4)
        pygame.draw.circle(rover_surface, RED, (30, 0), 2)

        # Колеса
        wheel_positions = [(6, 34), (16, 34), (26, 34), (34, 34), (44, 34), (54, 34)]
        for wx, wy in wheel_positions:
            pygame.draw.circle(rover_surface, ROVER_WHEEL, (wx, wy), 7)
            pygame.draw.circle(rover_surface, DARK_GRAY, (wx, wy), 5)
            pygame.draw.circle(rover_surface, LIGHT_GRAY, (wx, wy), 3)
            for i in range(4):
                sp_x = wx + int(3 * math.cos(i * math.pi / 2))
                sp_y = wy + int(3 * math.sin(i * math.pi / 2))
                pygame.draw.circle(rover_surface, GRAY, (sp_x, sp_y), 1)

        # Фары
        pygame.draw.circle(rover_surface, ROVER_LIGHT, (12, 18), 3)
        pygame.draw.circle(rover_surface, ROVER_LIGHT, (48, 18), 3)
        if angle != 0:
            pygame.draw.circle(rover_surface, (255, 255, 200, 50), (10, 18), 6)
            pygame.draw.circle(rover_surface, (255, 255, 200, 50), (50, 18), 6)

        # Груз (если есть)
        if rover and rover.get("has_cargo", False):
            pygame.draw.rect(rover_surface, ORANGE, (20, 10, 20, 15), border_radius=2)
            pygame.draw.rect(rover_surface, GOLD, (20, 10, 20, 15), 1, border_radius=2)
            cargo_surf = self.render_text("📦", font=self.font_small, color=WHITE)
            rover_surface.blit(cargo_surf, (22, 9))

        rotated = pygame.transform.rotate(rover_surface, angle)
        rotated_rect = rotated.get_rect(center=(x, y))
        if alpha < 255:
            rotated.set_alpha(alpha)
        self.screen.blit(rotated, rotated_rect)

    def draw_battery_indicator(self, x, y, rover):
        battery_percent = rover["battery"] / rover["max_battery"]
        batt_color = (
            GREEN if battery_percent > 0.5 else ORANGE if battery_percent > 0.2 else RED
        )
        pygame.draw.rect(self.screen, DARK_GRAY, (x - 20, y + 18, 40, 5))
        pygame.draw.rect(
            self.screen, batt_color, (x - 20, y + 18, int(40 * battery_percent), 5)
        )
        pygame.draw.rect(self.screen, WHITE, (x - 20, y + 18, 40, 5), 1)
        percent = self.render_text(
            f"{int(battery_percent * 100)}%", font=self.font_small, color=WHITE
        )
        self.screen.blit(percent, (x + 25, y + 13))

    def draw_dust_effect(self, x, y, angle):
        for _ in range(4):
            offset_x = -20 - random.randint(0, 15) * math.cos(math.radians(angle))
            offset_y = -20 - random.randint(0, 15) * math.sin(math.radians(angle))
            dust_x = x + offset_x * 0.3 + random.randint(-5, 5)
            dust_y = y + offset_y * 0.3 + random.randint(-5, 5)
            dust_size = random.randint(2, 6)
            dust_alpha = random.randint(50, 180)
            dust_surface = pygame.Surface(
                (dust_size * 2, dust_size * 2), pygame.SRCALPHA
            )
            pygame.draw.circle(
                dust_surface,
                (200, 200, 210, dust_alpha),
                (dust_size, dust_size),
                dust_size,
            )
            self.screen.blit(dust_surface, (dust_x - dust_size, dust_y - dust_size))

    def draw_base(self):
        x, y = BASE_POSITION
        pygame.draw.circle(self.screen, ROVER_SHADOW, (x + 5, y + 5), 40)

        base_rect = pygame.Rect(x - 35, y - 25, 70, 50)
        pygame.draw.rect(self.screen, DARK_BLUE, base_rect, border_radius=8)
        pygame.draw.rect(self.screen, BLUE, base_rect, 2, border_radius=8)

        pygame.draw.circle(self.screen, (100, 150, 255), (x, y - 25), 25)
        pygame.draw.circle(self.screen, WHITE, (x, y - 25), 25, 2)

        for i in range(-20, 21, 20):
            pygame.draw.line(
                self.screen, ROVER_ANTENNA, (x + i, y - 30), (x + i + 15, y - 55), 2
            )
            pygame.draw.circle(self.screen, RED, (x + i + 15, y - 55), 4)
            pygame.draw.circle(self.screen, ROVER_ANTENNA, (x + i + 15, y - 55), 2)

        base_text = self.render_text(
            "🌙 ЛУННАЯ БАЗА", font=self.font_medium, color=WHITE
        )
        self.screen.blit(base_text, (x - 70, y + 35))

    def draw_stats_on_map(self):
        self.draw_base()

        pending = sum(1 for o in self.data.orders.values() if o["status"] == "pending")
        text = self.render_text(
            f"Активных заказов: {pending}", font=self.font_small, color=WHITE
        )
        self.screen.blit(text, (MAP_LEFT + 10, MAP_TOP + 10))

        day_text = self.render_text(
            f"День {self.data.game_state['day']}", font=self.font_small, color=WHITE
        )
        self.screen.blit(day_text, (MAP_RIGHT - 120, MAP_TOP + 10))

    def draw_instructions(self):
        instr = self.render_text(
            "🎮 Выбери ровер → выбери заказ → ПРОБЕЛ для доставки",
            font=self.font_small,
            color=LIGHT_GRAY,
        )
        self.screen.blit(instr, (MAP_LEFT + 20, MAP_BOTTOM + 10))

        total = sum(r["deliveries_done"] for r in self.data.rovers.values())
        total_text = self.render_text(
            f"✅ Всего доставок: {total}", font=self.font_small, color=GREEN
        )
        self.screen.blit(total_text, (MAP_RIGHT - 180, MAP_BOTTOM + 10))

    def handle_click(self, pos):
        x, y = pos
        if self.buttons["next_day"].collidepoint(pos):
            return "next_day"

        for rover_id, rover in self.data.rovers.items():
            rx, ry = rover["position"]
            if abs(x - rx) < 30 and abs(y - ry) < 30:
                if rover["status"] == "idle":
                    self.selected_rover = rover_id
                    return "rover_selected"

        for order_id, order in self.data.orders.items():
            ox, oy = order["position"]
            if abs(x - ox) < 25 and abs(y - oy) < 25:
                if order["status"] == "pending":
                    self.selected_order = order_id
                    return "order_selected"

        return None
