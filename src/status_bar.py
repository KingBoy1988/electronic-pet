"""
状态面板 - 浮动在宠物旁边的迷你状态面板
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QProgressBar, QFrame, QPushButton)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QPalette, QFont
from src.config import CONFIG


class StatBar(QWidget):
    """单个状态条 - 迷你版"""

    def __init__(self, label: str, emoji: str, color: QColor, parent=None):
        super().__init__(parent)
        self._color = color

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Emoji + 标签
        self.label = QLabel(f"{emoji} {label}")
        self.label.setFixedWidth(60)
        self.label.setStyleSheet("font-size: 10px; color: #555;")
        layout.addWidget(self.label)

        # 进度条
        self.progress = QProgressBar()
        self.progress.setRange(0, CONFIG.max_stat)
        self.progress.setValue(80)
        self.progress.setTextVisible(True)
        self.progress.setFormat("%v")
        self.progress.setFixedHeight(14)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 4px;
                background: #f0f0f0;
                text-align: center;
                font-size: 9px;
                color: white;
            }
        """)
        layout.addWidget(self.progress)

        self._apply_color(color)

    def _apply_color(self, color: QColor):
        palette = self.progress.palette()
        palette.setColor(QPalette.ColorRole.Highlight, color)
        palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
        self.progress.setPalette(palette)

    def set_value(self, value: float):
        int_value = max(CONFIG.min_stat, min(CONFIG.max_stat, int(value)))
        self.progress.setValue(int_value)
        if int_value < 30:
            self._apply_color(QColor(220, 60, 60))
        else:
            self._apply_color(self._color)


class StatusPanel(QWidget):
    """浮动状态面板 - 显示在宠物旁边"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # 透明无边框窗口
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setFixedWidth(200)

        # 主容器
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 230);
                border-radius: 12px;
                border: 1px solid rgba(200, 200, 200, 150);
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.addWidget(container)

        inner_layout = QVBoxLayout(container)
        inner_layout.setContentsMargins(10, 8, 10, 8)
        inner_layout.setSpacing(3)

        # 标题
        title = QLabel("📊 宠物状态")
        title.setStyleSheet("font-size: 11px; font-weight: bold; color: #333;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        inner_layout.addWidget(title)

        # 等级和经验
        info_layout = QHBoxLayout()
        self.level_label = QLabel("Lv.1")
        self.level_label.setStyleSheet("font-size: 10px; font-weight: bold; color: #4a90d9;")
        info_layout.addWidget(self.level_label)

        self.exp_bar = QProgressBar()
        self.exp_bar.setRange(0, 100)
        self.exp_bar.setValue(0)
        self.exp_bar.setTextVisible(True)
        self.exp_bar.setFormat("%v/%m")
        self.exp_bar.setFixedHeight(12)
        self.exp_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 3px;
                background: #eee;
                text-align: center;
                font-size: 8px;
                color: white;
            }
        """)
        info_layout.addWidget(self.exp_bar)
        inner_layout.addLayout(info_layout)

        # 年龄
        self.age_label = QLabel("🎂 0分钟")
        self.age_label.setStyleSheet("font-size: 9px; color: #888;")
        inner_layout.addWidget(self.age_label)

        # 分割线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #ddd;")
        line.setFixedHeight(1)
        inner_layout.addWidget(line)

        # 状态条
        self.hunger_bar = StatBar("饱食", "🍖", QColor(255, 160, 60))
        inner_layout.addWidget(self.hunger_bar)

        self.happiness_bar = StatBar("心情", "😊", QColor(255, 200, 60))
        inner_layout.addWidget(self.happiness_bar)

        self.energy_bar = StatBar("精力", "⚡", QColor(100, 200, 100))
        inner_layout.addWidget(self.energy_bar)

        self.health_bar = StatBar("健康", "❤️", QColor(220, 80, 80))
        inner_layout.addWidget(self.health_bar)

        self.cleanliness_bar = StatBar("清洁", "🛁", QColor(100, 180, 255))
        inner_layout.addWidget(self.cleanliness_bar)

        # 经验条颜色
        palette = self.exp_bar.palette()
        palette.setColor(QPalette.ColorRole.Highlight, QColor(160, 120, 220))
        self.exp_bar.setPalette(palette)

    def update_stats(self, pet_data: dict):
        """更新所有状态显示"""
        self.level_label.setText(f"Lv.{pet_data.get('level', 1)}")
        self.age_label.setText(f"🎂 {pet_data.get('age', '')}")

        exp_str = pet_data.get('exp', '0/100')
        try:
            parts = exp_str.split('/')
            self.exp_bar.setRange(0, int(parts[1]))
            self.exp_bar.setValue(int(parts[0]))
        except (IndexError, ValueError):
            pass

        self.hunger_bar.set_value(pet_data.get('hunger', 0))
        self.happiness_bar.set_value(pet_data.get('happiness', 0))
        self.energy_bar.set_value(pet_data.get('energy', 0))
        self.health_bar.set_value(pet_data.get('health', 0))
        self.cleanliness_bar.set_value(pet_data.get('cleanliness', 0))

    def follow_pet(self, pet_pos, pet_size):
        """跟随宠物位置"""
        x = pet_pos.x() + pet_size + 10
        y = pet_pos.y() - 10
        self.move(x, y)
