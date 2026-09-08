"""
主窗口控制器 - 桌面宠物模式
宠物在桌面上自由活动，通过鼠标交互
"""

import sys
import time
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt, QTimer, QPoint
from src.config import CONFIG, PetState
from src.pet import Pet
from src.pet_widget import PetWidget
from src.status_bar import StatusPanel
from src.singing import singing_manager


class PetController:
    """桌面宠物控制器"""

    def __init__(self):
        # 初始化宠物
        self.pet = Pet.load()
        self.last_update = time.time()

        # 创建宠物显示窗口
        self.pet_widget = PetWidget(self)

        # 创建状态面板
        self.status_panel = StatusPanel()

        # 状态更新定时器
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._update_pet)
        self.status_timer.start(CONFIG.status_update_interval)

        # 动画定时器
        self.anim_timer = QTimer()
        self.anim_timer.timeout.connect(self._update_animation)
        self.anim_timer.start(CONFIG.animation_interval)

        # 面板跟随定时器
        self.follow_timer = QTimer()
        self.follow_timer.timeout.connect(self._update_panel_position)
        self.follow_timer.start(50)  # 50ms 跟随

        # 交互冷却
        self._cooldowns = {}

        # 唱歌状态
        self._is_singing = False
        self._sing_timer = QTimer()
        self._sing_timer.setSingleShot(True)
        self._sing_timer.timeout.connect(self._on_sing_end)

        # 初始显示
        self._refresh_ui()

        # 初始位置 - 屏幕右下角
        self._set_initial_position()

    def _set_initial_position(self):
        """设置初始位置在屏幕右下角"""
        screen = QApplication.primaryScreen().geometry()
        x = screen.width() - self.pet_widget.width() - 50
        y = screen.height() - self.pet_widget.height() - 100
        self.pet_widget.move(x, y)

    def show(self):
        """显示宠物"""
        self.pet_widget.show()

    # ========== 状态更新 ==========

    def _update_pet(self):
        """定时更新宠物状态"""
        now = time.time()
        delta = now - self.last_update
        self.last_update = now

        self.pet.update_stats(delta)
        self._refresh_ui()

    def _update_animation(self):
        """更新动画帧"""
        self.pet_widget.update_animation()

    def _update_panel_position(self):
        """更新状态面板位置 - 跟随宠物"""
        if self.status_panel.isVisible():
            pet_pos = self.pet_widget.pos()
            pet_size = self.pet_widget.width()
            self.status_panel.follow_pet(pet_pos, pet_size)

    def _refresh_ui(self):
        """刷新界面"""
        self.pet_widget.set_state(self.pet.current_state)
        self.status_panel.update_stats(self.pet.get_summary())

    def _refresh_pet_state(self):
        """临时状态结束后刷新"""
        self.pet._auto_update_state()
        self._refresh_ui()

    def _get_state_display_text(self) -> str:
        """获取状态显示文字"""
        if not self.pet.is_alive:
            return "💀 已离世"
        state_text = {
            PetState.IDLE.value: "悠闲中~",
            PetState.EATING.value: "进食中~",
            PetState.SLEEPING.value: "睡眠中~",
            PetState.PLAYING.value: "玩耍中~",
            PetState.HAPPY.value: "非常开心!",
            PetState.SAD.value: "不太开心...",
            PetState.SICK.value: "生病了...",
            PetState.SINGING.value: "🎵 唱歌中~♪",
        }
        return state_text.get(self.pet.current_state, "")

    # ========== 面板控制 ==========

    def toggle_status_panel(self):
        """切换状态面板显示/隐藏"""
        if self.status_panel.isVisible():
            self.status_panel.hide()
        else:
            self._update_panel_position()
            self.status_panel.show()

    # ========== 交互逻辑 ==========

    def _can_interact(self, action: str) -> bool:
        """检查交互冷却"""
        now = time.time()
        if action in self._cooldowns:
            remaining = self._cooldowns[action] - now
            if remaining > 0:
                return False
        self._cooldowns[action] = now + 1.0
        return True

    def _on_feed(self):
        """喂食"""
        if not self.pet.is_alive or self.pet.current_state == PetState.SLEEPING.value:
            return
        if not self._can_interact("feed"):
            return
        self.pet.feed()
        self.pet_widget.set_temp_state(PetState.EATING.value)
        self._refresh_ui()

    def _on_play(self):
        """玩耍"""
        if not self.pet.is_alive or self.pet.current_state == PetState.SLEEPING.value:
            return
        if not self._can_interact("play"):
            return
        if self.pet.play():
            self.pet_widget.set_temp_state(PetState.PLAYING.value)
            self._refresh_ui()

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
        if not self.pet.is_alive or self.pet.current_state == PetState.SLEEPING.value:
            return
        if not self._can_interact("clean"):
            return
        self.pet.clean()
        self._refresh_ui()

    def _on_pet(self):
        """抚摸"""
        if not self.pet.is_alive or self.pet.current_state == PetState.SLEEPING.value:
            return
        if not self._can_interact("pet"):
            return
        self.pet.pet()
        self._refresh_ui()

    def _on_save(self):
        """手动保存"""
        self.pet.save()

    # ========== 唱歌 ==========

    def _on_sing(self):
        """开始唱歌"""
        if not self.pet.is_alive or self.pet.current_state == PetState.SLEEPING.value:
            return
        if self._is_singing:
            # 正在唱歌 -> 停止
            self._on_sing_end()
            return
        if not self._can_interact("sing"):
            return

        self._is_singing = True
        self.pet_widget.set_state(PetState.SINGING.value)
        # 开始播放音乐
        singing_manager.start_singing(CONFIG.singing_duration)
        # 设置唱歌结束定时器
        self._sing_timer.start(int(CONFIG.singing_duration * 1000))

    def _on_sing_end(self):
        """唱歌结束"""
        self._is_singing = False
        singing_manager.stop_singing()
        self._sing_timer.stop()
        self.pet._auto_update_state()
        self._refresh_ui()

    def _on_revive(self):
        """复活宠物"""
        self.pet = Pet(name=self.pet.name)
        self.pet.save()
        self.last_update = time.time()
        self._refresh_ui()

    def _on_quit(self):
        """退出应用"""
        self.pet.save()
        QApplication.quit()

    def closeEvent(self, event):
        """关闭时自动保存"""
        self.pet.save()
        event.accept()
