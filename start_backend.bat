@echo off
echo =====================================================
echo        股票信号监控系统 - Windows后端启动脚本
echo =====================================================

echo.
echo 检查Python环境...
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo 未找到Python，请先安装Python 3.7+
    pause
    exit /b
)

echo.
echo 检查目录结构...
if not exist backend (
    echo 未找到backend目录，请确保目录结构正确
    pause
    exit /b
)

echo.
echo 检查Python虚拟环境...
if not exist venv (
    echo 正在创建虚拟环境...
    python -m venv venv
    echo 虚拟环境创建成功
) else (
    echo 使用已存在的虚拟环境
)

echo.
echo 激活虚拟环境...
call venv\Scripts\activate.bat

echo.
echo 安装后端依赖...
pip install -r backend\requirements.txt

echo.
echo 启动后端服务...
echo 后端服务将在 http://localhost:5001 运行
echo 按 Ctrl+C 停止服务
cd backend && python api.py 