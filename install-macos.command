#!/bin/bash
# 电子宠物 macOS 安装脚本

echo "================================"
echo "  电子宠物 - 安装程序"
echo "================================"
echo ""

# 检查 Python3
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到 Python3，请先安装"
    echo "  brew install python3"
    exit 1
fi

echo "[1/3] 安装依赖中..."
pip3 install PySide6 -q

echo "[2/3] 创建启动脚本..."
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LAUNCHER="$HOME/Desktop/电子宠物.command"

cat > "$LAUNCHER" << EOF
#!/bin/bash
cd "$SCRIPT_DIR"
python3 main.py &
EOF
chmod +x "$LAUNCHER"

echo "[3/3] 安装完成！"
echo ""
echo "桌面上已创建"电子宠物"启动器，双击即可运行。"
echo ""
