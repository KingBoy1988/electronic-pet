"""
宠物数据模型 - 管理宠物的状态、属性和存档
"""

import json
import os
import time
from dataclasses import dataclass, field, asdict
from typing import Optional
from src.config import CONFIG, PetState


@dataclass
class Pet:
    """宠物数据模型"""
    name: str = "小可爱"
    level: int = 1
    exp: int = 0
    exp_max: int = 100

    # 核心状态 (0-100)
    hunger: float = 80.0       # 饱食度，越高越饱
    happiness: float = 80.0    # 心情值，越高越开心
    energy: float = 80.0       # 精力值，越高越有精神
    health: float = 100.0      # 健康值
    cleanliness: float = 90.0   # 清洁度

    # 当前状态
    current_state: str = PetState.IDLE.value

    # 存活
    is_alive: bool = True
    birth_time: float = field(default_factory=time.time)
    last_save_time: float = field(default_factory=time.time)

    @property
    def age_seconds(self) -> float:
        """宠物存活时间（秒）"""
        return time.time() - self.birth_time

    @property
    def age_display(self) -> str:
        """格式化的存活时间"""
        seconds = int(self.age_seconds)
        days, remainder = divmod(seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, _ = divmod(remainder, 60)
        if days > 0:
            return f"{days}天{hours}小时"
        elif hours > 0:
            return f"{hours}小时{minutes}分钟"
        else:
            return f"{minutes}分钟"

    def update_stats(self, delta_seconds: float):
        """根据经过的时间更新宠物状态"""
        if not self.is_alive:
            return

        # 饥饿衰减
        self.hunger = max(CONFIG.min_stat, self.hunger - CONFIG.hunger_decay * delta_seconds)

        # 清洁度衰减
        self.cleanliness = max(CONFIG.min_stat, self.cleanliness - CONFIG.cleanliness_decay * delta_seconds)

        if self.current_state == PetState.SLEEPING.value:
            # 睡眠时恢复精力
            self.energy = min(CONFIG.max_stat, self.energy + CONFIG.energy_recover * delta_seconds)
            # 睡眠时心情缓慢下降
            self.happiness = max(CONFIG.min_stat, self.happiness - CONFIG.happiness_decay * 0.3 * delta_seconds)
        else:
            # 清醒时精力衰减
            self.energy = max(CONFIG.min_stat, self.energy - CONFIG.energy_decay * delta_seconds)
            # 心情衰减
            self.happiness = max(CONFIG.min_stat, self.happiness - CONFIG.happiness_decay * delta_seconds)

        # 健康检查
        self._check_health(delta_seconds)

        # 自动状态切换
        self._auto_update_state()

    def _check_health(self, delta_seconds: float):
        """检查健康状态"""
        # 饥饿过低扣血
        if self.hunger < 10:
            self.health = max(CONFIG.min_stat, self.health - 0.5 * delta_seconds)
        # 清洁度过低扣血
        if self.cleanliness < 10:
            self.health = max(CONFIG.min_stat, self.health - 0.3 * delta_seconds)
        # 精力过低扣血
        if self.energy < 10:
            self.health = max(CONFIG.min_stat, self.health - 0.2 * delta_seconds)

        # 健康为0，宠物死亡
        if self.health <= 0:
            self.is_alive = False
            self.current_state = PetState.SICK.value

        # 自然恢复健康（其他状态良好时）
        if self.hunger > 60 and self.energy > 60 and self.cleanliness > 60:
            self.health = min(CONFIG.max_stat, self.health + 0.1 * delta_seconds)

    def _auto_update_state(self):
        """根据数值自动更新宠物状态"""
        if not self.is_alive:
            self.current_state = PetState.SICK.value
            return

        if self.current_state == PetState.SLEEPING.value:
            # 睡眠中不自动切换（由用户或精力满后切换）
            if self.energy >= 95:
                self.current_state = PetState.IDLE.value
            return

        if self.current_state in (PetState.EATING.value, PetState.PLAYING.value):
            return  # 交互中不自动切换

        # 根据状态判断
        if self.health < 30:
            self.current_state = PetState.SICK.value
        elif self.happiness < 30 or self.hunger < 30:
            self.current_state = PetState.SAD.value
        elif self.happiness > 80 and self.hunger > 60:
            self.current_state = PetState.HAPPY.value
        else:
            self.current_state = PetState.IDLE.value

    def feed(self):
        """喂食"""
        if not self.is_alive:
            return False
        self.hunger = min(CONFIG.max_stat, self.hunger + CONFIG.feed_amount)
        self.current_state = PetState.EATING.value
        self.add_exp(5)
        return True

    def play(self):
        """玩耍"""
        if not self.is_alive or self.energy < CONFIG.play_energy_cost:
            return False
        self.happiness = min(CONFIG.max_stat, self.happiness + CONFIG.play_amount)
        self.energy = max(CONFIG.min_stat, self.energy - CONFIG.play_energy_cost)
        self.hunger = max(CONFIG.min_stat, self.hunger - 5)
        self.current_state = PetState.PLAYING.value
        self.add_exp(10)
        return True

    def sleep(self):
        """睡眠"""
        if not self.is_alive:
            return False
        self.current_state = PetState.SLEEPING.value
        return True

    def wake_up(self):
        """唤醒"""
        if self.current_state == PetState.SLEEPING.value:
            self.current_state = PetState.IDLE.value

    def clean(self):
        """清洁"""
        if not self.is_alive:
            return False
        self.cleanliness = min(CONFIG.max_stat, self.cleanliness + CONFIG.clean_amount)
        self.add_exp(3)
        return True

    def pet(self):
        """抚摸"""
        if not self.is_alive:
            return False
        self.happiness = min(CONFIG.max_stat, self.happiness + CONFIG.pet_amount)
        self.add_exp(1)
        return True

    def add_exp(self, amount: int):
        """增加经验值"""
        self.exp += amount
        while self.exp >= self.exp_max:
            self.exp -= self.exp_max
            self.level += 1
            self.exp_max = int(self.exp_max * 1.2)
            # 升级恢复少量健康
            self.health = min(CONFIG.max_stat, self.health + 20)

    def get_summary(self) -> dict:
        """获取状态摘要"""
        return {
            "name": self.name,
            "level": self.level,
            "exp": f"{self.exp}/{self.exp_max}",
            "hunger": int(self.hunger),
            "happiness": int(self.happiness),
            "energy": int(self.energy),
            "health": int(self.health),
            "cleanliness": int(self.cleanliness),
            "state": self.current_state,
            "age": self.age_display,
            "alive": self.is_alive,
        }

    def save(self, path: Optional[str] = None):
        """保存宠物数据"""
        if path is None:
            os.makedirs(CONFIG.saves_dir, exist_ok=True)
            path = os.path.join(CONFIG.saves_dir, "pet_save.json")

        self.last_save_time = time.time()
        data = asdict(self)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, path: Optional[str] = None) -> "Pet":
        """加载宠物数据"""
        if path is None:
            path = os.path.join(CONFIG.saves_dir, "pet_save.json")

        if not os.path.exists(path):
            return cls()

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            pet = cls(**data)

            # 计算离线期间的状态变化
            offline_seconds = time.time() - pet.last_save_time
            if offline_seconds > 0 and pet.is_alive:
                # 离线时状态以较慢速度衰减
                offline_delta = min(offline_seconds, 86400)  # 最多计算24小时
                pet.update_stats(offline_delta)

            return pet
        except (json.JSONDecodeError, TypeError):
            return cls()
