#!/bin/bash

# 设置颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=======================================================${NC}"
echo -e "${BLUE}       股票信号监控系统 - 安装和启动脚本              ${NC}"
echo -e "${BLUE}=======================================================${NC}"

# 检查Python环境
echo -e "\n${GREEN}检查Python环境...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}未找到Python3，请先安装Python 3.7+${NC}"
    exit 1
fi

# 检查pip
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}未找到pip3，请先安装pip${NC}"
    exit 1
fi

# 检查目录结构
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo -e "${RED}未找到backend或frontend目录，请确保目录结构正确${NC}"
    exit 1
fi

# 检查Node.js环境
echo -e "\n${GREEN}检查Node.js环境...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${RED}未找到Node.js，前端部分需要Node.js 14+${NC}"
    echo -e "${RED}请从 https://nodejs.org 下载安装${NC}"
    
    # 询问是否继续仅安装后端
    read -p "是否继续安装后端部分? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
    SKIP_FRONTEND=true
else
    # 检查npm
    if ! command -v npm &> /dev/null; then
        echo -e "${RED}未找到npm，请检查Node.js安装${NC}"
        SKIP_FRONTEND=true
    fi
    
    # 显示版本信息
    echo -e "Node.js版本: $(node -v)"
    echo -e "npm版本: $(npm -v)"
fi

# 创建Python虚拟环境
echo -e "\n${GREEN}创建Python虚拟环境...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}虚拟环境创建成功${NC}"
else
    echo -e "${GREEN}虚拟环境已存在${NC}"
fi

# 激活虚拟环境
echo -e "\n${GREEN}激活虚拟环境...${NC}"
source venv/bin/activate

# 安装后端依赖
echo -e "\n${GREEN}安装后端依赖...${NC}"
pip install -r backend/requirements.txt

# 安装前端依赖和构建
if [ "$SKIP_FRONTEND" != true ]; then
    echo -e "\n${GREEN}安装前端依赖...${NC}"
    cd frontend
    npm install
    
    echo -e "\n${GREEN}构建前端...${NC}"
    npm run build
    
    cd ..
    
    # 检查前端构建结果
    if [ -d "frontend-dist" ]; then
        echo -e "${GREEN}前端构建成功${NC}"
    else
        echo -e "${RED}前端构建失败或构建目录不存在${NC}"
    fi
else
    echo -e "\n${BLUE}跳过前端构建${NC}"
fi

# 启动后端服务
echo -e "\n${GREEN}启动后端服务...${NC}"
echo -e "${BLUE}后端服务将在 http://localhost:5001 运行${NC}"
echo -e "${BLUE}按 Ctrl+C 停止服务${NC}"
cd backend && python api.py 