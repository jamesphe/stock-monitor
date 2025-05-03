@echo off
echo =====================================================
echo        股票信号监控系统 - Windows安装和启动脚本
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
if not exist frontend (
    echo 未找到frontend目录，请确保目录结构正确
    pause
    exit /b
)

echo.
echo 检查Node.js环境...
where node >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo 未找到Node.js，前端部分需要Node.js 14+
    echo 请从 https://nodejs.org 下载安装
    
    echo 是否继续安装后端部分?
    set /p CONTINUE=输入y继续，其他键退出: 
    if /i not "%CONTINUE%"=="y" (
        pause
        exit /b
    )
    set SKIP_FRONTEND=true
) else (
    where npm >nul 2>nul
    if %ERRORLEVEL% neq 0 (
        echo 未找到npm，请检查Node.js安装
        set SKIP_FRONTEND=true
    ) else (
        echo Node.js版本:
        node -v
        echo npm版本:
        npm -v
    )
)

echo.
echo 创建Python虚拟环境...
if not exist venv (
    python -m venv venv
    echo 虚拟环境创建成功
) else (
    echo 虚拟环境已存在
)

echo.
echo 激活虚拟环境...
call venv\Scripts\activate.bat

echo.
echo 安装后端依赖...
pip install -r backend\requirements.txt

if not defined SKIP_FRONTEND (
    echo.
    echo 安装前端依赖...
    cd frontend
    call npm install
    
    echo.
    echo 构建前端...
    call npm run build
    
    cd ..
    
    if exist frontend-dist (
        echo 前端构建成功
    ) else (
        echo 前端构建失败或构建目录不存在
    )
) else (
    echo.
    echo 跳过前端构建
)

echo.
echo 启动后端服务...
echo 后端服务将在 http://localhost:5001 运行
echo 按 Ctrl+C 停止服务
cd backend && python api.py 