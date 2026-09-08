"""
动画管理器 - 管理宠物精灵图和动画帧
"""

import os
from typing import Optional, Dict, List
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont, QPen
from PySide6.QtCore import Qt, QTimer, QSize
from src.config import CONFIG, PetState


class SpriteManager:
    """精灵图管理器 - 加载和管理宠物模型图片"""

    # 状态对应的文件名
    SPRITE_NAMES: Dict[str, str] = {
        PetState.IDLE.value: "idle.png",
        PetState.EATING.value: "eating.png",
        PetState.SLEEPING.value: "sleeping.png",
        PetState.PLAYING.value: "playing.png",
        PetState.HAPPY.value: "happy.png",
        PetState.SAD.value: "sad.png",
        PetState.SICK.value: "sick.png",
    }

    def __init__(self):
        self._sprites: Dict[str, QPixmap] = {}
        self._use_placeholder = True
        self._load_sprites()

    def _load_sprites(self):
        """加载所有精灵图"""
        loaded_count = 0
        for state, filename in self.SPRITE_NAMES.items():
            path = os.path.join(CONFIG.sprites_dir, filename)
            if os.path.exists(path):
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    self._sprites[state] = pixmap
                    loaded_count += 1

        if loaded_count > 0:
            self._use_placeholder = False
        else:
            self._use_placeholder = True

    def get_sprite(self, state: str) -> Optional[QPixmap]:
        """获取指定状态的精灵图"""
        if state in self._sprites:
            return self._sprites[state]
        # 默认返回 idle 或占位图
        if PetState.IDLE.value in self._sprites:
            return self._sprites[PetState.IDLE.value]
        return None

    @property
    def use_placeholder(self) -> bool:
        """是否使用占位图（无自定义素材时）"""
        return self._use_placeholder

    def reload(self):
        """重新加载精灵图"""
        self._sprites.clear()
        self._load_sprites()


class PlaceholderRenderer:
    """占位图渲染器 - 没有自定义图片时绘制宠物"""

    @staticmethod
    def draw(painter: QPainter, width: int, height: int, state: str):
        """绘制占位宠物"""
        # 根据状态选择颜色
        color_map = {
            PetState.IDLE.value: QColor(100, 180, 255),      # 浅蓝
            PetState.EATING.value: QColor(255, 180, 100),     # 橙色
            PetState.SLEEPING.value: QColor(150, 150, 200),  # 紫灰
            PetState.PLAYING.value: QColor(255, 200, 100),    # 金黄
            PetState.HAPPY.value: QColor(100, 220, 120),      # 绿色
            PetState.SAD.value: QColor(160, 160, 160),         # 灰色
            PetState.SICK.value: QColor(180, 100, 100),       # 暗红
        }

        body_color = color_map.get(state, QColor(100, 180, 255))

        cx, cy = width // 2, height // 2
        body_r = min(width, height) // 3

        # 绘制身体（圆形）
        painter.setBrush(body_color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(cx - body_r, cy - body_r, body_r * 2, body_r * 2)

        # 绘制耳朵（小三角）
        ear_size = body_r // 2
        painter.setBrush(body_color.darker(120))
        # 左耳
        painter.drawEllipse(cx - body_r + 5, cy - body_r - ear_size // 2, ear_size, ear_size)
        # 右耳
        painter.drawEllipse(cx + body_r - ear_size - 5, cy - body_r - ear_size // 2, ear_size, ear_size)

        # 眼睛
        eye_size = body_r // 4
        eye_offset = body_r // 3
        painter.setBrush(QColor(40, 40, 40))

        if state == PetState.SLEEPING.value:
            # 闭眼 - 画弧线
            painter.setPen(QPen(QColor(40, 40, 40), 2))
            painter.setBrush(Qt.NoBrush)
            painter.drawArc(cx - eye_offset - eye_size, cy - 5, eye_size * 2, eye_size * 2, 0, 180)
            painter.drawArc(cx + eye_offset - eye_size, cy - 5, eye_size * 2, eye_size * 2, 0, 180)
            painter.setPen(Qt.NoPen)
        elif state == PetState.SICK.value:
            # X 眼
            painter.setPen(QPen(QColor(40, 40, 40), 2))
            ox = eye_size // 2
            painter.drawLine(cx - eye_offset - ox, cy - ox, cx - eye_offset + ox, cy + ox)
            painter.drawLine(cx - eye_offset + ox, cy - ox, cx - eye_offset - ox, cy + ox)
            painter.drawLine(cx + eye_offset - ox, cy - ox, cx + eye_offset + ox, cy + ox)
            painter.drawLine(cx + eye_offset + ox, cy - ox, cx + eye_offset - ox, cy + ox)
            painter.setPen(Qt.NoPen)
        else:
            # 正常眼睛
            painter.drawEllipse(cx - eye_offset - eye_size // 2, cy - eye_size // 2, eye_size, eye_size)
            painter.drawEllipse(cx + eye_offset - eye_size // 2, cy - eye_size // 2, eye_size, eye_size)

        # 嘴巴
        mouth_y = cy + body_r // 2
        painter.setPen(QPen(QColor(40, 40, 40), 2))
        painter.setBrush(Qt.NoBrush)
        if state in (PetState.HAPPY.value, PetState.PLAYING.value):
            # 笑脸
            painter.drawArc(cx - body_r // 3, mouth_y - 10, body_r * 2 // 3, 20, 0, -180)
        elif state in (PetState.SAD.value, PetState.SICK.value):
            # 哭脸
            painter.drawArc(cx - body_r // 3, mouth_y, body_r * 2 // 3, 20, 0, 180)
        elif state == PetState.EATING.value:
            # 张嘴
            painter.drawEllipse(cx - 8, mouth_y - 5, 16, 16)
        elif state == PetState.SLEEPING.value:
            # Z 字形表示睡觉
            painter.setPen(QPen(QColor(100, 100, 100), 2))
            font = QFont("Arial", 14)
            painter.setFont(font)
            painter.drawText(cx + body_r, cy - body_r, "Z")
        else:
            # 普通嘴
            painter.drawLine(cx - 10, mouth_y, cx + 10, mouth_y)

        painter.setPen(Qt.NoPen)

    @staticmethod
    def get_min_size() -> QSize:
        return QSize(200, 200)


class AnimationController:
    """动画控制器 - 控制动画帧切换和状态过渡"""

    def __init__(self, pet_widget):
        self.pet_widget = pet_widget
        self.sprite_manager = SpriteManager()
        self._timer = QTimer()
        self._timer.timeout.connect(self._on_tick)
        self._timer.start(CONFIG.animation_interval)
        self._frame = 0

    def _on_tick(self):
        """动画帧回调"""
        self._frame += 1
        self.pet_widget.update()

    def set_state(self, state: str):
        """设置当前状态"""
        self.pet_widget.current_state = state

    def reload_sprites(self):
        """重新加载精灵图"""
        self.sprite_manager.reload()
