#!/bin/bash

# 设置颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=======================================================${NC}"
echo -e "${BLUE}       股票信号监控系统 - 后端启动脚本                ${NC}"
echo -e "${BLUE}=======================================================${NC}"

# 检查Python环境
echo -e "\n${GREEN}检查Python环境...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}未找到Python3，请先安装Python 3.7+${NC}"
    exit 1
fi

# 检查目录结构
if [ ! -d "backend" ]; then
    echo -e "${RED}未找到backend目录，请确保目录结构正确${NC}"
    exit 1
fi

# 检查虚拟环境
echo -e "\n${GREEN}检查Python虚拟环境...${NC}"
if [ ! -d "venv" ]; then
    echo -e "${GREEN}正在创建虚拟环境...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}虚拟环境创建成功${NC}"
else
    echo -e "${GREEN}使用已存在的虚拟环境${NC}"
fi

# 激活虚拟环境
echo -e "\n${GREEN}激活虚拟环境...${NC}"
source venv/bin/activate

# 安装后端依赖
echo -e "\n${GREEN}安装后端依赖...${NC}"
pip install -r backend/requirements.txt

# 启动后端服务
echo -e "\n${GREEN}启动后端服务...${NC}"
echo -e "${BLUE}后端服务将在 http://localhost:5001 运行${NC}"
echo -e "${BLUE}按 Ctrl+C 停止服务${NC}"
cd backend && python api.py 