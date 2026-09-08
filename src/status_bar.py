"""
状态栏组件 - 显示宠物各项数值
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QProgressBar, QFrame)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from src.config import CONFIG


class StatBar(QWidget):
    """单个状态条"""

    def __init__(self, label: str, color: QColor, parent=None):
        super().__init__(parent)
        self._color = color
        self._label_text = label

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # 标签
        self.label = QLabel(label)
        self.label.setFixedWidth(45)
        self.label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.label)

        # 进度条
        self.progress = QProgressBar()
        self.progress.setRange(0, CONFIG.max_stat)
        self.progress.setValue(80)
        self.progress.setTextVisible(True)
        self.progress.setFormat("%v")
        self.progress.setFixedHeight(18)
        layout.addWidget(self.progress)

        self._apply_color(color)

    def _apply_color(self, color: QColor):
        """设置进度条颜色"""
        palette = self.progress.palette()
        palette.setColor(QPalette.ColorRole.Highlight, color)
        self.progress.setPalette(palette)

    def set_value(self, value: float):
        """设置数值"""
        int_value = max(CONFIG.min_stat, min(CONFIG.max_stat, int(value)))
        self.progress.setValue(int_value)

        # 数值过低时变红
        if int_value < 30:
            self._apply_color(QColor(220, 60, 60))
        else:
            self._apply_color(self._color)


class StatusBar(QWidget):
    """状态栏 - 显示宠物所有数值"""

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(4)

        # 等级和经验
        info_layout = QHBoxLayout()
        self.level_label = QLabel("Lv.1")
        self.level_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #4a90d9;")
        info_layout.addWidget(self.level_label)

        self.exp_bar = QProgressBar()
        self.exp_bar.setRange(0, 100)
        self.exp_bar.setValue(0)
        self.exp_bar.setTextVisible(True)
        self.exp_bar.setFormat("%v/%m")
        self.exp_bar.setFixedHeight(14)
        info_layout.addWidget(self.exp_bar)

        self.age_label = QLabel("")
        self.age_label.setStyleSheet("color: #888; font-size: 11px;")
        info_layout.addWidget(self.age_label)

        layout.addLayout(info_layout)

        # 分割线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #ddd;")
        layout.addWidget(line)

        # 各项状态条
        self.hunger_bar = StatBar("饱食", QColor(255, 160, 60))
        layout.addWidget(self.hunger_bar)

        self.happiness_bar = StatBar("心情", QColor(255, 200, 60))
        layout.addWidget(self.happiness_bar)

        self.energy_bar = StatBar("精力", QColor(100, 200, 100))
        layout.addWidget(self.energy_bar)

        self.health_bar = StatBar("健康", QColor(220, 80, 80))
        layout.addWidget(self.health_bar)

        self.cleanliness_bar = StatBar("清洁", QColor(100, 180, 255))
        layout.addWidget(self.cleanliness_bar)

    def update_stats(self, pet_data: dict):
        """更新所有状态显示"""
        self.level_label.setText(f"Lv.{pet_data.get('level', 1)}")
        self.age_label.setText(pet_data.get('age', ''))

        # 经验条
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

        # 更新经验条颜色
        palette = self.exp_bar.palette()
        palette.setColor(QPalette.ColorRole.Highlight, QColor(160, 120, 220))
        self.exp_bar.setPalette(palette)
