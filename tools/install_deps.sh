#!/bin/sh
# install_deps.sh - 安装 KDAP 运行依赖
# 适用于越狱后的 Kindle（Debian/Ubuntu 系）

echo "=== KDAP Dependency Installer ==="

# 更新包列表
echo "[1/4] Updating package lists..."
tput -T vt100 clear > /dev/null 2>&1 || true
opkg update 2>/dev/null || apt-get update 2>/dev/null || echo "Package manager not found, trying pip only"

# 安装 Python3 + pip
echo "[2/4] Installing Python3..."
opkg install python3 python3-pip python3-setuptools 2>/dev/null || \
apt-get install -y python3 python3-pip 2>/dev/null || true

# 安装 Python 包
echo "[3/4] Installing Python packages..."
pip3 install --upgrade pip 2>/dev/null || true
pip3 install numpy Pillow evdev 2>/dev/null || true

# 检查 FBInk
echo "[4/4] Checking FBInk..."
which FBInk 2>/dev/null && echo "FBInk found" || echo "FBInk NOT found - please install FBInk manually"

echo ""
echo "=== Done ==="
echo "If packages failed to install via opkg/apt, try:"
echo "  pip3 install numpy Pillow evdev --target /mnt/us/kdap/lib"
echo "  export PYTHONPATH=/mnt/us/kdap/lib:\$PYTHONPATH"
