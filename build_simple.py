#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版漫画阅读器 - 简化打包脚本
避免pathlib冲突，使用最基本的PyInstaller命令
"""

import os
import sys
import subprocess
import shutil
from datetime import datetime

def check_requirements():
    """检查基本要求"""
    print("检查打包环境...")
    
    # 检查源文件
    if not os.path.exists("manga_reader_enhanced.py"):
        print("✗ 错误：找不到源文件 manga_reader_enhanced.py")
        return False
    print("✓ 找到源文件")
    
    # 检查PyInstaller
    try:
        result = subprocess.run([sys.executable, "-c", "import PyInstaller; print(PyInstaller.__version__)"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ PyInstaller已安装: {result.stdout.strip()}")
        else:
            print("正在安装PyInstaller...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✓ PyInstaller安装完成")
    except Exception as e:
        print(f"✗ PyInstaller检查失败: {e}")
        return False
    
    # 检查Pillow
    try:
        result = subprocess.run([sys.executable, "-c", "import PIL; print(PIL.__version__)"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Pillow已安装: {result.stdout.strip()}")
        else:
            print("正在安装Pillow...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
            print("✓ Pillow安装完成")
    except Exception as e:
        print(f"✗ Pillow检查失败: {e}")
        return False
    
    return True

def clean_previous_build():
    """清理之前的构建文件"""
    print("清理之前的构建文件...")
    
    dirs_to_clean = ["build", "dist", "__pycache__"]
    files_to_clean = ["*.spec"]
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"✓ 已删除 {dir_name}")
    
    # 删除spec文件
    import glob
    for spec_file in glob.glob("*.spec"):
        os.remove(spec_file)
        print(f"✓ 已删除 {spec_file}")

def build_with_pyinstaller():
    """使用PyInstaller构建"""
    print("开始构建可执行文件...")
    
    # 使用最简单的命令，避免复杂配置
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onedir",  # 单目录模式
        "--windowed",  # 无控制台
        "--name=MangaReader",  # 使用英文名避免编码问题
        "--noconfirm",
        "--clean",
        "manga_reader_enhanced.py"
    ]
    
    print(f"执行命令: {' '.join(cmd)}")
    print("这可能需要几分钟时间，请耐心等待...")
    
    try:
        # 直接运行，显示实时输出
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                 text=True, encoding='utf-8', errors='ignore')
        
        # 实时显示输出
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        
        return_code = process.poll()
        
        if return_code == 0:
            print("\n✓ 构建成功！")
            return True
        else:
            print(f"\n✗ 构建失败，退出码: {return_code}")
            return False
            
    except Exception as e:
        print(f"\n✗ 构建过程中发生异常: {e}")
        return False

def post_build_setup():
    """构建后设置"""
    print("\n进行构建后设置...")
    
    # 检查输出文件
    exe_path = "dist/MangaReader/MangaReader.exe"
    if not os.path.exists(exe_path):
        print("✗ 未找到生成的可执行文件")
        return False
    
    # 重命名为中文名（在文件夹内操作）
    try:
        dist_dir = "dist/MangaReader"
        new_exe_path = os.path.join(dist_dir, "增强版漫画阅读器.exe")
        os.rename(exe_path, new_exe_path)
        print("✓ 已重命名可执行文件")
    except Exception as e:
        print(f"⚠️  重命名失败，但不影响使用: {e}")
        new_exe_path = exe_path
    
    # 创建使用说明
    readme_content = f"""# 增强版漫画阅读器

## 使用方法
1. 双击运行可执行文件
2. 点击"选择目录"选择漫画文件夹
3. 使用方向键或鼠标翻页

## 快捷键
- 方向键：翻页
- F11：全屏
- Ctrl+O：选择目录
- 鼠标滚轮：翻页

## 支持格式
- 图片：JPG, PNG, GIF, BMP, WEBP, TIFF
- 视频：MP4, AVI, MKV, MOV, WMV, FLV

构建时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    try:
        readme_path = os.path.join(dist_dir, "使用说明.txt")
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print("✓ 已创建使用说明")
    except Exception as e:
        print(f"⚠️  创建说明文件失败: {e}")
    
    print(f"\n✓ 打包完成！")
    print(f"输出目录: {os.path.abspath(dist_dir)}")
    
    return True

def main():
    """主函数"""
    print("=" * 60)
    print("增强版漫画阅读器 - 简化打包脚本")
    print("=" * 60)
    
    try:
        # 检查环境
        if not check_requirements():
            return False
        
        # 清理旧文件
        clean_previous_build()
        
        # 构建
        if not build_with_pyinstaller():
            return False
        
        # 后处理
        if not post_build_setup():
            return False
        
        print("\n" + "=" * 60)
        print("🎉 打包成功完成！")
        print("=" * 60)
        
        return True
        
    except KeyboardInterrupt:
        print("\n用户取消操作")
        return False
    except Exception as e:
        print(f"\n发生未预期的错误: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n打包失败，请检查错误信息")
    
    input("\n按回车键退出...")