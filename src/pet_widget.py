"""
宠物显示组件 - 渲染宠物精灵图或占位图
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtCore import Qt, QSize
from src.config import CONFIG, PetState
from src.animations import SpriteManager, PlaceholderRenderer


class PetWidget(QWidget):
    """宠物显示组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(280, 280)
        self.current_state = PetState.IDLE.value
        self.sprite_manager = SpriteManager()
        self._bounce_offset = 0
        self._bounce_dir = 1

    def set_state(self, state: str):
        """设置宠物状态"""
        self.current_state = state
        self.update()

    def update_animation(self):
        """更新动画帧"""
        # 弹跳效果（空闲/开心时轻微跳动）
        if self.current_state in (PetState.IDLE.value, PetState.HAPPY.value, PetState.PLAYING.value):
            self._bounce_offset += self._bounce_dir * 2
            if self._bounce_offset > 6:
                self._bounce_dir = -1
            elif self._bounce_offset < -6:
                self._bounce_dir = 1
        else:
            self._bounce_offset = 0
        self.update()

    def paintEvent(self, event):
        """绘制宠物"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        width = self.width()
        height = self.height()

        # 获取精灵图
        sprite = self.sprite_manager.get_sprite(self.current_state)

        if sprite and not self.sprite_manager.use_placeholder:
            # 绘制自定义精灵图
            scaled = sprite.scaled(
                width - 40, height - 40,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            x = (width - scaled.width()) // 2
            y = (height - scaled.height()) // 2 + self._bounce_offset
            painter.drawPixmap(x, y, scaled)
        else:
            # 绘制占位图
            # 加上弹跳偏移
            painter.save()
            painter.translate(0, self._bounce_offset)
            PlaceholderRenderer.draw(painter, width, height, self.current_state)
            painter.restore()

        painter.end()

    def reload_sprites(self):
        """重新加载精灵图"""
        self.sprite_manager.reload()
        self.update()
