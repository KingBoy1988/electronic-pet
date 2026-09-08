"""
宠物显示组件 - 透明背景渲染宠物精灵图
"""

from PySide6.QtWidgets import QWidget, QToolTip
from PySide6.QtGui import QPainter, QPixmap, QAction, QColor
from PySide6.QtCore import Qt, QPoint, QPointF, QTimer
from src.config import CONFIG, PetState
from src.animations import SpriteManager, PlaceholderRenderer


class PetWidget(QWidget):
    """宠物显示组件 - 透明背景，支持鼠标交互"""

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.pet = controller.pet

        # 窗口属性 - 透明无边框置顶
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool  # 不在任务栏显示
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)  # 启用 hover 事件

        # 尺寸
        size = CONFIG.pet_size
        self.setFixedSize(size, size)

        # 状态
        self.current_state = PetState.IDLE.value
        self.sprite_manager = SpriteManager()
        self._bounce_offset = 0
        self._bounce_dir = 1
        self._is_hovered = False
        self._dragging = False
        self._drag_offset = QPoint(0, 0)
        self._click_count = 0
        self._click_timer = QTimer()
        self._click_timer.setSingleShot(True)
        self._click_timer.timeout.connect(self._on_single_click)

        # 临时状态定时器
        self._temp_state_timer = QTimer()
        self._temp_state_timer.setSingleShot(True)
        self._temp_state_timer.timeout.connect(self._on_temp_state_end)

        # 提示文字定时器（未使用，预留）
        self._tooltip_timer = QTimer()

    def set_state(self, state: str):
        """设置宠物状态"""
        self.current_state = state
        self.update()

    def update_animation(self):
        """更新动画帧"""
        # 弹跳效果（空闲/开心/玩耍时轻微跳动）
        if self.current_state in (PetState.IDLE.value, PetState.HAPPY.value, PetState.PLAYING.value):
            self._bounce_offset += self._bounce_dir * 2
            if self._bounce_offset > 5:
                self._bounce_dir = -1
            elif self._bounce_offset < -5:
                self._bounce_dir = 1
        elif self.current_state == PetState.SLEEPING.value:
            # 睡眠时缓慢呼吸效果
            self._bounce_offset += self._bounce_dir * 0.5
            if self._bounce_offset > 3:
                self._bounce_dir = -1
            elif self._bounce_offset < -3:
                self._bounce_dir = 1
        else:
            self._bounce_offset = 0
        self.update()

    def paintEvent(self, event):
        """绘制宠物 - 透明背景"""
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
                width, height,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            x = (width - scaled.width()) // 2
            y = (height - scaled.height()) // 2 + int(self._bounce_offset)
            painter.drawPixmap(x, y, scaled)
        else:
            # 绘制占位图
            painter.save()
            painter.translate(0, self._bounce_offset)
            PlaceholderRenderer.draw(painter, width, height, self.current_state)
            painter.restore()

        # 悬停时显示状态提示文字
        if self._is_hovered and not self._dragging:
            painter.setPen(QColor(60, 60, 60, 200))
            from PySide6.QtGui import QFont
            painter.setFont(QFont("Arial", 9))
            state_text = self.controller._get_state_display_text()
            text_rect = painter.fontMetrics().boundingRect(state_text)
            tx = (width - text_rect.width()) // 2
            ty = height - 5
            # 背景圆角矩形
            painter.setBrush(QColor(255, 255, 255, 200))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(tx - 6, ty - 16, text_rect.width() + 12, 20, 6, 6)
            # 文字
            painter.setPen(QColor(60, 60, 60))
            painter.drawText(tx, ty - 2, state_text)

        painter.end()

    # ========== 鼠标交互 ==========

    def mousePressEvent(self, event):
        """鼠标按下"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 开始拖拽
            self._dragging = False  # 先标记为可能拖拽
            self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self._click_start = event.globalPosition().toPoint()
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            # 右键菜单
            self._show_context_menu(event.globalPosition().toPoint())
            event.accept()

    def mouseMoveEvent(self, event):
        """鼠标移动 - 拖拽宠物"""
        if event.buttons() & Qt.MouseButton.LeftButton:
            current_pos = event.globalPosition().toPoint()
            # 如果移动距离超过阈值，标记为拖拽
            if (current_pos - self._click_start).manhattanLength() > 5:
                self._dragging = True
            if self._dragging:
                self.move(current_pos - self._drag_offset)
                event.accept()

    def mouseReleaseEvent(self, event):
        """鼠标释放"""
        if event.button() == Qt.MouseButton.LeftButton:
            if not self._dragging:
                # 单击/双击检测
                self._click_count += 1
                if self._click_count == 1:
                    self._click_timer.start(300)  # 300ms 内双击
                elif self._click_count == 2:
                    self._click_timer.stop()
                    self._click_count = 0
                    self._on_double_click()
            self._dragging = False
            event.accept()

    def _on_single_click(self):
        """单击事件"""
        self._click_count = 0
        # 单击 = 抚摸
        self.controller._on_pet()

    def _on_double_click(self):
        """双击事件 - 切换状态面板"""
        self.controller.toggle_status_panel()

    def enterEvent(self, event):
        """鼠标进入"""
        self._is_hovered = True
        self.update()

    def leaveEvent(self, event):
        """鼠标离开"""
        self._is_hovered = False
        self.update()

    def _show_context_menu(self, pos):
        """右键菜单"""
        from PySide6.QtWidgets import QMenu
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #ffffff;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 30px 6px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #f0f0f0;
            }
            QMenu::separator {
                height: 1px;
                background: #eee;
                margin: 4px 10px;
            }
        """)

        # 交互动作
        feed_action = menu.addAction("🍖 喂食")
        play_action = menu.addAction("🎾 玩耍")
        sleep_action = menu.addAction("💤 睡觉" if self.pet.current_state != PetState.SLEEPING.value else "☀️ 醒来")
        clean_action = menu.addAction("🛁 洗澡")
        pet_action = menu.addAction("🤚 抚摸")

        menu.addSeparator()

        # 信息
        info_action = menu.addAction(f"📊 状态: {self.controller._get_state_display_text()}")
        info_action.setEnabled(False)
        age_action = menu.addAction(f"🎂 年龄: {self.pet.age_display}")
        age_action.setEnabled(False)

        menu.addSeparator()

        # 面板切换
        if self.controller.status_panel.isVisible():
            panel_action = menu.addAction("🙈 隐藏面板")
        else:
            panel_action = menu.addAction("👁️ 显示面板")

        menu.addSeparator()

        # 保存和退出
        save_action = menu.addAction("💾 保存")
        quit_action = menu.addAction("❌ 退出")

        action = menu.exec(pos)

        if action == feed_action:
            self.controller._on_feed()
        elif action == play_action:
            self.controller._on_play()
        elif action == sleep_action:
            self.controller._on_sleep()
        elif action == clean_action:
            self.controller._on_clean()
        elif action == pet_action:
            self.controller._on_pet()
        elif action == panel_action:
            self.controller.toggle_status_panel()
        elif action == save_action:
            self.controller._on_save()
        elif action == quit_action:
            self.controller._on_quit()

    def set_temp_state(self, state: str, duration: float = None):
        """设置临时状态（如进食、玩耍动画）"""
        if duration is None:
            duration = CONFIG.temp_state_duration
        self.set_state(state)
        self._temp_state_timer.start(int(duration * 1000))

    def _on_temp_state_end(self):
        """临时状态结束"""
        self.controller._refresh_pet_state()

    def reload_sprites(self):
        """重新加载精灵图"""
        self.sprite_manager.reload()
        self.update()
