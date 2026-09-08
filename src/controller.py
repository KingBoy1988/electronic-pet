"""
主窗口控制器 - 整合所有组件，管理交互逻辑
"""

import time
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QLabel, QMessageBox)
from PySide6.QtCore import Qt, QTimer
from src.config import CONFIG, PetState
from src.pet import Pet
from src.pet_widget import PetWidget
from src.status_bar import StatusBar
from src.animations import AnimationController


class PetController(QMainWindow):
    """主窗口控制器"""

    def __init__(self):
        super().__init__()

        # 初始化宠物
        self.pet = Pet.load()
        self.last_update = time.time()

        # 设置窗口
        self.setWindowTitle(CONFIG.window_title)
        self.setFixedSize(CONFIG.window_width, CONFIG.window_height)

        # 创建 UI
        self._init_ui()

        # 创建动画控制器
        self.animation = AnimationController(self.pet_widget)

        # 状态更新定时器
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._update_pet)
        self.status_timer.start(CONFIG.status_update_interval)

        # 动画定时器
        self.anim_timer = QTimer()
        self.anim_timer.timeout.connect(self._update_animation)
        self.anim_timer.start(CONFIG.animation_interval)

        # 交互冷却
        self._cooldowns = {}

        # 初始显示
        self._refresh_ui()

    def _init_ui(self):
        """初始化界面"""
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # 宠物名称
        name_bar = QHBoxLayout()
        self.name_label = QLabel(self.pet.name)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        name_bar.addWidget(self.name_label)

        self.state_label = QLabel("")
        self.state_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.state_label.setStyleSheet("font-size: 12px; color: #888;")
        name_bar.addWidget(self.state_label)
        layout.addLayout(name_bar)

        # 宠物显示区
        self.pet_widget = PetWidget()
        self.pet_widget.set_state(self.pet.current_state)
        layout.addWidget(self.pet_widget, stretch=1)

        # 状态栏
        self.status_bar = StatusBar()
        layout.addWidget(self.status_bar)

        # 按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(5)

        self.btn_feed = self._create_button("喂食", "#ff9a40")
        self.btn_feed.clicked.connect(self._on_feed)
        btn_layout.addWidget(self.btn_feed)

        self.btn_play = self._create_button("玩耍", "#ffc850")
        self.btn_play.clicked.connect(self._on_play)
        btn_layout.addWidget(self.btn_play)

        self.btn_sleep = self._create_button("睡觉", "#9aa9c0")
        self.btn_sleep.clicked.connect(self._on_sleep)
        btn_layout.addWidget(self.btn_sleep)

        self.btn_clean = self._create_button("洗澡", "#64b4ff")
        self.btn_clean.clicked.connect(self._on_clean)
        btn_layout.addWidget(self.btn_clean)

        self.btn_pet = self._create_button("抚摸", "#ff96c4")
        self.btn_pet.clicked.connect(self._on_pet)
        btn_layout.addWidget(self.btn_pet)

        layout.addLayout(btn_layout)

        # 底部操作栏
        bottom_layout = QHBoxLayout()

        self.btn_save = self._create_button("保存", "#80c864", small=True)
        self.btn_save.clicked.connect(self._on_save)
        bottom_layout.addWidget(self.btn_save)

        self.btn_revive = self._create_button("复活", "#ff6464", small=True)
        self.btn_revive.clicked.connect(self._on_revive)
        self.btn_revive.setVisible(not self.pet.is_alive)
        bottom_layout.addWidget(self.btn_revive)

        self.btn_reload = self._create_button("重载素材", "#a0a0a0", small=True)
        self.btn_reload.clicked.connect(self._on_reload_sprites)
        bottom_layout.addWidget(self.btn_reload)

        layout.addLayout(bottom_layout)

        # 样式
        self.setStyleSheet("""
            QMainWindow { background-color: #f5f5f5; }
        """)

    def _create_button(self, text: str, color: str, small: bool = False) -> QPushButton:
        """创建按钮"""
        btn = QPushButton(text)
        if small:
            btn.setFixedHeight(28)
            font_size = "11px"
        else:
            btn.setFixedHeight(40)
            font_size = "13px"
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 6px;
                font-size: {font_size};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {color};
                opacity: 0.85;
            }}
            QPushButton:pressed {{
                background-color: {color};
                opacity: 0.7;
            }}
            QPushButton:disabled {{
                background-color: #ccc;
                color: #999;
            }}
        """)
        return btn

    def _update_pet(self):
        """定时更新宠物状态"""
        now = time.time()
        delta = now - self.last_update
        self.last_update = now

        self.pet.update_stats(delta)

        # 交互状态自动恢复
        if self.pet.current_state in (PetState.EATING.value, PetState.PLAYING.value):
            if not hasattr(self, '_interact_end_time'):
                self._interact_end_time = {}
            end_time = self._interact_end_time.get(self.pet.current_state)
            if end_time and now >= end_time:
                self._interact_end_time.pop(self.pet.current_state)

        self._refresh_ui()
        self._check_buttons_enabled()

    def _update_animation(self):
        """更新动画帧"""
        self.pet_widget.update_animation()

    def _refresh_ui(self):
        """刷新界面"""
        self.name_label.setText(self.pet.name)
        self.state_label.setText(self._get_state_display_text())

        self.pet_widget.set_state(self.pet.current_state)
        self.status_bar.update_stats(self.pet.get_summary())

        self.btn_revive.setVisible(not self.pet.is_alive)

    def _get_state_display_text(self) -> str:
        """获取状态显示文字"""
        if not self.pet.is_alive:
            return "💀 已离世"
        state_text = {
            PetState.IDLE.value: "悠闲中...",
            PetState.EATING.value: "进食中...",
            PetState.SLEEPING.value: "睡眠中...",
            PetState.PLAYING.value: "玩耍中...",
            PetState.HAPPY.value: "非常开心!",
            PetState.SAD.value: "不太开心...",
            PetState.SICK.value: "生病了...",
        }
        return state_text.get(self.pet.current_state, "")

    def _check_buttons_enabled(self):
        """检查按钮可用状态"""
        alive = self.pet.is_alive
        sleeping = self.pet.current_state == PetState.SLEEPING.value

        self.btn_feed.setEnabled(alive and not sleeping)
        self.btn_play.setEnabled(alive and not sleeping and self.pet.energy > CONFIG.play_energy_cost)
        self.btn_sleep.setEnabled(alive and not sleeping)
        self.btn_clean.setEnabled(alive and not sleeping)
        self.btn_pet.setEnabled(alive and not sleeping)

    def _can_interact(self, action: str) -> bool:
        """检查交互冷却"""
        now = time.time()
        if action in self._cooldowns:
            remaining = self._cooldowns[action] - now
            if remaining > 0:
                return False
        self._cooldowns[action] = now + 1.0  # 1秒通用冷却
        return True

    def _on_feed(self):
        """喂食"""
        if not self._can_interact("feed") or not self.pet.is_alive:
            return
        self.pet.feed()
        self._set_temp_state(PetState.EATING.value, 2.0)
        self._refresh_ui()

    def _on_play(self):
        """玩耍"""
        if not self._can_interact("play") or not self.pet.is_alive:
            return
        if self.pet.play():
            self._set_temp_state(PetState.PLAYING.value, 2.0)
            self._refresh_ui()
        else:
            QMessageBox.information(self, "提示", f"{self.pet.name} 太累了，需要休息！")

    def _on_sleep(self):
        """睡觉/醒来"""
        if not self.pet.is_alive:
            return
        if self.pet.current_state == PetState.SLEEPING.value:
            self.pet.wake_up()
        else:
            self.pet.sleep()
        self._refresh_ui()

    def _on_clean(self):
        """洗澡"""
        if not self._can_interact("clean") or not self.pet.is_alive:
            return
        self.pet.clean()
        self._refresh_ui()

    def _on_pet(self):
        """抚摸"""
        if not self._can_interact("pet") or not self.pet.is_alive:
            return
        self.pet.pet()
        self._refresh_ui()

    def _set_temp_state(self, state: str, duration: float):
        """设置临时状态"""
        self.pet.current_state = state
        self._interact_end_time = getattr(self, '_interact_end_time', {})
        self._interact_end_time[state] = time.time() + duration

    def _on_save(self):
        """手动保存"""
        self.pet.save()
        QMessageBox.information(self, "保存成功", f"{self.pet.name} 的状态已保存！")

    def _on_revive(self):
        """复活宠物"""
        reply = QMessageBox.question(
            self, "复活宠物",
            f"确定要复活 {self.pet.name} 吗？\n（状态将重置）",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.pet = Pet(name=self.pet.name)
            self.pet.save()
            self.last_update = time.time()
            self._refresh_ui()
            self._check_buttons_enabled()

    def _on_reload_sprites(self):
        """重新加载精灵图"""
        self.pet_widget.reload_sprites()
        self.animation.reload_sprites()
        QMessageBox.information(self, "提示", "素材已重新加载！\n\n请确保图片已放入 assets/sprites/ 目录。")

    def closeEvent(self, event):
        """关闭时自动保存"""
        self.pet.save()
        event.accept()
