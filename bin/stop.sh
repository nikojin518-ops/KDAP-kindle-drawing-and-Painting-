#!/bin/sh
# KDAP v1.8 停止脚本（Kindle Voyage / K5 系列）
# 修复点：只杀 kdap 相关进程，不误杀全部 python3

LOG=/tmp/kdap.log
echo "==== KDAP v1.8 stop: $(date) ====" >>$LOG

# 精准杀 kdap.py，避免误伤其他 python3 程序
KDAP_PIDS=$(pgrep -f "python3.*kdap.py")
if [ -n "$KDAP_PIDS" ]; then
    kill $KDAP_PIDS 2>/dev/null
    sleep 1
    # 仍未退出的再强杀
    KDAP_PIDS=$(pgrep -f "python3.*kdap.py")
    if [ -n "$KDAP_PIDS" ]; then
        kill -9 $KDAP_PIDS 2>/dev/null
    fi
    echo "[ok] kdap.py stopped" >>$LOG
else
    echo "[info] kdap.py not running" >>$LOG
fi

# 清屏提示
FB=/mnt/us/kdap/bin/fbink
[ -x "$FB" ] || FB=$(command -v fbink 2>/dev/null)
if [ -n "$FB" ] && [ -x "$FB" ]; then
    $FB -c -f -W GC16 -m "KDAP stopped. GUI restored." >>$LOG 2>&1 || true
fi

echo "KDAP stopped."
