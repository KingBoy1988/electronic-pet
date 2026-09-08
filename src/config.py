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
    # 窗口 - 桌面宠物模式
    pet_size: int = 200           # 宠物显示尺寸
    window_title: str = "电子宠物 - Electronic Pet"

    # 宠物状态衰减（每秒衰减量）
    hunger_decay: float = 0.15       # 饥饿值衰减
    happiness_decay: float = 0.10    # 心情衰减
    energy_decay: float = 0.08       # 精力衰减（清醒时）
    energy_recover: float = 0.50     # 精力恢复（睡眠时）
    cleanliness_decay: float = 0.05  # 清洁度衰减

    # 状态范围
    max_stat: int = 100
    min_stat: int = 0

    # 交互效果
    feed_amount: float = 30.0        # 喂食增加的饥饿值
    play_amount: float = 25.0       # 玩耍增加的心情值
    play_energy_cost: float = 15.0  # 玩耍消耗的精力
    clean_amount: float = 40.0       # 清洁增加的清洁度
    pet_amount: float = 5.0         # 抚摸增加的心情值

    # 交互冷却时间（毫秒）
    feed_cooldown: int = 2000
    play_cooldown: int = 3000
    clean_cooldown: int = 2000
    pet_cooldown: int = 1000

    # 动画
    animation_interval: int = 200    # 动画帧间隔（毫秒）
    status_update_interval: int = 1000  # 状态更新间隔（毫秒）
    temp_state_duration: float = 2.0  # 临时状态持续时间（秒）
    singing_duration: float = 27.5   # 唱歌持续时间（秒）

    # 路径
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


# 全局配置实例
CONFIG = AppConfig()
