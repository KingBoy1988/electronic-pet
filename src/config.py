"""
全局配置 - 窗口、宠物、状态衰减等参数
"""

import os
from dataclasses import dataclass, field
from enum import Enum


class PetState(Enum):
    """宠物状态枚举"""
    IDLE = "idle"
    EATING = "eating"
    SLEEPING = "sleeping"
    PLAYING = "playing"
    HAPPY = "happy"
    SAD = "sad"
    SICK = "sick"
    SINGING = "singing"


@dataclass
class AppConfig:
    """应用配置"""
    pet_size: int = 200
    window_title: str = "电子宠物 - Electronic Pet"
    hunger_decay: float = 0.15
    happiness_decay: float = 0.10
    energy_decay: float = 0.08
    energy_recover: float = 0.50
    cleanliness_decay: float = 0.05
    max_stat: int = 100
    min_stat: int = 0
    feed_amount: float = 30.0
    play_amount: float = 25.0
    play_energy_cost: float = 15.0
    clean_amount: float = 40.0
    pet_amount: float = 5.0
    feed_cooldown: int = 2000
    play_cooldown: int = 3000
    clean_cooldown: int = 2000
    pet_cooldown: int = 1000
    animation_interval: int = 200
    status_update_interval: int = 1000
    temp_state_duration: float = 2.0
    singing_duration: float = 27.5
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assets_dir: str = field(init=False)
    sprites_dir: str = field(init=False)
    sounds_dir: str = field(init=False)
    saves_dir: str = field(init=False)

    def __post_init__(self):
        self.assets_dir = os.path.join(self.base_dir, "assets")
        self.sprites_dir = os.path.join(self.assets_dir, "sprites")
        self.sounds_dir = os.path.join(self.assets_dir, "sounds")
        self.saves_dir = os.path.join(self.base_dir, "saves")


CONFIG = AppConfig()
