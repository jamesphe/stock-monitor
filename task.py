import time
import schedule
import logging
from datetime import datetime, time as dtime
from monitor import (
    load_config, 
    evaluate_rules, 
    send_wecom
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("monitor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("stock_monitor")

def is_trading_time():
    """判断当前是否是交易时间"""
    now = datetime.now()
    weekday = now.weekday()
    
    # 周末不是交易日
    if weekday >= 5:  # 5是星期六，6是星期日
        return False
    
    current_time = now.time()
    morning_start = dtime(9, 30)
    morning_end = dtime(11, 30)
    afternoon_start = dtime(13, 0)
    afternoon_end = dtime(15, 0)
    
    # 判断是否在交易时间段内
    is_morning_session = morning_start <= current_time <= morning_end
    is_afternoon_session = afternoon_start <= current_time <= afternoon_end
    
    return is_morning_session or is_afternoon_session

def check_signals():
    """检查所有股票的信号并发送通知"""
    logger.info("开始检查股票信号...")
    
    # 非交易时间不检查
    if not is_trading_time():
        logger.info("当前不是交易时间，跳过检查")
        return
    
    config = load_config()
    
    # 如果没有配置股票，则退出
    if not config.get("stocks"):
        logger.info("没有配置监控的股票，跳过检查")
        return
    
    # 如果没有配置webhook，则只记录不发送
    webhook_url = config.get("wecom_webhook", "")
    
    # 评估所有规则
    results = evaluate_rules(config)
    
    if results and results.get("signals"):
        signals = results.get("signals", [])
        logger.info(f"检测到 {len(signals)} 个信号")
        
        # 发送企业微信通知
        if webhook_url:
            for signal in signals:
                stock_code = signal.get("code", "")
                stock_name = signal.get("name", "")
                message = signal.get("message", "")
                
                title = f"股票信号提醒: {stock_name or stock_code}"
                content = (f"{title}\n\n{message}\n\n"
                          f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                try:
                    send_wecom(webhook_url, content)
                    logger.info(f"已发送通知: {stock_code} - {message}")
                except Exception as e:
                    logger.error(f"发送通知失败: {e}")
        else:
            logger.warning("未配置企业微信Webhook，无法发送通知")
    else:
        logger.info("未检测到任何信号")

def run_scheduler():
    """启动定时任务"""
    logger.info("启动定时任务调度器...")
    
    # 交易时间内每5分钟检查一次
    schedule.every(5).minutes.do(check_signals)
    
    # 每天开盘前检查一次
    schedule.every().day.at("09:25").do(check_signals)
    
    # 每天收盘后检查一次
    schedule.every().day.at("15:05").do(check_signals)
    
    logger.info("定时任务已启动，等待执行...")
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    # 启动时先执行一次检查
    check_signals()
    
    # 启动定时任务
    run_scheduler() 