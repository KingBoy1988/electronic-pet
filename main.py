"""
Electronic Pet - 电子宠物桌面应用
程序入口
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from src.controller import PetController


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Electronic Pet")
    app.setOrganizationName("ElectronicPet")

    # 高 DPI 支持
    app.setStyle("Fusion")

    controller = PetController()
    controller.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
