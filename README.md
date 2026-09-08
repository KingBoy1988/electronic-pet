# Electronic Pet (电子宠物)

一个用 Python + PySide6 构建的桌面电子宠物应用。支持喂食、玩要、睡眠、清洁等交互，宠物状态随时间变化，支持自定义宠物模型素材。

## 功能特性

- **状态系统**：饥饿值、心情值、精力值、健康值、清洁度
- **交互系统**：喂食、玩要、睡眠、清洁、抚摸
- **动画系统**：空闲、进食、睡眠、玩要、开心、伤心等状态动画
- **时间系统**：状态随时间衰减，离线后状态继续变化
- **存档系统**：自动保存/加载宠物状态
- **自定义模型**：支持替换 `assets/sprites/` 中的图片素材

## 安装

```bash
# 克隆仓库
git clone https://github.com/KingBoy1988/electronic-pet.git
cd electronic-pet

# 安装依赖
pip install -r requirements.txt
```

## 运行

```bash
python main.py
```

## 项目结构

```
electronic-pet/
├── main.py                # 程序入口
├── requirements.txt       # Python 依赖
├── setup.py              # 安装配置
├── src/
│   ├── __init__.py
│   ├── config.py          # 全局配置
│   ├── pet.py             # 宠物数据模型
│   ├── animations.py      # 动画管理器
│   ├── pet_widget.py      # 宠物显示组件
│   ├── status_bar.py      # 状态栏组件
│   └── controller.py      # 主窗口控制器
├── assets/
│   ├── sprites/           # 宠物模型图片（可自定义）
│   ├── sounds/           # 音效文件
│   └── icons/             # UI 图标
├── saves/                 # 存档目录
└── .gitignore
```

## 自定义宠物模型

将你的宠物图片放入 `assets/sprites/` 目录，按以下命名：

| 文件名 | 用途 |
|--------|------|
| `idle.png` | 空闲状态 |
| `eating.png` | 进食状态 |
| `sleeping.png` | 睡眠状态 |
| `playing.png` | 玩要状态 |
| `happy.png` | 开心状态 |
| `sad.png` | 伤心状态 |
| `sick.png` | 生病状态 |

图片建议使用 PNG 格式（支持透明背景），尺寸 200x200 像素。

## 技术栈

- **Python 3.8+**
- **PySide6** (Qt for Python) - GUI 框架
- **JSON** - 存档格式

## License

MIT License
