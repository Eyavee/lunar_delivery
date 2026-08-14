# game_data.py
import random
import math
from datetime import datetime, timedelta
from settings import (
    ROVER_POSITIONS,
    BASE_POSITION,
    RISK_ZONES,
    MAP_LEFT,
    MAP_TOP,
    MAP_RIGHT,
    MAP_BOTTOM,
)


class GameData:
    def __init__(self):
        self.game_state = {
            "day": 1,
            "money": 100,
            "rating": 100,
            "days_to_survive": 10,
        }

        self.rovers = {
            "rover_1": {
                "id": "rover_1",
                "name": "Кузя",
                "type": "medium",
                "battery": 150,
                "max_battery": 150,
                "capacity": 15,
                "status": "idle",
                "position": ROVER_POSITIONS[0],
                "start_position": ROVER_POSITIONS[0],
                "color": (100, 150, 255),
                "deliveries_done": 0,
                "is_moving": False,
                "target_position": None,
                "animation_progress": 0,
                "has_cargo": False,
            },
            "rover_2": {
                "id": "rover_2",
                "name": "Буран",
                "type": "heavy",
                "battery": 200,
                "max_battery": 200,
                "capacity": 30,
                "status": "idle",
                "position": ROVER_POSITIONS[1],
                "start_position": ROVER_POSITIONS[1],
                "color": (255, 180, 50),
                "deliveries_done": 0,
                "is_moving": False,
                "target_position": None,
                "animation_progress": 0,
                "has_cargo": False,
            },
            "rover_3": {
                "id": "rover_3",
                "name": "Спутник",
                "type": "light",
                "battery": 100,
                "max_battery": 100,
                "capacity": 5,
                "status": "idle",
                "position": ROVER_POSITIONS[2],
                "start_position": ROVER_POSITIONS[2],
                "color": (100, 200, 100),
                "deliveries_done": 0,
                "is_moving": False,
                "target_position": None,
                "animation_progress": 0,
                "has_cargo": False,
            },
        }

        self.orders = {}
        self.generate_initial_orders()
        self.delivery_history = []
        self.events = []
        self.orders_to_remove = []

    def generate_initial_orders(self):
        base_x, base_y = BASE_POSITION
        order_templates = [
            {"weight": 3, "reward": 20, "urgency": 1, "risk": 0.2},
            {"weight": 8, "reward": 40, "urgency": 2, "risk": 0.4},
            {"weight": 12, "reward": 60, "urgency": 3, "risk": 0.6},
            {"weight": 20, "reward": 90, "urgency": 4, "risk": 0.8},
            {"weight": 25, "reward": 110, "urgency": 5, "risk": 1.0},
            {"weight": 5, "reward": 30, "urgency": 2, "risk": 0.3},
            {"weight": 15, "reward": 70, "urgency": 3, "risk": 0.5},
            {"weight": 10, "reward": 50, "urgency": 4, "risk": 0.7},
        ]
        for i, template in enumerate(order_templates):
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
            order_id = f"order_{i+1}"
            self.orders[order_id] = {
                "id": order_id,
                "title": f"Заказ #{i+1}",
                "weight": template["weight"],
                "reward": template["reward"],
                "urgency": template["urgency"],
                "risk": template["risk"] * risk_multiplier,
                "position": (int(x), int(y)),
                "status": "pending",
                "time_created": datetime.now(),
                "time_deadline": datetime.now() + timedelta(days=random.randint(1, 5)),
                "assigned_rover": None,
            }
