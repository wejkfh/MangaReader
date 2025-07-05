# 增强版漫画阅读器 - PowerShell打包脚本
# 支持Windows PowerShell和PowerShell Core

# 设置控制台编码为UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "增强版漫画阅读器 - PowerShell打包脚本" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# 检查Python是否安装
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }
    Write-Host "✓ 检测到Python环境: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "✗ 错误：未找到Python环境" -ForegroundColor Red
    Write-Host "请先安装Python 3.7或更高版本" -ForegroundColor Yellow
    Write-Host "下载地址：https://www.python.org/downloads/" -ForegroundColor Yellow
    Read-Host "按回车键退出"
    exit 1
}

# 检查源文件是否存在
if (-not (Test-Path "manga_reader_enhanced.py")) {
    Write-Host "✗ 错误：找不到源文件 manga_reader_enhanced.py" -ForegroundColor Red
    Write-Host "请确保在正确的目录中运行此脚本" -ForegroundColor Yellow
    Read-Host "按回车键退出"
    exit 1
}

Write-Host "✓ 找到源文件: manga_reader_enhanced.py" -ForegroundColor Green
Write-Host ""

# 检查并安装依赖
Write-Host "检查依赖包..." -ForegroundColor Yellow

# 检查Pillow
try {
    python -c "import PIL; print(f'Pillow {PIL.__version__}')" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Pillow已安装" -ForegroundColor Green
    } else {
        throw "Pillow not found"
    }
}
catch {
    Write-Host "正在安装Pillow..." -ForegroundColor Yellow
    python -m pip install Pillow>=8.0.0
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Pillow安装失败" -ForegroundColor Red
        Read-Host "按回车键退出"
        exit 1
    }
    Write-Host "✓ Pillow安装成功" -ForegroundColor Green
}

# 检查PyInstaller
try {
    python -c "import PyInstaller; print(f'PyInstaller {PyInstaller.__version__}')" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ PyInstaller已安装" -ForegroundColor Green
    } else {
        throw "PyInstaller not found"
    }
}
catch {
    Write-Host "正在安装PyInstaller..." -ForegroundColor Yellow
    python -m pip install pyinstaller>=5.0.0
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ PyInstaller安装失败" -ForegroundColor Red
        Read-Host "按回车键退出"
        exit 1
    }
    Write-Host "✓ PyInstaller安装成功" -ForegroundColor Green
}

Write-Host ""
Write-Host "开始打包..." -ForegroundColor Yellow

# 运行打包脚本
try {
    python build_exe.py
    if ($LASTEXITCODE -ne 0) {
        throw "Build script failed"
    }
}
catch {
    Write-Host "✗ 打包过程中发生错误" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

# 检查打包结果
$exePath = "dist\增强版漫画阅读器\增强版漫画阅读器.exe"
if (Test-Path $exePath) {
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Green
    Write-Host "✓ 打包成功！" -ForegroundColor Green
    Write-Host "可执行文件位置：$(Resolve-Path 'dist\增强版漫画阅读器')" -ForegroundColor Green
    Write-Host "================================================" -ForegroundColor Green
    Write-Host ""
    
    # 询问是否打开输出目录
    $choice = Read-Host "是否要打开输出目录？(Y/N)"
    if ($choice -match "^[Yy].*") {
        try {
            Invoke-Item "dist\增强版漫画阅读器"
        }
        catch {
            Write-Host "无法打开目录，请手动导航到: dist\增强版漫画阅读器" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Red
    Write-Host "✗ 打包失败，未找到可执行文件" -ForegroundColor Red
    Write-Host "================================================" -ForegroundColor Red
}

Write-Host ""
Read-Host "按回车键退出"