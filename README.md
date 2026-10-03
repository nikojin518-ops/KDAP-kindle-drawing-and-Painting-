[README.md](https://github.com/user-attachments/files/32988826/README.md)
# KDAP-kindle-drawing-and-Painting-
this is an tool to use kindle to drawing and painting
# KDAP - Kindle Drawing & Painting

为 Kindle（特别适配 Voyage / K5 系列）打造的灰度绘画软件。

## KDAP v1.8

在 v1.5 全部功能基础上，修复安装与运行依赖问题，并内嵌 FBInk 集成方案。

### v1.8 新增 / 修复

- **FBInk 自动探测**：启动时按优先级查找 `fbink`
  1. `/mnt/us/kdap/bin/fbink`（项目自带，推荐）
  2. `PATH` 中的 `fbink`（NiLuJe 已装时）
  3. 兼容旧写法的 `FBInk`
  4. 兜底路径 `/usr/local/bin/fbink`、`/usr/bin/fbink`
- **依赖自检**：启动脚本检查 fbink / python3 / numpy / PIL，缺哪个就写在 `/tmp/kdap.log` 里
- **文件格式向后兼容**：v1.8 能打开 v1.5 保存的 `.kdap` 文件（magic `KDAP`、版本字段 `0x0108`，旧文件照读）
- **精准停进程**：`stop.sh` 只杀 `kdap.py`，不再误杀所有 `python3`
- **启动写屏确认**：`kdap_init_fb()` 清屏并显示 "KDAP v1.8 Ready"

## 功能

- 画笔 / 橡皮 / 油漆桶 / 移动工具
- 多图层系统（8层，显隐 / 增删 / 移动 / 透明度 / 混合模式）
- 文字工具（预设文字 + 软键盘 + SSH 管道 + HTTP 输入）
- 软键盘（英文 QWERTY + 中文拼音 + 符号）
- HTTP 文字输入（浏览器远程输入，支持 Basic Auth）
- 保存 PNG / `.kdap`（多图层，含缩略图，文件版本 v1.8）
- 读取 `.kdap` 文件（兼容 v1.5）
- 横屏 / 竖屏布局切换
- 中英文界面（首次启动选语言）
- 字体粗细与字体切换
- 图层缩略图 + 文件自动命名（`kdapMMDD`）

## 依赖

- **越狱 Kindle** + **KUAL** + **MRPI**
- **Python3**（NiLuJe 的 Kindle 5/PW2/KV 版）
- **numpy** + **Pillow**（NiLuJe Python3 快照自带）
- **FBInk**（命令行二进制 `fbink`，**本项目不含该二进制**，见下方）

> evdev 为可选：装了就用原生触摸输入，没装走 HTTP / 模拟输入也能跑。

## 安装

1. 越狱 Kindle，装 KUAL + MRPI（NiLuJe Snapshots）
2. 装 Python3（含 numpy + Pillow）
3. 解压 KDAP 到 `/mnt/us/kdap/`
4. 把 KUAL 扩展拷进去：
   ```
   kual/menu.json     →   /mnt/us/extensions/kdap/menu.json
   kual/config.xml    →   /mnt/us/extensions/kdap/config.xml
   bin/start.sh       →   /mnt/us/extensions/kdap/bin/start.sh
   bin/stop.sh        →   /mnt/us/extensions/kdap/bin/stop.sh
   ```
   没有 `config.xml` 就照 KUAL 文档补一个指向 `menu.json` 的扩展描述。
5. 给脚本加执行权限：
   ```sh
   chmod +x /mnt/us/extensions/kdap/bin/*.sh
   chmod +x /mnt/us/kdap/bin/*.sh
   chmod +x /mnt/us/kdap/kdap.py
   ```
6. 放 FBInk（见下一节）
7. KUAL 里点 "Start KDAP"

## FBInk 怎么装（项目不含该二进制）

本项目**没有打包 `fbink` 可执行文件**。它用 GPLv2 开源，请从 NiLuJe 维护的发布页获取：

- 发布页：<https://github.com/NiLuJe/FBInk/releases>
- 选 `FBInk-x.x.x-Kindle.zip`（不是 "Source code" 那两个）
- 解压后取 **`K5/bin/fbink`**（Voyage 属 K5/PW2 armv7，别用 K3）
- 放到 Kindle：
  ```sh
  cp fbink /mnt/us/kdap/bin/fbink
  chmod +x /mnt/us/kdap/bin/fbink
  /mnt/us/kdap/bin/fbink -m "FBInk OK"
  ```
  屏幕显示 "FBInk OK" 就说明装对了。

> 提示：装了 NiLuJe USBNetwork 的设备通常已有系统级 `fbink`，
> KDAP 会优先用项目自带的，没有再走系统路径。

## 操作

- 左侧工具栏切换工具
- 连点 3 下画笔/橡皮 → 粗细面板
- 连点 3 下文字工具 T → 字体面板
- 点 ⚙ → 图层列表面板
- 文字工具点画布 → 预设文字 / 键盘 / HTTP
- 设置 → HTTP → 配置 IP / 端口 / 用户名 / 密码
- 浏览器打开 `http://kindle-ip:port` → 输入文字

## HTTP 配置（SSH）

```bash
cd /mnt/us/kdap
python3 -c "
import json
p='kdap.conf'
d=json.load(open(p))
d['http_port']=9090
d['http_user']='myname'
d['http_pass']='mypassword'
json.dump(d, open(p,'w'))
print('done')
"
```

## 文件格式

- `.png` —— 合并后的灰度图像
- `.kdap` —— 多图层源文件（魔数 `KDAP`，版本 **1.8** = `0x0108`，
  含缩略图；**v1.5 (`0x0105`) 文件可直接打开**，旧版 KDAP 打开新版会提示版本不支持）
- 默认文件名：`kdapMMDD.kdap`（月日）

## 目录结构

```
kdap/
├── kdap.py            # 主入口
├── kdap.conf          # 配置文件（含 fbink_path、max_layers）
├── core/              # 核心引擎（含 fb.py 帧缓冲输出）
├── ui/                # 界面
├── input/             # 输入（touch.py 条件导入 evdev）
├── kio/               # 文件 I/O（kdap_io.py 唯一真源）
├── ime/               # 拼音输入法
├── data/              # 词库
├── lang/              # 语言文件
├── fonts/             # 字体（需自行放置 TTF）
├── drawings/          # 用户文件
├── tools/             # 工具脚本
├── bin/               # 启动/停止脚本 + fbink 放置点
└── kual/              # KUAL 扩展（menu.json / config.xml）
```

## 排错

启动后点 KUAL 菜单就回主界面 / 没反应，依次检查：

```sh
cat /tmp/kdap.log                      # 看自检结果
ls -l /mnt/us/kdap/bin/start.sh        # 要有 x 权限
ls -l /mnt/us/kdap/bin/fbink           # 要有 x 权限
which fbink; fbink -m "test"           # fbink 可用
which python3; python3 -c "import numpy, PIL"
sh -x /mnt/us/kdap/bin/start.sh        # 手动跑，看卡在哪
```

## 版本

KDAP v1.8（文件格式版本 `0x0108`，兼容 v1.5 `0x0105`）

## License

KDAP 本体：MIT  
FBInk 为 NiLuJe 维护的独立项目，GPLv2 —— 发行时请保留其
`CREDITS` / `LICENSE`（FBInk Kindle 包内附带）。
