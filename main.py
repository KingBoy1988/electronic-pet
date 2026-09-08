"""
Electronic Pet - 桌面电子宠物
程序入口 - 透明窗口桌面宠物模式
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from src.controller import PetController


def main():
    # 高 DPI 支持
    QApplication.setHighDpiScaleFactorScalingPolicy(
        Qt.HighDpiScaleFactorScalingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("Electronic Pet")
    app.setOrganizationName("ElectronicPet")
    app.setQuitOnLastWindowClosed(True)
    app.setStyle("Fusion")

    controller = PetController()
    controller.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
