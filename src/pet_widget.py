"""
宠物显示组件 - 透明背景渲染宠物精灵图
支持揉捏变形 + 弹性回弹物理效果
"""

import math
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QPixmap, QColor, QFont, QTransform
from PySide6.QtCore import Qt, QPoint, QPointF, QTimer
from src.config import CONFIG, PetState
from src.animations import SpriteManager, PlaceholderRenderer


class PetWidget(QWidget):
    """宠物显示组件 - 透明背景，支持揉捏变形"""

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.pet = controller.pet

        # 窗口属性 - 透明无边框置顶
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

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

        # ===== 揉捏物理参数 =====
        # 当前缩放（1.0 = 原始大小）
        self._scale_x = 1.0
        self._scale_y = 1.0
        # 速度
        self._vel_x = 0.0
        self._vel_y = 0.0
        # 弹簧物理参数
        self._spring_stiffness = 0.15   # 弹簧硬度（越大回弹越快）
        self._spring_damping = 0.12     # 阻尼（越大停止越快）
        self._max_squish = 0.35         # 最大变形量
        # 揉捏灵敏度
        self._squish_factor = 0.008     # 拖拽距离到变形量的转换系数
        # 是否正在弹回
        self._is_bouncing = False
        # 拖拽起始位置和当前方向
        self._drag_start = QPointF(0, 0)
        self._drag_current = QPointF(0, 0)
        # 旋转角度（拖拽时轻微倾斜）
        self._rotation = 0.0
        self._rot_vel = 0.0

        # 弹性动画定时器
        self._physics_timer = QTimer()
        self._physics_timer.timeout.connect(self._update_physics)
        self._physics_timer.start(16)  # ~60fps

    def set_state(self, state: str):
        """设置宠物状态"""
        self.current_state = state
        self.update()

    def update_animation(self):
        """更新基础动画帧（弹跳）"""
        if self._is_bouncing or self._dragging:
            return  # 揉捏/弹回时不做基础弹跳

        if self.current_state in (PetState.IDLE.value, PetState.HAPPY.value, PetState.PLAYING.value):
            self._bounce_offset += self._bounce_dir * 2
            if self._bounce_offset > 5:
                self._bounce_dir = -1
            elif self._bounce_offset < -5:
                self._bounce_dir = 1
        elif self.current_state == PetState.SLEEPING.value:
            self._bounce_offset += self._bounce_dir * 0.5
            if self._bounce_offset > 3:
                self._bounce_dir = -1
            elif self._bounce_offset < -3:
                self._bounce_dir = 1
        else:
            self._bounce_offset = 0
        self.update()

    # ===== 揉捏物理引擎 =====

    def _update_physics(self):
        """弹簧物理更新 - 每帧调用"""
        if self._dragging:
            # 拖拽中：根据拖拽方向施加变形
            dx = self._drag_current.x() - self._drag_start.x()
            dy = self._drag_current.y() - self._drag_start.y()

            # 水平拖拽 -> 横向拉伸 + 纵向压缩
            target_sx = 1.0 + max(-self._max_squish, min(self._max_squish, dx * self._squish_factor))
            target_sy = 1.0 - max(-self._max_squish, min(self._max_squish, dx * self._squish_factor)) * 0.6

            # 垂直拖拽 -> 纵向拉伸 + 横向压缩
            target_sy += max(-self._max_squish, min(self._max_squish, dy * self._squish_factor)) * 0.6
            target_sx -= max(-self._max_squish, min(self._max_squish, dy * self._squish_factor)) * 0.4

            # 旋转：根据水平移动轻微倾斜
            target_rot = max(-15, min(15, dx * 0.15))

            # 平滑过渡到目标值
            self._scale_x += (target_sx - self._scale_x) * 0.3
            self._scale_y += (target_sy - self._scale_y) * 0.3
            self._rotation += (target_rot - self._rotation) * 0.2

            self.update()

        elif self._is_bouncing:
            # 弹回中：弹簧物理模拟
            # X 轴弹簧
            force_x = -self._spring_stiffness * (self._scale_x - 1.0)
            self._vel_x += force_x
            self._vel_x *= (1.0 - self._spring_damping)
            self._scale_x += self._vel_x

            # Y 轴弹簧
            force_y = -self._spring_stiffness * (self._scale_y - 1.0)
            self._vel_y += force_y
            self._vel_y *= (1.0 - self._spring_damping)
            self._scale_y += self._vel_y

            # 旋转弹簧
            force_rot = -self._spring_stiffness * 0.5 * self._rotation
            self._rot_vel += force_rot
            self._rot_vel *= (1.0 - self._spring_damping)
            self._rotation += self._rot_vel

            # 判断是否稳定下来
            total_motion = abs(self._vel_x) + abs(self._vel_y) + abs(self._rot_vel)
            total_offset = abs(self._scale_x - 1.0) + abs(self._scale_y - 1.0) + abs(self._rotation)
            if total_motion < 0.001 and total_offset < 0.001:
                self._scale_x = 1.0
                self._scale_y = 1.0
                self._rotation = 0.0
                self._vel_x = 0.0
                self._vel_y = 0.0
                self._rot_vel = 0.0
                self._is_bouncing = False
                self._bounce_offset = 0

            self.update()

    def paintEvent(self, event):
        """绘制宠物 - 透明背景 + 揉捏变形"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        width = self.width()
        height = self.height()

        # 中心点
        cx = width / 2.0
        cy = height / 2.0

        # 应用变换：平移到中心 -> 旋转 -> 缩放 -> 平移回去
        painter.save()
        painter.translate(cx, cy + self._bounce_offset)
        painter.rotate(self._rotation)
        painter.scale(self._scale_x, self._scale_y)
        painter.translate(-cx, -cy)

        # 获取精灵图
        sprite = self.sprite_manager.get_sprite(self.current_state)

        if sprite and not self.sprite_manager.use_placeholder:
            scaled = sprite.scaled(
                width, height,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            x = (width - scaled.width()) // 2
            y = (height - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
        else:
            PlaceholderRenderer.draw(painter, width, height, self.current_state)

        painter.restore()

        # 悬停时显示状态提示文字（不受变形影响）
        if self._is_hovered and not self._dragging:
            painter.setPen(QColor(60, 60, 60, 200))
            painter.setFont(QFont("Arial", 9))
            state_text = self.controller._get_state_display_text()
            text_rect = painter.fontMetrics().boundingRect(state_text)
            tx = (width - text_rect.width()) // 2
            ty = height - 5
            painter.setBrush(QColor(255, 255, 255, 200))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(tx - 6, ty - 16, text_rect.width() + 12, 20, 6, 6)
            painter.setPen(QColor(60, 60, 60))
            painter.drawText(tx, ty - 2, state_text)

        painter.end()

    # ========== 鼠标交互 ==========

    def mousePressEvent(self, event):
        """鼠标按下"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self._click_start = event.globalPosition().toPoint()
            # 记录揉捏起始点（相对于宠物中心）
            local_pos = event.position()
            self._drag_start = QPointF(
                local_pos.x() - self.width() / 2,
                local_pos.y() - self.height() / 2
            )
            self._drag_current = self._drag_start
            # 停止弹回
            self._is_bouncing = False
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            self._show_context_menu(event.globalPosition().toPoint())
            event.accept()

    def mouseMoveEvent(self, event):
        """鼠标移动 - 拖拽宠物 + 揉捏变形"""
        if event.buttons() & Qt.MouseButton.LeftButton:
            current_pos = event.globalPosition().toPoint()
            if (current_pos - self._click_start).manhattanLength() > 5:
                self._dragging = True
            if self._dragging:
                # 移动窗口
                self.move(current_pos - self._drag_offset)
                # 更新揉捏方向（基于鼠标在宠物上的相对位置）
                local_pos = event.position()
                self._drag_current = QPointF(
                    local_pos.x() - self.width() / 2,
                    local_pos.y() - self.height() / 2
                )
                event.accept()

    def mouseReleaseEvent(self, event):
        """鼠标释放 - 触发弹性回弹"""
        if event.button() == Qt.MouseButton.LeftButton:
            if not self._dragging:
                # 单击/双击检测
                self._click_count += 1
                if self._click_count == 1:
                    self._click_timer.start(300)
                elif self._click_count == 2:
                    self._click_timer.stop()
                    self._click_count = 0
                    self._on_double_click()
            else:
                # 拖拽结束 -> 启动弹性回弹
                self._is_bouncing = True
                # 给一点初始速度让回弹更有弹性
                self._vel_x = (1.0 - self._scale_x) * 0.5
                self._vel_y = (1.0 - self._scale_y) * 0.5
                self._rot_vel = -self._rotation * 0.3

            self._dragging = False
            event.accept()

    def _on_single_click(self):
        """单击事件 - 抚摸 + 轻微弹跳反馈"""
        self._click_count = 0
        # 单击时给一个轻微弹跳效果
        self._vel_y = 0.3
        self._is_bouncing = True
        self.controller._on_pet()

    def _on_double_click(self):
        """双击事件 - 切换状态面板 + 弹跳效果"""
        self._vel_y = -0.5
        self._vel_x = 0.1
        self._is_bouncing = True
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

        feed_action = menu.addAction("🍖 喂食")
        play_action = menu.addAction("🎾 玩耍")
        sleep_action = menu.addAction("💤 睡觉" if self.pet.current_state != PetState.SLEEPING.value else "☀️ 醒来")
        clean_action = menu.addAction("🛁 洗澡")
        pet_action = menu.addAction("🤚 抚摸")

        menu.addSeparator()

        info_action = menu.addAction(f"📊 状态: {self.controller._get_state_display_text()}")
        info_action.setEnabled(False)
        age_action = menu.addAction(f"🎂 年龄: {self.pet.age_display}")
        age_action.setEnabled(False)

        menu.addSeparator()

        if self.controller.status_panel.isVisible():
            panel_action = menu.addAction("🙈 隐藏面板")
        else:
            panel_action = menu.addAction("👁️ 显示面板")

        menu.addSeparator()

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
        """设置临时状态"""
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
