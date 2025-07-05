# 下载地址
https://github.com/wejkfh/MangaReader/releases/tag/release-v1.0.0

# 增强版漫画阅读器

一个功能完整的漫画阅读器，支持图片和视频文件的浏览与播放，提供多种阅读模式和便捷的打包方案。

## 🌟 主要功能

### 核心特性
- **多格式支持**: 支持JPG、PNG、GIF、BMP、WEBP、TIFF等图片格式
- **视频播放**: 支持MP4、AVI、MKV、MOV、WMV、FLV等视频格式
- **文件树导航**: 左侧文件树，可视化目录结构，快速切换子目录
- **全屏高清显示**: 支持全屏模式，最大化图片清晰度
- **智能排序**: 目录按日期排序，文件按数字序号排序

### 阅读模式
- **翻页模式**: 传统的单页浏览体验
- **连续模式**: 多张图片连续显示，类似网页浏览
- **多种对齐**: 宽度对齐、高度对齐、适应窗口

### 操作方式
- **键盘快捷键**: 方向键翻页、F11全屏、Ctrl+O选择目录
- **鼠标操作**: 点击翻页、滚轮滚动、拖拽缩放
- **缩略图预览**: 左侧缩略图面板，快速跳转

## 📋 环境要求

### 运行环境
- **操作系统**: Windows 7/8/10/11
- **Python版本**: Python 3.7 或更高版本
- **内存**: 建议4GB以上
- **磁盘空间**: 至少500MB可用空间

### 依赖包
```bash
# 必需依赖
Pillow>=8.0.0          # 图像处理
tkinter                # GUI界面（Python内置）

# 可选依赖
opencv-python>=4.5.0   # 视频播放功能

# 打包依赖
pyinstaller>=5.0.0     # 生成可执行文件
```

## 🚀 快速开始

### 1. 安装依赖
```bash
# 安装必需依赖
pip install -r requirements.txt

# 可选：安装视频支持
pip install opencv-python
```

### 2. 运行程序
```bash
# 运行增强版（推荐）
python manga_reader_enhanced.py

# 或运行简化版
python manga_reader_simple.py
```

### 3. 使用说明
1. 点击"选择目录"按钮选择漫画文件夹
2. 使用左侧文件树导航不同目录
3. 通过快捷键或鼠标操作浏览图片
4. 按F11进入全屏模式获得最佳阅读体验

## 📦 打包为可执行文件

项目提供了多种打包方案，生成独立的exe文件，无需Python环境即可运行。

### 一键打包（推荐）

#### Windows批处理（新手推荐）
```bash
# 双击运行
build.bat
```

#### PowerShell脚本（高级用户）
```powershell
# 右键选择"使用PowerShell运行"
.\build.ps1
```

#### Python脚本（手动控制）
```bash
# 完整功能版本
python build_exe.py

# 简化版本（推荐）
python build_simple.py
```

### 打包输出
打包完成后，在`dist`目录下生成：
```
dist/
└── 增强版漫画阅读器/
    ├── 增强版漫画阅读器.exe    # 主程序
    ├── 使用说明.txt            # 用户说明
    └── _internal/              # 依赖文件（不要删除）
```

### 常见问题
- **pathlib冲突**: 脚本会自动检测并处理
- **内存不足**: 使用简化版打包脚本
- **杀毒软件误报**: 将输出目录添加到白名单

## 📁 项目文件结构

### 核心文件
```
├── manga_reader_enhanced.py    # 增强版主程序 ⭐
├── manga_reader_simple.py      # 简化版程序
├── manga_reader.py             # 基础版程序
└── requirements.txt            # 依赖列表
```

### 打包相关
```
├── build_simple.py             # 简化打包脚本 ⭐
├── build_exe.py                # 完整打包脚本
├── build.bat                   # Windows批处理
├── build.ps1                   # PowerShell脚本
└── 打包说明.md                 # 详细打包指南
```

### 文档
```
├── README.md                   # 项目说明
├── README_GIT.md              # Git仓库说明 ⭐
└── 打包说明.md                 # 打包详细指南
```

## 🔧 Git仓库管理

### 推荐上传的文件

#### 必需文件 ✅
```
├── manga_reader_enhanced.py    # 主程序
├── manga_reader_simple.py      # 简化版
├── requirements.txt            # 依赖
├── README_GIT.md              # 项目说明
├── build_simple.py             # 推荐的打包脚本
├── build.bat                   # 批处理脚本
├── build.ps1                   # PowerShell脚本
└── 打包说明.md                 # 打包指南
```

#### 可选文件 ⚪
```
├── manga_reader.py             # 基础版（可选）
├── build_exe.py                # 完整打包脚本（可选）
└── README.md                   # 原始说明（可选）
```

#### 忽略文件 ❌
```
├── build/                      # 构建临时文件
├── dist/                       # 打包输出
├── __pycache__/               # Python缓存
├── *.spec                      # PyInstaller规格文件
├── *.pyc                       # 编译文件
└── .DS_Store                   # 系统文件
```

### Git操作步骤

#### 1. 初始化仓库
```bash
# 在项目目录中初始化Git仓库
cd h:\files\manga\1
git init
```

#### 2. 创建.gitignore文件
```bash
# 创建忽略文件
echo "# 构建文件" > .gitignore
echo "build/" >> .gitignore
echo "dist/" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo "*.pyo" >> .gitignore
echo "*.spec" >> .gitignore
echo ".DS_Store" >> .gitignore
echo "Thumbs.db" >> .gitignore
echo "*.log" >> .gitignore
```

#### 3. 添加文件到仓库
```bash
# 添加推荐的文件
git add manga_reader_enhanced.py
git add manga_reader_simple.py
git add requirements.txt
git add README_GIT.md
git add build_simple.py
git add build.bat
git add build.ps1
git add 打包说明.md
git add .gitignore

# 或者添加所有文件（会自动忽略.gitignore中的文件）
git add .
```

#### 4. 提交更改
```bash
# 首次提交
git commit -m "初始提交：增强版漫画阅读器"

# 后续提交
git commit -m "更新功能：添加新特性"
```

#### 5. 连接远程仓库
```bash
# 添加远程仓库（替换为你的仓库地址）
git remote add origin https://github.com/yourusername/manga-reader.git

# 推送到远程仓库
git push -u origin main
```

#### 6. 日常操作
```bash
# 检查状态
git status

# 查看更改
git diff

# 添加更改
git add .

# 提交更改
git commit -m "描述你的更改"

# 推送到远程
git push
```

### 分支管理建议

```bash
# 创建开发分支
git checkout -b develop

# 创建功能分支
git checkout -b feature/new-feature

# 合并分支
git checkout main
git merge feature/new-feature

# 删除已合并的分支
git branch -d feature/new-feature
```

## 📝 版本历史

- **v1.0.0**: 基础漫画阅读功能
- **v2.0.0**: 增加视频播放支持
- **v3.0.0**: 添加文件树导航和全屏模式
- **v3.1.0**: 优化连续阅读模式
- **v3.2.0**: 完善打包方案和Git支持

## 🤝 贡献指南

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🆘 技术支持

如果遇到问题：
1. 查看 [打包说明.md](打包说明.md) 了解详细的故障排除
2. 检查 [Issues](https://github.com/yourusername/manga-reader/issues) 中的已知问题
3. 创建新的 Issue 描述你遇到的问题

## 🎯 未来计划

- [ ] 添加书签功能
- [ ] 支持更多图片格式
- [ ] 添加主题切换
- [ ] 优化内存使用
- [ ] 添加插件系统
- [ ] 支持云端同步

---

**注意**: 本项目主要针对Windows系统优化，其他系统可能需要额外配置。