#!/bin/sh
# KDAP v1.8 启动脚本（Kindle Voyage / K5 系列）
# 修复点：依赖自检、写日志、给屏提示、不粗暴停 GUI

LOG=/tmp/kdap.log
FB=/mnt/us/kdap/bin/fbink

echo "==== KDAP v1.8 start: $(date) ====" >$LOG

# 1) 运行环境
export PYTHONPATH=/mnt/us/kdap
export HOME=/mnt/us/kdap
cd /mnt/us/kdap || { echo "cannot cd /mnt/us/kdap" >>$LOG; exit 1; }
mkdir -p drawings

# 2) 自检：fbink
if [ -x "$FB" ]; then
    echo "[ok] fbink found: $FB" >>$LOG
elif command -v fbink >/dev/null 2>&1; then
    echo "[ok] fbink in PATH: $(command -v fbink)" >>$LOG
else
    echo "[MISSING] fbink not found. Put FBInk K5/bin/fbink to $FB and chmod +x" >>$LOG
    # 能显示就给个屏上提示，不能显示就留日志
    $FB -c -f -W GC16 -m "KDAP: fbink missing" 2>>$LOG || true
fi

# 3) 自检：python3
if command -v python3 >/dev/null 2>&1; then
    echo "[ok] python3: $(python3 -V 2>&1)" >>$LOG
else
    echo "[MISSING] python3 not found" >>$LOG
    exit 2
fi

# 4) 自检：numpy / PIL
python3 -c "import numpy, PIL; print('[ok] numpy+PIL OK')" >>$LOG 2>>$LOG

# 5) 启动主程序（后台运行，不抢占当前 shell）
nohup setsid python3 kdap.py >>$LOG 2>&1 &
PID=$!
echo "[ok] kdap.py launched pid=$PID" >>$LOG

# 6) 提示前台一行
echo "KDAP v1.8 started. tail -f /tmp/kdap.log for details"
