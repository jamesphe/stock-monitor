"""
股票监控系统 - 重构版本

使用基于规则的设计模式实现，更加灵活和易于扩展
"""

import json
import time
import datetime
import logging
import requests
import pandas as pd
import pandas_ta as ta
from typing import Dict, List, Any

# 导入规则相关模块
from rules.rule_evaluator import RuleEvaluator
from rules.price_rule import PriceAboveRule
from rules.volume_rule import VolumeAboveRule
from rules.rule_factory import RuleFactory

# 确保所有布尔值转换为可序列化的格式
# 递归处理字典中的布尔值
def convert_booleans(obj):
    """
    递归地将对象中的所有布尔值转换为整数(1/0)
    确保JSON序列化不会出错
    
    Args:
        obj: 任意对象，可以是布尔值、字典、列表或其他类型
        
    Returns:
        转换后的对象，布尔值会被转换为整数
    """
    if isinstance(obj, bool):
        return 1 if obj else 0
    elif isinstance(obj, dict):
        return {k: convert_booleans(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_booleans(i) for i in obj]
    return obj

# 尝试导入akshare，如果失败则使用备选数据源
try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    print("警告: akshare库导入失败，将使用备选数据源")
    AKSHARE_AVAILABLE = False

# 数据缓存，避免重复请求
DATA_CACHE = {}
CACHE_EXPIRE_TIME = 300  # 缓存有效期5分钟


def check_price_above(df: pd.DataFrame, price_level: float, 
                      consecutive_bars: int = 1) -> bool:
    """
    检查价格是否连续若干个周期高于指定水平
    
    Args:
        df: 包含行情数据的DataFrame
        price_level: 价格阈值
        consecutive_bars: 连续周期数
        
    Returns:
        bool: 是否满足价格高于条件
    """
    # 使用PriceAboveRule中的方法避免代码重复
    params = {"price_level": price_level, "consecutive_bars": consecutive_bars}
    rule = PriceAboveRule(params)
    return rule._check_price_above(df)


def check_volume_above(df: pd.DataFrame, volume_multiple: float, 
                       lookback: int = 5) -> bool:
    """
    检查当前成交量是否高于过去N个周期平均成交量的M倍
    
    Args:
        df: 包含行情数据的DataFrame
        volume_multiple: 成交量倍数阈值
        lookback: 回溯周期数
        
    Returns:
        bool: 是否满足成交量条件
    """
    # 使用VolumeAboveRule中的方法避免代码重复
    params = {"volume_multiple": volume_multiple, "lookback": lookback}
    rule = VolumeAboveRule(params)
    return rule._check_volume_above(df)


def setup_logging():
    """配置日志系统"""
    logger = logging.getLogger("monitor")
    
    # 如果已经有处理器，不要重复添加
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.INFO)
    
    # 创建控制台处理器
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    # 设置格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    ch.setFormatter(formatter)
    
    # 添加处理器
    logger.addHandler(ch)
    
    return logger


def load_config(config_path="monitor_config.json"):
    """加载配置文件"""
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        # 如果文件不存在，返回默认配置
        return {"wecom_webhook": "", "stocks": []}


def save_config(config, config_path="monitor_config.json"):
    """保存配置文件"""
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def send_wecom(webhook_url, content):
    """发送企业微信机器人消息
    
    Args:
        webhook_url: 企业微信机器人webhook地址
        content: 要发送的文本内容
    
    Returns:
        bool: 是否发送成功
    """
    if not webhook_url:
        print("企业微信Webhook地址未配置")
        return False
    
    headers = {'Content-Type': 'application/json'}
    data = {
        "msgtype": "markdown",
        "markdown": {
            "content": content
        }
    }
    
    try:
        response = requests.post(webhook_url, headers=headers, json=data)
        result = response.json()
        
        if result.get('errcode') == 0:
            return True
        else:
            print(f"发送企业微信消息失败: {result}")
            return False
            
    except Exception as e:
        print(f"发送企业微信消息异常: {e}")
        return False


def fetch_data_alternative(stock_code, period="daily", count=120):
    """备选的股票数据获取方法
    
    当akshare不可用时使用此方法。使用新浪财经等公开API。
    """
    try:
        print(f"使用备选数据源获取 {stock_code} 的{period}数据")
        
        # 解析股票代码
        if stock_code.startswith(('sh', 'sz')):
            market = stock_code[:2]
            code = stock_code[2:]
        else:
            # 默认添加市场前缀
            code = stock_code
            if stock_code.startswith('6'):
                market = 'sh'
            elif stock_code.startswith(('0', '3')):
                market = 'sz'
            else:
                # 指数等其他情况
                market = 'sh' if stock_code.startswith('0') else 'sz'
        
        full_code = f"{market}{code}"
        print(f"完整股票代码: {full_code}")
        
        if period == "daily":
            # 使用新浪财经API获取日线数据
            url = (f"https://money.finance.sina.com.cn/quotes_service/api/"
                   f"json_v2.php/CN_MarketData.getKLineData?symbol={full_code}"
                   f"&scale=240&ma=no&datalen={count}")
            print(f"请求URL: {url}")
            
            response = requests.get(url)
            print(f"响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"获取到{len(data)}条数据记录")
                print(f"数据示例: {data[0] if data else '空数据'}")
                
                df = pd.DataFrame(data)
                
                # 转换数据类型
                df['day'] = pd.to_datetime(df['day'])
                df['open'] = df['open'].astype(float)
                df['high'] = df['high'].astype(float)
                df['low'] = df['low'].astype(float)
                df['close'] = df['close'].astype(float)
                df['volume'] = df['volume'].astype(float)
                
                # 重命名列以保持一致性
                df = df.rename(columns={"day": "date"})
                print(f"处理后的列名: {df.columns.tolist()}")
                
                # 计算RSI指标
                df['rsi'] = ta.rsi(df['close'], length=14)
                
                return df
            else:
                print(f"获取股票 {stock_code} 数据失败: HTTP {response.status_code}")
                print(f"响应内容: {response.text[:200]}...")
                return None
                
        elif period in ["1min", "5min"]:
            # 分钟线数据获取比较复杂，这里提供一个简化的版本
            scale = "5" if period == "5min" else "1"
            url = (f"https://quotes.sina.cn/cn/api/jsonp_v2.php/=/"
                   f"CN_MarketDataService.getKLineData?symbol={full_code}"
                   f"&scale={scale}&datalen={count}")
            print(f"请求URL: {url}")
            
            response = requests.get(url)
            print(f"响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                # 处理JSONP响应
                text = response.text
                print(f"响应前30字符: {text[:30]}...")
                
                json_start = text.find('(') + 1
                json_end = text.rfind(')')
                json_str = text[json_start:json_end]
                
                data = json.loads(json_str)
                print(f"获取到{len(data)}条数据记录")
                print(f"数据示例: {data[0] if data else '空数据'}")
                
                df = pd.DataFrame(data)
                
                # 转换数据类型
                df['day'] = pd.to_datetime(df['day'])
                df['open'] = df['open'].astype(float)
                df['high'] = df['high'].astype(float)
                df['low'] = df['low'].astype(float)
                df['close'] = df['close'].astype(float)
                df['volume'] = df['volume'].astype(float)
                
                # 重命名列以保持一致性
                df = df.rename(columns={"day": "date"})
                print(f"处理后的列名: {df.columns.tolist()}")
                
                # 计算RSI指标
                df['rsi'] = ta.rsi(df['close'], length=14)
                
                # 处理不合理的未来日期问题
                if 'date' in df.columns:
                    # 确保日期数据是合理的
                    today = datetime.datetime.now()
                    
                    # 检查数据中是否有异常日期
                    min_date = df['date'].min()
                    max_date = df['date'].max()
                    date_range = (max_date - min_date).days
                    
                    print(f"数据日期范围: {min_date} 到 {max_date}，共{date_range}天")
                    
                    # 如果数据跨度不正常（超过2年），可能是日期格式有问题
                    if date_range > 730:  # 约2年
                        print("警告: 数据日期跨度异常大，可能需要检查")
                    
                    # 查找"明显不合理"的未来日期（超过一个季度）
                    extreme_future_dates = df['date'] > today + datetime.timedelta(
                        days=90
                    )
                    if extreme_future_dates.any():
                        print("警告: 发现明显不合理的未来日期，尝试重新解析")
                        
                        # 检查所有日期是否有一致的偏移模式
                        all_years = df['date'].dt.year.unique()
                        if len(all_years) == 1 and all_years[0] != today.year:
                            # 如果所有日期都是同一年且不是当前年，可能只是年份有问题
                            wrong_year = all_years[0]
                            print(f"所有日期都在{wrong_year}年，可能是年份错误")
                            
                            # 只修正年份，保留月日时分秒
                            df['date'] = df['date'].apply(
                                lambda x: x.replace(year=today.year) 
                                if abs(x.year - today.year) > 1 else x
                            )
                        
                        print(f"修正后的日期范围: {df['date'].min()} 到 {df['date'].max()}")
                
                return df
            else:
                print(
                    f"获取股票 {stock_code} 分钟线数据失败: HTTP {response.status_code}"
                )
                print(f"响应内容: {response.text[:200]}...")
                return None
    except Exception as e:
        print(f"备选数据源获取 {stock_code} 数据出错: {e}")
        print(f"错误类型: {type(e).__name__}")
        import traceback
        print(f"详细错误: {traceback.format_exc()}")
        return None


def fetch_data(stock_code, period="daily", count=120):
    """获取股票数据，添加缓存机制减少重复请求
    
    Args:
        stock_code: 股票代码，如 '000001' 或 'sh000001'
        period: 'daily' 或 '1min' 或 '5min'
        count: 获取的数据点数量
    
    Returns:
        pandas.DataFrame: 包含行情数据的DataFrame
    """
    # 生成缓存键
    cache_key = f"{stock_code}_{period}_{count}"
    
    # 检查缓存是否存在且未过期
    current_time = time.time()
    if cache_key in DATA_CACHE:
        cache_time, df = DATA_CACHE[cache_key]
        if current_time - cache_time < CACHE_EXPIRE_TIME:
            print(f"使用缓存数据: {cache_key}")
            return df.copy()  # 返回副本避免修改缓存
    
    # 缓存不存在或已过期，获取新数据
    df = None
    
    # 如果akshare可用，优先使用akshare
    if AKSHARE_AVAILABLE:
        try:
            # 检查股票代码格式
            if stock_code.startswith(('sh', 'sz')):
                code = stock_code
                clean_code = stock_code[2:]
            else:
                # 默认加上市场前缀
                clean_code = stock_code
                if stock_code.startswith('6'):
                    prefix = 'sh'
                elif stock_code.startswith(('0', '3')):
                    prefix = 'sz'
                else:
                    # 指数等其他情况
                    prefix = 'sh' if stock_code.startswith('0') else 'sz'
                code = f"{prefix}{stock_code}"
            
            if period == "daily":
                # 获取日线数据
                print(f"获取 {stock_code} 的日线数据")
                
                try:
                    start_date = (
                        datetime.datetime.now() - 
                        datetime.timedelta(days=count)
                    ).strftime('%Y%m%d')
                    end_date = datetime.datetime.now().strftime('%Y%m%d')
                    
                    df = ak.stock_zh_a_hist(
                        symbol=clean_code, 
                        period="daily", 
                        start_date=start_date,
                        end_date=end_date,
                        adjust="qfq"
                    )
                    
                    # 处理可能的不同列名
                    column_mappings = {
                        "日期": "date", "时间": "date", "date": "date", 
                        "时点": "date", "日期时间": "date",
                        "开盘": "open", "开盘价": "open", "open": "open",
                        "收盘": "close", "收盘价": "close", "close": "close",
                        "最高": "high", "最高价": "high", "high": "high",
                        "最低": "low", "最低价": "low", "low": "low",
                        "成交量": "volume", "成交额": "amount", "volume": "volume"
                    }
                    
                    # 重命名列，保证格式一致
                    for old_col, new_col in column_mappings.items():
                        if old_col in df.columns:
                            df = df.rename(columns={old_col: new_col})
                except Exception as e:
                    print(f"获取日线数据时出错: {e}")
                    return fetch_data_alternative(stock_code, period, count)
                
            elif period in ["1min", "5min"]:
                # 获取分钟线数据
                period_map = {"1min": "1", "5min": "5"}
                
                print(f"获取 {stock_code} 的分钟线数据")
                
                try:
                    df = ak.stock_zh_a_minute(
                        symbol=code, 
                        period=period_map[period]
                    )
                    
                    # 处理可能的不同列名
                    column_mappings = {
                        "日期": "date", "时间": "date", "date": "date", 
                        "时点": "date", "日期时间": "date",
                        "开盘": "open", "开盘价": "open", "open": "open",
                        "收盘": "close", "收盘价": "close", "close": "close",
                        "最高": "high", "最高价": "high", "high": "high",
                        "最低": "low", "最低价": "low", "low": "low",
                        "成交量": "volume", "成交额": "amount", "volume": "volume"
                    }
                    
                    # 重命名列，保证格式一致
                    for old_col, new_col in column_mappings.items():
                        if old_col in df.columns:
                            df = df.rename(columns={old_col: new_col})
                    
                    # 截取最近的记录
                    df = df.iloc[-count:] if len(df) > count else df
                    
                except Exception as e:
                    print(f"获取分钟线数据时出错: {e}")
                    return fetch_data_alternative(stock_code, period, count)
            
            # 确保日期列为datetime类型
            if df is not None and 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                
                # 计算RSI指标
                if 'close' in df.columns and len(df) > 14:
                    df['rsi'] = ta.rsi(df['close'], length=14)
            
                # 保存到缓存
                DATA_CACHE[cache_key] = (current_time, df.copy())
                return df
            else:
                print(f"获取 {stock_code} 数据失败，尝试备选数据源")
                df = fetch_data_alternative(stock_code, period, count)
                if df is not None:
                    DATA_CACHE[cache_key] = (current_time, df.copy())
                return df
        except Exception as e:
            print(f"获取 {stock_code} 数据时出错: {e}")
            df = fetch_data_alternative(stock_code, period, count)
            if df is not None:
                DATA_CACHE[cache_key] = (current_time, df.copy())
            return df
    else:
        # 如果akshare不可用，使用备选数据源
        df = fetch_data_alternative(stock_code, period, count)
        if df is not None:
            DATA_CACHE[cache_key] = (current_time, df.copy())
        return df


def evaluate_rules(config=None):
    """
    评估所有监控规则（重构版本）
    
    Args:
        config: 配置字典，如果为None则自动加载
    
    Returns:
        list: 触发的告警消息列表，包含详细的判断结果
    """
    start_time = time.time()
    logger = setup_logging()
    logger.info("开始评估监控规则 (重构版本)")
    
    if config is None:
        config = load_config()
        logger.debug("从配置文件加载规则")
    else:
        logger.debug("使用传入的规则配置")
    
    webhook_url = config.get("wecom_webhook", "")
    stocks = config.get("stocks", [])
    
    logger.info(f"需要评估 {len(stocks)} 只股票")
    
    evaluator = RuleEvaluator(logger)
    all_alerts = []
    
    for idx, stock in enumerate(stocks):
        stock_start_time = time.time()
        stock_code = stock.get("code", "")
        stock_name = stock.get("name", stock_code)
        
        logger.info(
            f"[{idx+1}/{len(stocks)}] 开始评估股票: {stock_name}({stock_code})"
        )
        print(f"\n{'='*50}")
        print(f"开始评估股票: {stock_name}({stock_code}) [{idx+1}/{len(stocks)}]")
        print(f"{'='*50}")
        
        if not stock_code:
            logger.warning(f"股票代码为空，跳过: {stock}")
            print("股票代码为空，跳过")
            continue
        
        # 获取数据
        logger.debug(f"获取 {stock_code} 的日线数据")
        print(f"获取 {stock_code} 的日线数据")
        data_fetch_start = time.time()
        daily_data = fetch_data(stock_code, period="daily")
        logger.debug(f"获取 {stock_code} 的5分钟线数据")
        print(f"获取 {stock_code} 的5分钟线数据")
        minute_data = fetch_data(stock_code, period="5min")
        data_fetch_time = time.time() - data_fetch_start
        logger.debug(f"数据获取耗时: {data_fetch_time:.2f}秒")
        
        # 转换为新的配置格式
        strategies = convert_to_strategy_format(stock)
        
        # 评估所有策略
        stock_alerts = evaluator.evaluate_stock_rules(
            stock_code, stock_name, daily_data, minute_data, strategies
        )
        
        # 添加到总告警列表
        all_alerts.extend(stock_alerts)
        
        # 发送告警
        for alert in stock_alerts:
            if webhook_url:
                send_wecom(webhook_url, alert["message"])
                logger.info("已发送告警至企业微信")
                print("已发送告警至企业微信")
        
        # 输出此股票处理时间
        stock_time = time.time() - stock_start_time
        logger.debug(
            f"股票 {stock_name}({stock_code}) 评估完成，耗时: {stock_time:.2f}秒"
        )
        print(f"\n股票 {stock_name}({stock_code}) 评估完成，耗时: {stock_time:.2f}秒")
    
    # 总耗时统计
    total_time = time.time() - start_time
    logger.info(f"所有股票评估完成，共耗时: {total_time:.2f}秒")
    print(f"\n所有股票评估完成，共耗时: {total_time:.2f}秒")
    
    return all_alerts


def evaluate_single_strategy(
    stock: Dict[str, Any],
    strategy: Dict[str, Any],
    detail_level: str = 'normal'
) -> Dict[str, Any]:
    """
    评估单个股票的单个策略
    
    Args:
        stock: 股票信息字典，包含code和name
        strategy: 策略配置字典
        detail_level: 详细程度，可选值为'simple', 'normal', 'detailed'
    
    Returns:
        Dict: 评估结果字典
    """
    logger = setup_logging()
    logger.info("开始评估单个策略")
    
    # 获取股票基本信息
    stock_code = stock.get("code", "")
    stock_name = stock.get("name", stock_code)
    
    if not stock_code:
        logger.error("股票代码为空")
        return {
            "status": "error",
            "message": "股票代码为空",
            "timestamp": int(time.time() * 1000)
        }
        
    logger.info(f"评估股票策略: {stock_name}({stock_code}) - "
                f"{strategy.get('strategy_name', '')}")
    logger.debug(f"策略内容: {strategy}")
    
    # 获取数据
    daily_data = fetch_data(stock_code, period="daily")
    minute_data = fetch_data(stock_code, period="5min")
    
    # 检查数据是否获取成功
    if daily_data is None and minute_data is None:
        logger.error(f"获取股票 {stock_name}({stock_code}) 数据失败")
        return {
            "status": "error", 
            "message": f"获取股票 {stock_name}({stock_code}) 数据失败",
            "timestamp": int(time.time() * 1000)
        }
    
    # 准备基本信息
    strategy_name = strategy.get("strategy_name", "未命名策略")
    strategy_type = strategy.get("strategy_type", "未知")
    rules_config = strategy.get("rules", {})
    
    logger.debug(f"规则配置: {rules_config}")
    
    # 收集所有规则评估详情，无论是否触发
    all_rule_details = {}
    conditions_met = []
    trigger_reasons = []
    
    # 手动检查price_threshold规则
    if "price_threshold" in rules_config:
        price_threshold = float(rules_config["price_threshold"])
        logger.debug(f"评估价格阈值规则: {price_threshold}")
        
        price_detail = {
            "pass": 0,  # 使用数字代替布尔值
            "description": "",
            "target_level": price_threshold,
            "daily_price": 0,
            "minute_price": 0
        }
        
        # 日线价格条件
        if daily_data is not None and 'close' in daily_data.columns and len(daily_data) > 0:
            current_price = float(daily_data['close'].iloc[-1])
            price_detail["daily_price"] = current_price
            
            # 根据策略类型判断是检查上突破还是下突破
            if "加仓" in strategy_type or "买入" in strategy_type:
                # 买入/加仓策略检查上突破
                price_above = current_price > price_threshold
                price_msg = f"日线当前价格: {current_price:.2f}, 加仓阈值: {price_threshold:.2f}"
                price_detail["description"] += price_msg
                logger.debug(f"价格条件评估: {price_msg}, 是否满足: {price_above}")
                
                if price_above:
                    price_detail["pass"] = 1  # 使用数字代替布尔值
                    conditions_met.append("price_threshold")
                    trigger_reasons.append(f"价格突破加仓阈值{price_threshold:.2f}")
            elif "减仓" in strategy_type or "卖出" in strategy_type:
                # 卖出/减仓策略检查下突破
                price_below = current_price < price_threshold
                price_msg = f"日线当前价格: {current_price:.2f}, 减仓阈值: {price_threshold:.2f}"
                price_detail["description"] += price_msg
                logger.debug(f"价格条件评估: {price_msg}, 是否满足: {price_below}")
                
                if price_below:
                    price_detail["pass"] = 1  # 使用数字代替布尔值
                    conditions_met.append("price_threshold")
                    trigger_reasons.append(f"价格跌破减仓阈值{price_threshold:.2f}")
            else:
                # 其他策略类型，价格接近阈值1%以内
                price_diff = abs(current_price - price_threshold) / price_threshold
                price_match = price_diff < 0.01
                price_msg = (f"日线当前价格: {current_price:.2f}, "
                             f"目标阈值: {price_threshold:.2f}, "
                             f"相差: {price_diff:.2%}")
                price_detail["description"] += price_msg
                logger.debug(f"价格条件评估: {price_msg}, 是否满足: {price_match}")
                
                if price_match:
                    price_detail["pass"] = 1  # 使用数字代替布尔值
                    conditions_met.append("price_threshold")
                    trigger_reasons.append(f"价格接近目标阈值{price_threshold:.2f}")
        
        # 将详情添加到结果中
        all_rule_details["price_threshold"] = price_detail
    
    # 手动检查volume_threshold规则
    if "volume_threshold" in rules_config:
        # 修复：处理volume_threshold可能是字典的情况
        if isinstance(rules_config["volume_threshold"], dict):
            volume_threshold_config = rules_config["volume_threshold"]
            if volume_threshold_config.get("enabled", True):
                volume_threshold = float(
                    volume_threshold_config.get("value", 0)
                )
                should_process = True
            else:
                # 如果规则被禁用，跳过此规则
                logger.debug("成交量阈值规则被禁用，跳过")
                all_rule_details["volume_threshold"] = {
                    "pass": 0,  # 使用数字代替布尔值
                    "description": "规则已禁用",
                    "enabled": 0  # 使用数字代替布尔值
                }
                should_process = False
        else:
            # 原来的处理逻辑，直接使用数值
            volume_threshold = float(rules_config["volume_threshold"])
            should_process = True
        
        # 只有当规则启用时才继续处理
        if should_process:
            logger.debug(f"评估成交量阈值规则: {volume_threshold}")
            
            volume_detail = {
                "pass": 0,  # 使用数字代替布尔值
                "description": "",
                "target_threshold": volume_threshold,
                "current_volume": 0,
                "enabled": 1  # 使用数字代替布尔值
            }
            
            # 日线成交量条件
            if (daily_data is not None 
                and 'volume' in daily_data.columns 
                and len(daily_data) > 0):
                current_volume = float(daily_data['volume'].iloc[-1])
                volume_detail["current_volume"] = current_volume
                
                volume_above = current_volume > volume_threshold
                volume_msg = (
                    f"当前成交量: {int(current_volume)}, "
                    f"阈值: {int(volume_threshold)}"
                )
                volume_detail["description"] = volume_msg
                logger.debug(
                    f"成交量条件评估: {volume_msg}, 是否满足: {volume_above}"
                )
                
                if volume_above:
                    volume_detail["pass"] = 1  # 使用数字代替布尔值
                    conditions_met.append("volume_threshold")
                    trigger_reasons.append(
                        f"成交量超过阈值{int(volume_threshold)}"
                    )
            
            # 将详情添加到结果中
            all_rule_details["volume_threshold"] = volume_detail
    
    # 如果规则配置中有其他技术指标规则，创建并评估
    try:
        rules = RuleFactory.create_rules_from_config(strategy)
        logger.debug(f"从工厂创建的规则数量: {len(rules)}")
        
        # 评估除了price_threshold和volume_threshold之外的规则
        for rule in rules:
            rule_name = rule.get_rule_name()
            if hasattr(rule, '__class__'):
                rule_type = rule.__class__.__name__
                # 跳过已经手动评估的价格和成交量规则
                if (rule_type == 'PriceBreakoutRule' and "price_threshold" in all_rule_details) or \
                   (rule_type == 'VolumeThresholdRule' and "volume_threshold" in all_rule_details):
                    logger.debug(f"跳过已评估的规则: {rule_type}")
                    continue
            
            logger.debug(f"评估规则: {rule_name}, 类型: {rule.__class__.__name__}")
            
            # 执行规则检查
            is_triggered, reason, result = rule.check(daily_data, minute_data)
            
            # 确保结果中的布尔值被转换为整数
            result = convert_booleans(result)
            rule_details = result.get("details", {})
            rule_conditions = result.get("conditions_met", [])
            
            # 存储规则键名
            if hasattr(rule, '__class__'):
                rule_type = rule.__class__.__name__
                if rule_type == 'PriceAboveRule':
                    rule_key = "price_level"
                elif rule_type == 'VolumeAboveRule':
                    rule_key = "volume_multiple"
                elif rule_type == 'RSICrossRule':
                    rule_key = "rsi_check"
                elif rule_type == 'MACrossRule':
                    rule_key = "ma_check"
                elif rule_type == 'MACDRule':
                    rule_key = "macd_check"
                elif rule_type == 'PriceBreakoutRule':
                    rule_key = "price_threshold"
                else:
                    rule_key = rule_name
            else:
                rule_key = rule_name
            
            # 将布尔值is_triggered转换为整数
            is_triggered_int = 1 if is_triggered else 0
            logger.debug(f"规则 {rule_key} 评估结果: 触发={is_triggered_int}, 原因={reason}")
            
            # 添加到详细结果
            all_rule_details[rule_key] = rule_details
            
            # 如果规则触发，记录触发信息
            if is_triggered:
                trigger_reasons.append(reason)
                conditions_met.extend(rule_conditions)
    except Exception as e:
        logger.error(f"评估其他规则时出错: {e}", exc_info=True)
    
    # 评估策略的触发条件
    triggered = len(conditions_met) > 0
    if strategy_type != "基础监控":
        # 非基础监控策略要求所有规则都满足
        required_rules = [r for r in rules_config.keys()]
        triggered = (len(conditions_met) > 0 and 
                     len(conditions_met) >= len(required_rules))
    
    # 将布尔值转换为整数，用于日志记录
    triggered_int = 1 if triggered else 0
    logger.debug(f"策略评估结果: 触发={triggered_int}, 满足条件={conditions_met}, "
                f"需满足规则数={len(rules_config)}")
    logger.debug(f"详细评估结果: {all_rule_details}")
    
    # 准备当前股价信息，并修复日期格式问题
    current_price_info = {}
    if daily_data is not None and len(daily_data) > 0:
        # 正确提取和格式化日期
        try:
            if hasattr(daily_data.index[-1], 'strftime'):
                date_str = daily_data.index[-1].strftime("%Y-%m-%d")
            else:
                date_row = daily_data.iloc[-1]
                if 'date' in daily_data.columns:
                    date_obj = date_row['date']
                    if hasattr(date_obj, 'strftime'):
                        date_str = date_obj.strftime("%Y-%m-%d")
                    else:
                        date_str = str(date_obj)
                else:
                    date_str = str(daily_data.index[-1])
        except Exception as e:
            logger.warning(f"日期格式化错误: {e}")
            date_str = str(daily_data.index[-1])
            
        current_price_info["daily"] = {
            "close": float(daily_data['close'].iloc[-1]),
            "date": date_str,
            "open": float(daily_data['open'].iloc[-1]),
            "high": float(daily_data['high'].iloc[-1]),
            "low": float(daily_data['low'].iloc[-1]),
            "volume": float(daily_data['volume'].iloc[-1])
        }
    
    if minute_data is not None and len(minute_data) > 0:
        # 正确提取和格式化日期
        try:
            if hasattr(minute_data.index[-1], 'strftime'):
                date_str = minute_data.index[-1].strftime("%Y-%m-%d %H:%M")
            else:
                date_row = minute_data.iloc[-1]
                if 'date' in minute_data.columns:
                    date_obj = date_row['date']
                    if hasattr(date_obj, 'strftime'):
                        date_str = date_obj.strftime("%Y-%m-%d %H:%M")
                    else:
                        date_str = str(date_obj)
                else:
                    date_str = str(minute_data.index[-1])
        except Exception as e:
            logger.warning(f"日期格式化错误: {e}")
            date_str = str(minute_data.index[-1])
            
        current_price_info["minute"] = {
            "close": float(minute_data['close'].iloc[-1]),
            "date": date_str,
            "open": float(minute_data['open'].iloc[-1]),
            "high": float(minute_data['high'].iloc[-1]),
            "low": float(minute_data['low'].iloc[-1]),
            "volume": float(minute_data['volume'].iloc[-1])
        }
    
    # 处理规则详情中的布尔值
    all_rule_details = convert_booleans(all_rule_details)
    
    # 处理原始规则配置中的布尔值
    rules_config = convert_booleans(rules_config)
    
    # 根据detail_level裁剪结果
    if detail_level == 'simple':
        # 简单版本只返回基本状态和消息
        if triggered:
            return {
                "status": "success",
                "message": f"触发策略: {strategy_name}",
                "details": "触发原因: " + ", ".join(trigger_reasons),
                "timestamp": int(time.time() * 1000)
            }
        else:
            # 提供更详细的未触发信息
            failed_details = []
            for key, detail in all_rule_details.items():
                if detail and not detail.get("pass", 0):
                    desc = detail.get("description", "")
                    if desc:
                        failed_details.append(desc)
            
            # 生成详细消息
            if failed_details:
                detail_msg = "\n".join(failed_details)
            else:
                detail_msg = "所有检查条件均未满足"
            
            return {
                "status": "warning",
                "message": "策略条件未满足",
                "details": detail_msg,
                "timestamp": int(time.time() * 1000)
            }
    else:
        # 完整版本返回全部评估结果
        result = {
            "stock": {
                "code": stock_code,
                "name": stock_name,
                "current_price": current_price_info
            },
            "strategy": {
                "name": strategy_name,
                "type": strategy_type,
                "rules": rules_config  # 已处理布尔值
            },
            "evaluation": {
                "triggered": 1 if triggered else 0,
                "conditions_met": conditions_met,
                "details": all_rule_details  # 已处理布尔值
            },
            "status": "success" if triggered else "warning",
            "message": ("触发策略: " + strategy_name) if triggered 
                       else "策略条件未满足",
            "timestamp": int(time.time() * 1000)
        }
        
        # 如果触发，添加触发原因
        if triggered:
            result["evaluation"]["reasons"] = trigger_reasons
        
        # 最终再次确保所有数据都是可序列化的
        result = convert_booleans(result)
            
        logger.debug(f"最终返回结果: {result}")
        return result


def convert_to_strategy_format(stock: Dict[str, Any]) -> List[Dict[str, Any]]:
    """将旧格式配置转换为策略列表格式"""
    strategies = stock.get("strategies", None)
    
    # 如果已经是新格式（有strategies数组），直接返回
    if strategies:
        return strategies
    
    # 从旧格式转换
    strategy = {
        "strategy_name": stock.get("strategy_name", "基础监控"),
        "strategy_type": stock.get("strategy_type", "基础监控"),
        "rules": stock.get("rules", {})
    }
    
    return [strategy]


if __name__ == "__main__":
    # 直接运行此文件时，执行一次完整的规则评估
    config = load_config()
    alerts = evaluate_rules(config)
    
    # 输出结果摘要
    print("\n\n告警结果摘要:")
    print("=" * 50)
    if alerts:
        for alert in alerts:
            print(f"触发告警: {alert['name']}({alert['code']})")
            print(f"原因: {', '.join(alert.get('reasons', []))}")
            print("-" * 50)
    else:
        print("没有触发任何告警")
    print("=" * 50) 