import subprocess
import sys
import time
import webbrowser
import argparse


def print_banner():
    """打印启动banner"""
    banner = """
    ┌─────────────────────────────────────────────┐
    │                                             │
    │       股票信号监控系统                      │
    │                                             │
    │       Alpine.js + TailwindCSS + Flask       │
    │                                             │
    └─────────────────────────────────────────────┘
    """
    print(banner)


def start_api_server():
    """启动API服务器"""
    print("正在启动API服务器...")
    api_process = subprocess.Popen(
        [sys.executable, "api.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return api_process


def start_scheduler():
    """启动定时任务"""
    print("正在启动定时任务...")
    scheduler_process = subprocess.Popen(
        [sys.executable, "task.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return scheduler_process


def open_browser():
    """打开浏览器"""
    print("正在打开浏览器...")
    webbrowser.open("http://localhost:8080")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="启动股票信号监控系统")
    parser.add_argument("--no-browser", action="store_true", help="不自动打开浏览器")
    parser.add_argument("--api-only", action="store_true", help="仅启动API服务器")
    parser.add_argument("--task-only", action="store_true", help="仅启动定时任务")
    args = parser.parse_args()
    
    print_banner()
    
    api_process = None
    scheduler_process = None
    
    try:
        # 启动API服务器
        if not args.task_only:
            api_process = start_api_server()
            print("API服务器启动成功，访问 http://localhost:8080")
            
            # 等待服务器启动完成
            time.sleep(2)
            
            # 自动打开浏览器
            if not args.no_browser:
                open_browser()
        
        # 启动定时任务
        if not args.api_only:
            scheduler_process = start_scheduler()
            print("定时任务启动成功")
        
        # 保持程序运行
        print("\n按Ctrl+C退出程序...\n")
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n正在关闭服务...")
        
        # 关闭进程
        if api_process:
            api_process.terminate()
        
        if scheduler_process:
            scheduler_process.terminate()
        
        print("服务已关闭")


if __name__ == "__main__":
    main() 