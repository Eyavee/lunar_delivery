# game_logic.py
import math
import random
from datetime import datetime
from settings import ANIMATION_SPEED, BASE_POSITION


class GameLogic:
    def __init__(self, game_data):
        self.data = game_data
        self.moving_rovers = {}

    def calculate_distance(self, pos1, pos2):
        x1, y1 = pos1
        x2, y2 = pos2
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def check_delivery_possible(self, rover_id, order_id):
        rover = self.data.rovers.get(rover_id)
        order = self.data.orders.get(order_id)
        if not rover or not order:
            return False, "Ровер или заказ не найден"
        if rover["status"] != "idle":
            return False, f"Ровер {rover['name']} занят"
        if order["status"] != "pending":
            return False, "Заказ уже выполняется или выполнен"
        if order["weight"] > rover["capacity"]:
            return (
                False,
                f"Слишком тяжело! Грузоподъемность: {rover['capacity']} ед., заказ весит {order['weight']} ед.",
            )
        distance = self.calculate_distance(rover["position"], order["position"])
        total_cost = (distance / 10) + (order["risk"] * 5) + (order["weight"] * 0.3)
        if total_cost > rover["battery"]:
            return (
                False,
                f"Не хватает батареи! Нужно: {total_cost:.1f} ед., есть: {rover['battery']} ед.",
            )
        if distance > 500 and order["risk"] > 1.0:
            return False, "Слишком опасно и далеко! Ровер не сможет вернуться."
        return True, f"Доставка возможна! Расход: {total_cost:.1f} ед."

    def start_delivery_animation(self, rover_id, order_id):
        rover = self.data.rovers.get(rover_id)
        order = self.data.orders.get(order_id)
        if not rover or not order:
            return False, "Ровер или заказ не найден"
        if rover["status"] != "idle":
            return False, f"Ровер {rover['name']} занят"
        if order["status"] != "pending":
            return False, "Заказ уже выполняется"
        possible, message = self.check_delivery_possible(rover_id, order_id)
        if not possible:
            return False, message

        rover["status"] = "busy"
        rover["is_moving"] = True
        rover["target_position"] = order["position"]
        rover["animation_progress"] = 0
        rover["has_cargo"] = False

        self.moving_rovers[rover_id] = {
            "order_id": order_id,
            "start_pos": rover["position"],
            "end_pos": order["position"],
            "stage": "to_order",
            "order_data": order.copy(),
        }
        order["assigned_rover"] = rover_id

        return True, f"Ровер {rover['name']} отправлен за заказом!"

    def update_animations(self):
        for rover_id, rover in self.data.rovers.items():
            if rover.get("is_moving", False) and rover.get("target_position"):
                current_x, current_y = rover["position"]
                target_x, target_y = rover["target_position"]
                dx = target_x - current_x
                dy = target_y - current_y
                distance = math.sqrt(dx**2 + dy**2)

                if distance < ANIMATION_SPEED:
                    rover["position"] = rover["target_position"]
                    rover["is_moving"] = False

                    if rover_id in self.moving_rovers:
                        stage = self.moving_rovers[rover_id]["stage"]
                        order_id = self.moving_rovers[rover_id]["order_id"]

                        if stage == "to_order":
                            order = self.data.orders.get(order_id)
                            if order:
                                order["status"] = "in_progress"
                                rover["has_cargo"] = True

                            rover["target_position"] = rover["start_position"]
                            rover["is_moving"] = True
                            self.moving_rovers[rover_id]["stage"] = "to_base"
                            self.moving_rovers[rover_id]["start_pos"] = rover[
                                "position"
                            ]
                        else:
                            self.complete_delivery(rover_id)
                else:
                    step_x = (dx / distance) * ANIMATION_SPEED
                    step_y = (dy / distance) * ANIMATION_SPEED
                    rover["position"] = (current_x + step_x, current_y + step_y)

                    if rover_id in self.moving_rovers:
                        start_pos = self.moving_rovers[rover_id]["start_pos"]
                        end_pos = rover["target_position"]
                        total_distance = self.calculate_distance(
                            rover["position"], start_pos
                        )
                        full_distance = self.calculate_distance(end_pos, start_pos)
                        rover["animation_progress"] = (
                            total_distance / full_distance if full_distance > 0 else 0
                        )

        # Удаляем заказы, которые были доставлены (в complete_delivery)
        # Здесь ничего не удаляем

    def complete_delivery(self, rover_id):
        rover = self.data.rovers.get(rover_id)
        if not rover or rover_id not in self.moving_rovers:
            return 0, 0

        move_data = self.moving_rovers[rover_id]
        order_id = move_data["order_id"]
        order = self.data.orders.get(order_id)

        if order is None:
            order = move_data.get("order_data")
            if order is None:
                return 0, 0

        reward, cost = self.execute_delivery_from_data(rover, order)

        if order_id in self.data.orders:
            del self.data.orders[order_id]

        rover["status"] = "idle"
        rover["is_moving"] = False
        rover["target_position"] = None
        rover["has_cargo"] = False
        rover["position"] = rover["start_position"]

        del self.moving_rovers[rover_id]

        return reward, cost

    def execute_delivery_from_data(self, rover, order):
        distance = self.calculate_distance(rover["position"], order["position"])
        total_cost = (distance / 10) + (order["risk"] * 5) + (order["weight"] * 0.3)

        rover["battery"] = max(0, rover["battery"] - total_cost)
        reward = order["reward"]

        if random.random() < order["risk"] * 0.3:
            reward = reward * 0.5
            rover["battery"] = max(0, rover["battery"] - 20)
            if rover["battery"] < 20:
                rover["status"] = "broken"

        self.data.game_state["money"] += reward
        self.data.game_state["rating"] = min(100, self.data.game_state["rating"] + 2)

        rover["deliveries_done"] += 1

        delivery_record = {
            "rover": rover["name"],
            "order": order["title"],
            "reward": reward,
            "battery_used": total_cost,
            "time": datetime.now(),
        }
        self.data.delivery_history.append(delivery_record)

        self.generate_new_order()

        return reward, total_cost

    def generate_new_order(self):
        import random
        from settings import (
            RISK_ZONES,
            MAP_LEFT,
            MAP_TOP,
            MAP_RIGHT,
            MAP_BOTTOM,
            BASE_POSITION,
        )

        weight = random.randint(2, 28)
        reward = int(weight * 4.5 + random.randint(-10, 20))
        urgency = random.randint(1, 5)
        risk = random.uniform(0.1, 1.0)

        base_x, base_y = BASE_POSITION
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(120, 400)
        x = base_x + distance * math.cos(angle)
        y = base_y + distance * math.sin(angle)
        x = max(MAP_LEFT + 50, min(MAP_RIGHT - 50, x))
        y = max(MAP_TOP + 50, min(MAP_BOTTOM - 50, y))

        risk_multiplier = 1.0
        for zone in RISK_ZONES:
            zx, zy, zw, zh, zr = zone
            if zx <= x <= zx + zw and zy <= y <= zy + zh:
                risk_multiplier = zr
                break

        order_id = f"order_{len(self.data.orders) + 1}"
        self.data.orders[order_id] = {
            "id": order_id,
            "title": f"Заказ #{len(self.data.orders) + 1}",
            "weight": weight,
            "reward": reward,
            "urgency": urgency,
            "risk": risk * risk_multiplier,
            "position": (int(x), int(y)),
            "status": "pending",
            "time_created": datetime.now(),
            "assigned_rover": None,
        }

    def advance_day(self):
        self.data.game_state["day"] += 1

        for rover in self.data.rovers.values():
            if rover["status"] != "broken":
                rover["battery"] = min(rover["max_battery"], rover["battery"] + 20)

        for order in self.data.orders.values():
            if order["status"] == "pending":
                if (datetime.now() - order["time_created"]).days >= 3:
                    order["status"] = "failed"
                    self.data.game_state["rating"] = max(
                        0, self.data.game_state["rating"] - 5
                    )

        if self.data.game_state["rating"] <= 0:
            return "game_over", "Рейтинг базы упал до нуля!"
        if self.data.game_state["day"] > self.data.game_state["days_to_survive"]:
            return (
                "victory",
                f"Вы продержались {self.data.game_state['days_to_survive']} дней!",
            )
        return "continue", ""
