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
        self.pet = Pet.load()
        self.last_update = time.time()

        self.pet_widget = PetWidget(self)
        self.status_panel = StatusPanel()

        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._update_pet)
        self.status_timer.start(CONFIG.status_update_interval)

        self.anim_timer = QTimer()
        self.anim_timer.timeout.connect(self._update_animation)
        self.anim_timer.start(CONFIG.animation_interval)

        self.follow_timer = QTimer()
        self.follow_timer.timeout.connect(self._update_panel_position)
        self.follow_timer.start(50)

        self._cooldowns = {}
        self._is_singing = False
        self._sing_timer = QTimer()
        self._sing_timer.setSingleShot(True)
        self._sing_timer.timeout.connect(self._on_sing_end)

        self._refresh_ui()
        self._set_initial_position()

    def _set_initial_position(self):
        screen = QApplication.primaryScreen().geometry()
        x = screen.width() - self.pet_widget.width() - 50
        y = screen.height() - self.pet_widget.height() - 100
        self.pet_widget.move(x, y)

    def show(self):
        self.pet_widget.show()

    def _update_pet(self):
        now = time.time()
        delta = now - self.last_update
        self.last_update = now
        self.pet.update_stats(delta)
        self._refresh_ui()

    def _update_animation(self):
        self.pet_widget.update_animation()

    def _update_panel_position(self):
        if self.status_panel.isVisible():
            pet_pos = self.pet_widget.pos()
            pet_size = self.pet_widget.width()
            self.status_panel.follow_pet(pet_pos, pet_size)

    def _refresh_ui(self):
        self.pet_widget.set_state(self.pet.current_state)
        self.status_panel.update_stats(self.pet.get_summary())

    def _refresh_pet_state(self):
        self.pet._auto_update_state()
        self._refresh_ui()

    def _get_state_display_text(self) -> str:
        if not self.pet.is_alive:
            return "已离世"
        state_text = {
            PetState.IDLE.value: "悠闲中~",
            PetState.EATING.value: "进食中~",
            PetState.SLEEPING.value: "睡眠中~",
            PetState.PLAYING.value: "玩耍中~",
            PetState.HAPPY.value: "非常开心!",
            PetState.SAD.value: "不太开心...",
            PetState.SICK.value: "生病了...",
            PetState.SINGING.value: "唱歌中~",
        }
        return state_text.get(self.pet.current_state, "")

    def toggle_status_panel(self):
        if self.status_panel.isVisible():
            self.status_panel.hide()
        else:
            self._update_panel_position()
            self.status_panel.show()

    def _can_interact(self, action: str) -> bool:
        now = time.time()
        if action in self._cooldowns:
            remaining = self._cooldowns[action] - now
            if remaining > 0:
                return False
        self._cooldowns[action] = now + 1.0
        return True

    def _on_feed(self):
        if not self.pet.is_alive or self.pet.current_state == PetState.SLEEPING.value:
            return
        if not self._can_interact("feed"):
            return
        self.pet.feed()
        self.pet_widget.set_temp_state(PetState.EATING.value)
        self._refresh_ui()

    def _on_play(self):
        if not self.pet.is_alive or self.pet.current_state == PetState.SLEEPING.value:
            return
        if not self._can_interact("play"):
            return
        if self.pet.play():
            self.pet_widget.set_temp_state(PetState.PLAYING.value)
            self._refresh_ui()

    def _on_sleep(self):
        if not self.pet.is_alive:
            return
        if self.pet.current_state == PetState.SLEEPING.value:
            self.pet.wake_up()
        else:
            self.pet.sleep()
        self._refresh_ui()

    def _on_clean(self):
        if not self.pet.is_alive or self.pet.current_state == PetState.SLEEPING.value:
            return
        if not self._can_interact("clean"):
            return
        self.pet.clean()
        self._refresh_ui()

    def _on_pet(self):
        if not self.pet.is_alive or self.pet.current_state == PetState.SLEEPING.value:
            return
        if not self._can_interact("pet"):
            return
        self.pet.pet()
        self._refresh_ui()

    def _on_save(self):
        self.pet.save()

    def _on_sing(self):
        if not self.pet.is_alive or self.pet.current_state == PetState.SLEEPING.value:
            return
        if self._is_singing:
            self._on_sing_end()
            return
        if not self._can_interact("sing"):
            return
        self._is_singing = True
        self.pet_widget.set_state(PetState.SINGING.value)
        singing_manager.start_singing(CONFIG.singing_duration)
        self._sing_timer.start(int(CONFIG.singing_duration * 1000))

    def _on_sing_end(self):
        self._is_singing = False
        singing_manager.stop_singing()
        self._sing_timer.stop()
        self.pet._auto_update_state()
        self._refresh_ui()

    def _on_revive(self):
        self.pet = Pet(name=self.pet.name)
        self.pet.save()
        self.last_update = time.time()
        self._refresh_ui()

    def _on_quit(self):
        self.pet.save()
        QApplication.quit()

    def closeEvent(self, event):
        self.pet.save()
        event.accept()
