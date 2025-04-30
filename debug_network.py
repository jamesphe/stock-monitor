#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import requests
import sys
import os
import subprocess
import platform
import json
import logging
from urllib.parse import urlparse

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("network_debug")


def check_port_open(host, port):
    """检查指定主机的端口是否开放"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0


def check_server_running():
    """检查Flask服务器是否正在运行"""
    # 检查本地5000端口是否开放
    if check_port_open("localhost", 5000):
        logger.info("✅ 检测到5000端口已开放，服务器可能正在运行")
        return True
    else:
        logger.warning("❌ 5000端口未开放，服务器可能未启动")
        return False


def check_network_connectivity():
    """检查网络连接状态"""
    try:
        # 尝试访问百度，检查互联网连接
        response = requests.get("https://www.baidu.com", timeout=5)
        if response.status_code == 200:
            logger.info("✅ 网络连接正常")
            return True
        else:
            logger.warning(f"⚠️ 网络连接异常，状态码: {response.status_code}")
            return False
    except requests.RequestException as e:
        logger.error(f"❌ 网络连接失败: {e}")
        return False


def run_ping(host):
    """对指定主机执行ping命令"""
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "4", host]
    try:
        output = subprocess.check_output(command).decode("utf-8")
        logger.info(f"Ping {host} 结果:\n{output}")
        return True
    except subprocess.CalledProcessError:
        logger.error(f"❌ 无法ping通 {host}")
        return False


def test_api_endpoint(url="http://localhost:5000/api/test"):
    """测试API端点"""
    logger.info(f"正在测试API端点: {url}")
    
    parsed_url = urlparse(url)
    host = parsed_url.netloc.split(":")[0]
    
    # 检查DNS解析
    try:
        ip = socket.gethostbyname(host)
        logger.info(f"✅ DNS解析成功: {host} -> {ip}")
    except socket.gaierror:
        logger.error(f"❌ DNS解析失败: {host}")
    
    # 检查端口
    port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)
    if check_port_open(host, port):
        logger.info(f"✅ 端口检查成功: {host}:{port} 开放")
    else:
        logger.error(f"❌ 端口检查失败: {host}:{port} 未开放")
    
    # 测试API
    try:
        headers = {
            "User-Agent": "NetworkDebugScript/1.0",
            "Origin": "http://localhost:8000"  # 模拟跨域请求
        }
        response = requests.get(url, headers=headers, timeout=5)
        
        logger.info(f"API响应状态码: {response.status_code}")
        logger.info(f"API响应头: {json.dumps(dict(response.headers), indent=2)}")
        
        if response.status_code == 200:
            logger.info(f"✅ API测试成功: {url}")
            logger.info(f"响应内容: {response.text[:200]}...")
            return True
        else:
            logger.error(f"❌ API测试失败: {url}, 状态码: {response.status_code}")
            if response.text:
                logger.info(f"响应内容: {response.text[:200]}...")
            return False
    except requests.RequestException as e:
        logger.error(f"❌ API请求异常: {e}")
        return False


def check_cors_headers(url="http://localhost:5000/api/test"):
    """检查API响应是否包含CORS头"""
    logger.info(f"正在检查CORS配置: {url}")
    
    # 模拟OPTIONS预检请求
    try:
        headers = {
            "Origin": "http://example.com",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Content-Type"
        }
        response = requests.options(url, headers=headers, timeout=5)
        
        logger.info(f"预检请求状态码: {response.status_code}")
        logger.info(f"预检请求响应头: {json.dumps(dict(response.headers), indent=2)}")
        
        # 检查关键CORS头
        cors_headers = [
            "Access-Control-Allow-Origin",
            "Access-Control-Allow-Methods",
            "Access-Control-Allow-Headers"
        ]
        
        all_headers_present = True
        for header in cors_headers:
            if header in response.headers:
                logger.info(f"✅ 存在CORS头: {header}={response.headers[header]}")
            else:
                logger.warning(f"❌ 缺少CORS头: {header}")
                all_headers_present = False
        
        return all_headers_present
    except requests.RequestException as e:
        logger.error(f"❌ CORS检查请求异常: {e}")
        return False


def check_flask_server_logs():
    """检查Flask服务器日志"""
    log_files = ["api.log", "monitor.log"]
    for log_file in log_files:
        if os.path.exists(log_file):
            logger.info(f"找到日志文件: {log_file}")
            try:
                # 读取最后20行
                with open(log_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    last_lines = lines[-20:] if len(lines) > 20 else lines
                    logger.info(f"{log_file} 最后{len(last_lines)}行:")
                    for line in last_lines:
                        print(f"  {line.strip()}")
            except Exception as e:
                logger.error(f"读取日志文件失败: {e}")
        else:
            logger.warning(f"未找到日志文件: {log_file}")


def main():
    """主函数"""
    logger.info("===== 开始网络和API诊断 =====")
    logger.info(f"操作系统: {platform.system()} {platform.release()}")
    
    # 检查网络连接
    check_network_connectivity()
    
    # Ping本地和远程服务器
    run_ping("localhost")
    run_ping("baidu.com")
    
    # 检查服务器状态
    server_running = check_server_running()
    
    if server_running:
        # 测试API基本功能
        test_api_endpoint()
        
        # 检查CORS配置
        check_cors_headers()
    else:
        logger.warning("因为服务器未运行，跳过API测试")
        
        # 提供启动服务器的建议
        logger.info("建议执行以下命令启动服务器:")
        logger.info("  python api.py")
        logger.info("或者:")
        logger.info("  python start.py --api-only")
    
    # 检查日志
    logger.info("\n===== 检查服务器日志 =====")
    check_flask_server_logs()
    
    logger.info("\n===== 诊断结束 =====")
    
    # 提供进一步的解决建议
    logger.info("\n===== 解决方案建议 =====")
    if not server_running:
        logger.info("1. 首先确保API服务器正在运行")
        logger.info("2. 检查启动日志是否有错误信息")
        logger.info("3. 确认服务器正在监听0.0.0.0（所有网络接口）而不仅是127.0.0.1")
    else:
        logger.info("1. 确认已安装flask-cors依赖: pip install flask-cors")
        logger.info("2. 重启API服务器以应用CORS配置")
        logger.info("3. 在浏览器中打开调试工具（F12），查看网络请求的详细信息")
        logger.info("4. 确保前端代码中的API URL与服务器地址匹配")
    
    logger.info("5. 尝试使用debug.html页面进行更详细的API测试")


if __name__ == "__main__":
    main() 