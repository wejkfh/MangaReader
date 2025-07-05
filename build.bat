@echo off
chcp 65001 >nul
echo ================================================
echo 增强版漫画阅读器 - 一键打包脚本
echo ================================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Python环境
    echo 请先安装Python 3.7或更高版本
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

echo 检测到Python环境，开始打包...
echo.

REM 运行打包脚本
python build_exe.py

REM 检查打包是否成功
if exist "dist\增强版漫画阅读器\增强版漫画阅读器.exe" (
    echo.
    echo ================================================
    echo 打包成功！
    echo 可执行文件位置：dist\增强版漫画阅读器\
    echo ================================================
    echo.
    echo 是否要打开输出目录？(Y/N)
    set /p choice=
    if /i "%choice%"=="Y" (
        explorer "dist\增强版漫画阅读器"
    )
) else (
    echo.
    echo ================================================
    echo 打包失败，请检查错误信息
    echo ================================================
)

echo.
echo 按任意键退出...
pause >nul