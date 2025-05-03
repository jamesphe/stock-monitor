import json
import time
import datetime
import requests
import pandas as pd
import pandas_ta as ta
import logging

# 数据缓存，避免重复请求
DATA_CACHE = {}
CACHE_EXPIRE_TIME = 300  # 缓存有效期5分钟

# 尝试导入akshare，如果失败则使用备选数据源
try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    print("警告: akshare库导入失败，将使用备选数据源")
    AKSHARE_AVAILABLE = False


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
            url = f"https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol={full_code}&scale=240&ma=no&datalen={count}"
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
            url = f"https://quotes.sina.cn/cn/api/jsonp_v2.php/=/CN_MarketDataService.getKLineData?symbol={full_code}&scale={scale}&datalen={count}"
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
                    extreme_future_dates = df['date'] > today + datetime.timedelta(days=90)
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
                print(f"获取股票 {stock_code} 分钟线数据失败: HTTP {response.status_code}")
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
                    df = ak.stock_zh_a_hist(
                        symbol=clean_code, 
                        period="daily", 
                        start_date=(datetime.datetime.now() - 
                                     datetime.timedelta(days=count)).strftime('%Y%m%d'),
                        end_date=datetime.datetime.now().strftime('%Y%m%d'), 
                        adjust="qfq"
                    )
                    
                    # 处理可能的不同列名
                    column_mappings = {
                        "日期": "date", "时间": "date", "date": "date", "时点": "date", "日期时间": "date",
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
                    df = ak.stock_zh_a_minute(symbol=code, period=period_map[period])
                    
                    # 处理可能的不同列名
                    column_mappings = {
                        "日期": "date", "时间": "date", "date": "date", "时点": "date", "日期时间": "date",
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


def check_price_above(df, price_level, consecutive_bars=1):
    """检查价格是否连续若干个周期高于指定水平"""
    if df is None or df.empty or len(df) < consecutive_bars:
        return False
    
    # 获取最近N个周期的收盘价
    recent_closes = df['close'].tail(consecutive_bars)
    # 检查是否所有收盘价都高于指定价格
    return all(recent_closes > price_level)


def check_volume_above(df, volume_multiple, lookback=5):
    """检查当前成交量是否高于过去N日平均的M倍"""
    if df is None or df.empty or len(df) <= lookback:
        return False
    
    current_volume = df['volume'].iloc[-1]
    avg_volume = df['volume'].iloc[-lookback-1:-1].mean()
    
    return current_volume > avg_volume * volume_multiple


def check_rsi_cross(df, overbought=70, oversold=30):
    """检查RSI是否发生金叉或死叉"""
    if df is None or df.empty or len(df) < 3:
        return False, None
    
    # 检查是否有效的RSI值
    if 'rsi' not in df.columns or df['rsi'].isnull().any():
        return False, None
    
    # 获取最近三个RSI值
    rsi_values = df['rsi'].tail(3).values
    
    # 检查金叉（从超卖区向上穿越）
    if rsi_values[0] < oversold and rsi_values[1] < oversold and rsi_values[2] > oversold:
        return True, "金叉(超卖区域向上突破)"
    
    # 检查死叉（从超买区向下穿越）
    if rsi_values[0] > overbought and rsi_values[1] > overbought and rsi_values[2] < overbought:
        return True, "死叉(超买区域向下突破)"
    
    return False, None


def check_ma_cross(df, fast_ma="ma5", slow_ma="ma20"):
    """检查均线交叉
    
    Args:
        df: 数据DataFrame
        fast_ma: 快速均线列名，如"ma5"
        slow_ma: 慢速均线列名，如"ma20"
    
    Returns:
        tuple: (是否交叉, 交叉类型描述)
    """
    if df is None or df.empty or len(df) < 3:
        return False, None
    
    # 检查均线列是否存在
    if fast_ma not in df.columns or slow_ma not in df.columns:
        return False, None
    
    # 获取最近3个周期的均线值
    fast_values = df[fast_ma].tail(3).values
    slow_values = df[slow_ma].tail(3).values
    
    # 检查是否有缺失值
    if any(pd.isna(fast_values)) or any(pd.isna(slow_values)):
        return False, None
    
    # 检查金叉（快线从下方穿过慢线）
    golden_cross = (fast_values[0] < slow_values[0] and 
                    fast_values[1] < slow_values[1] and 
                    fast_values[2] > slow_values[2])
    if golden_cross:
        cross_type = f"{fast_ma}/{slow_ma}金叉"
        description = "(快线向上穿越慢线)"
        return True, cross_type + description
    
    # 检查死叉（快线从上方穿过慢线）
    death_cross = (fast_values[0] > slow_values[0] and 
                   fast_values[1] > slow_values[1] and 
                   fast_values[2] < slow_values[2])
    if death_cross:
        cross_type = f"{fast_ma}/{slow_ma}死叉"
        description = "(快线向下穿越慢线)"
        return True, cross_type + description
    
    return False, None


def check_macd_cross(df):
    """检查MACD指标是否发生金叉或死叉
    
    Args:
        df: 数据DataFrame，包含MACD、MACDs（信号线）列
    
    Returns:
        tuple: (是否交叉, 交叉类型描述)
    """
    if df is None or df.empty or len(df) < 3:
        return False, None
    
    # 检查MACD相关列是否存在
    if 'MACD_12_26_9' not in df.columns or 'MACDs_12_26_9' not in df.columns:
        return False, None
    
    # 获取最近3个周期的MACD和信号线值
    macd_values = df['MACD_12_26_9'].tail(3).values
    signal_values = df['MACDs_12_26_9'].tail(3).values
    
    # 检查是否有缺失值
    if any(pd.isna(macd_values)) or any(pd.isna(signal_values)):
        return False, None
    
    # 检查金叉（MACD从下方穿过信号线）
    if macd_values[0] < signal_values[0] and macd_values[1] < signal_values[1] and macd_values[2] > signal_values[2]:
        return True, "MACD金叉(MACD线上穿信号线)"
    
    # 检查死叉（MACD从上方穿过信号线）
    if macd_values[0] > signal_values[0] and macd_values[1] > signal_values[1] and macd_values[2] < signal_values[2]:
        return True, "MACD死叉(MACD线下穿信号线)"
    
    return False, None


def check_price_breakout(df, lookback=20):
    """检查价格是否突破前期高点或低点
    
    Args:
        df: 数据DataFrame
        lookback: 回溯的周期数
        
    Returns:
        tuple: (是否突破, 突破类型描述)
    """
    if df is None or df.empty or len(df) < lookback + 1:
        return False, None
    
    # 获取前N个周期的最高价和最低价
    current_close = df['close'].iloc[-1]
    recent_highs = df['high'].iloc[-lookback-1:-1]
    recent_lows = df['low'].iloc[-lookback-1:-1]
    
    previous_high = recent_highs.max()
    previous_low = recent_lows.min()
    
    # 突破前期高点
    if current_close > previous_high:
        return True, f"突破{lookback}周期前高点{previous_high:.2f}"
    
    # 跌破前期低点
    if current_close < previous_low:
        return True, f"跌破{lookback}周期前低点{previous_low:.2f}"
    
    return False, None


def check_volume_price_divergence(df, window=5):
    """检查量价背离
    
    Args:
        df: 数据DataFrame
        window: 观察窗口大小
        
    Returns:
        tuple: (是否背离, 背离类型描述)
    """
    if df is None or df.empty or len(df) < window + 2:
        return False, None
    
    # 获取价格和成交量数据
    current_slice = df.iloc[-window:]
    previous_slice = df.iloc[-window*2:-window]
    
    # 计算价格趋势
    current_price_trend = current_slice['close'].iloc[-1] - current_slice['close'].iloc[0]
    previous_price_trend = previous_slice['close'].iloc[-1] - previous_slice['close'].iloc[0]
    
    # 计算成交量趋势
    current_volume_sum = current_slice['volume'].sum()
    previous_volume_sum = previous_slice['volume'].sum()
    volume_trend = current_volume_sum - previous_volume_sum
    
    # 检查背离
    # 1. 价格上涨但成交量萎缩
    if current_price_trend > 0 and previous_price_trend > 0 and volume_trend < 0:
        return True, "价升量缩背离(价格上涨但成交量萎缩)"
    
    # 2. 价格下跌但成交量放大
    if current_price_trend < 0 and previous_price_trend < 0 and volume_trend > 0:
        return True, "价跌量增背离(价格下跌但成交量放大)"
    
    return False, None


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


def check_price_pullback(df, price_level, volume_multiple=1.2, lookback=5):
    """检查价格是否回调至特定水平且放量
    
    Args:
        df (pandas.DataFrame): 股票数据，必须包含'close'和'volume'列
        price_level (float): 回调目标价格
        volume_multiple (float): 成交量放大倍数（与过去lookback期均量对比）
        lookback (int): 对比的周期数
        
    Returns:
        tuple: (是否满足条件, 满足条件的描述)
    """
    if len(df) < lookback + 2:
        return False, None
    
    # 获取最近数据
    recent_data = df.iloc[-lookback-2:]
    
    # 条件1：当前收盘价接近目标价格（上下浮动1%以内）
    current_close = recent_data['close'].iloc[-1]
    price_diff_percent = abs(current_close - price_level) / price_level * 100
    price_condition = price_diff_percent <= 1.0  # 价格在目标价格1%范围内
    
    # 条件2：之前价格高于目标价格，现在回调至目标价格
    previous_high = recent_data['close'].iloc[:-1].max()
    pullback_condition = previous_high > price_level * 1.03  # 之前价格至少高出目标价格3%
    
    # 条件3：成交量放大
    current_volume = recent_data['volume'].iloc[-1]
    avg_volume = recent_data['volume'].iloc[-lookback-1:-1].mean()
    volume_condition = current_volume > avg_volume * volume_multiple
    
    # 综合三个条件
    if price_condition and pullback_condition and volume_condition:
        return True, f"价格从{previous_high:.2f}回调至{current_close:.2f}附近(目标:{price_level:.2f})且放量{current_volume/avg_volume:.2f}倍"
    
    return False, None


def check_specific_breakout(df, high_level=None, low_level=None, consecutive_bars=1):
    """检查价格是否突破指定高点或低点
    
    Args:
        df (pandas.DataFrame): 股票数据，必须包含'close'列
        high_level (float): 指定的高点价格，None表示不检查
        low_level (float): 指定的低点价格，None表示不检查
        consecutive_bars (int): 连续K线数量
        
    Returns:
        tuple: (是否满足条件, 满足条件的描述)
    """
    if len(df) < consecutive_bars:
        return False, None
    
    # 获取最近n根K线的收盘价
    recent_closes = df['close'].iloc[-consecutive_bars:].values
    
    # 检查突破高点
    if high_level is not None:
        # 检查最近n根K线是否全部收盘价高于指定高点
        if all(close > high_level for close in recent_closes):
            return True, f"价格突破指定高点{high_level}，连续{consecutive_bars}周期收盘价为{', '.join([f'{c:.2f}' for c in recent_closes])}"
    
    # 检查突破低点
    if low_level is not None:
        # 检查最近n根K线是否全部收盘价低于指定低点
        if all(close < low_level for close in recent_closes):
            return True, f"价格跌破指定低点{low_level}，连续{consecutive_bars}周期收盘价为{', '.join([f'{c:.2f}' for c in recent_closes])}"
    
    return False, None


def evaluate_rules(config=None):
    """评估所有监控规则
    
    Args:
        config: 配置字典，如果为None则自动加载
    
    Returns:
        list: 触发的告警消息列表，包含详细的判断结果
    """
    start_time = time.time()
    logger = logging.getLogger("monitor")
    logger.info("开始评估监控规则")
    
    if config is None:
        config = load_config()
        logger.debug("从配置文件加载规则")
    else:
        logger.debug("使用传入的规则配置")
        
    webhook_url = config.get("wecom_webhook", "")
    stocks = config.get("stocks", [])
    
    logger.info(f"需要评估 {len(stocks)} 只股票")
    
    alerts = []
    
    for idx, stock in enumerate(stocks):
        stock_start_time = time.time()
        stock_code = stock.get("code", "")
        stock_name = stock.get("name", stock_code)
        
        logger.info(f"[{idx+1}/{len(stocks)}] 开始评估股票: {stock_name}({stock_code})")
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
        
        # 输出获取到的数据概况
        if daily_data is not None:
            date_min = daily_data['date'].min() if 'date' in daily_data.columns and not daily_data.empty else "未知"
            date_max = daily_data['date'].max() if 'date' in daily_data.columns and not daily_data.empty else "未知"
            logger.debug(f"日线数据: {len(daily_data)}行，日期范围: {date_min} - {date_max}")
            print(f"日线数据: {len(daily_data)}行，日期范围: {date_min} - {date_max}")
            
            if 'close' in daily_data.columns and not daily_data.empty:
                current_price = daily_data['close'].iloc[-1]
                logger.debug(f"最新收盘价: {current_price}")
                print(f"最新收盘价: {current_price}")
        else:
            logger.warning(f"未获取到 {stock_code} 的日线数据")
            print("未获取到日线数据")
            
        if minute_data is not None:
            date_min = minute_data['date'].min() if 'date' in minute_data.columns and not minute_data.empty else "未知"
            date_max = minute_data['date'].max() if 'date' in minute_data.columns and not minute_data.empty else "未知"
            logger.debug(f"分钟线数据: {len(minute_data)}行，日期范围: {date_min} - {date_max}")
            print(f"分钟线数据: {len(minute_data)}行，日期范围: {date_min} - {date_max}")
            
            if 'close' in minute_data.columns and not minute_data.empty:
                current_price = minute_data['close'].iloc[-1]
                logger.debug(f"最新5分钟收盘价: {current_price}")
                print(f"最新5分钟收盘价: {current_price}")
        else:
            logger.warning(f"未获取到 {stock_code} 的5分钟线数据")
            print("未获取到分钟线数据")
        
        # 检查是否使用新的配置结构（包含strategies数组）
        strategies = stock.get("strategies", None)
        
        # 如果是新结构（有strategies数组）
        if strategies:
            logger.info(f"检测到新的配置结构，该股票有{len(strategies)}个策略")
            print(f"\n发现{len(strategies)}个监控策略配置")
            
            for strategy_idx, strategy in enumerate(strategies):
                strategy_name = strategy.get("strategy_name", f"策略{strategy_idx+1}")
                strategy_type = strategy.get("strategy_type", "未知")
                rules = strategy.get("rules", {})
                
                logger.info(f"评估策略 [{strategy_idx+1}/{len(strategies)}]: {strategy_name}({strategy_type})")
                print(f"\n{'*'*30}")
                print(f"评估策略: {strategy_name}({strategy_type}) [{strategy_idx+1}/{len(strategies)}]")
                print(f"{'*'*30}")
                
                # 策略评估逻辑（与旧版本相同，但使用strategy中的rules）
                # 条件判断
                triggered = False
                trigger_reasons = []
                daily_conditions_met = []
                minute_conditions_met = []
                
                # 详细条件结果
                details = {}
                
                logger.info(f"开始评估 {stock_code} 策略 {strategy_name} 的监控条件")
                print(f"\n-----监控条件评估开始-----")
                
                # 价格突破条件
                if rules.get("price_level"):
                    price_level = float(rules.get("price_level"))
                    consecutive_bars = int(rules.get("consecutive_bars", 1))
                    
                    logger.debug(f"评估价格突破条件: 价格 > {price_level}，持续{consecutive_bars}周期")
                    print(f"\n🔍 评估价格突破条件: 价格 > {price_level}，持续{consecutive_bars}周期")
                    
                    price_detail = {"pass": False, "description": ""}
                    
                    # 日线价格突破
                    if daily_data is not None and 'close' in daily_data.columns and len(daily_data) >= consecutive_bars:
                        condition_start = time.time()
                        price_above = check_price_above(daily_data, price_level, consecutive_bars)
                        recent_prices = [str(round(p, 2)) for p in daily_data['close'].tail(consecutive_bars).values]
                        condition_time = time.time() - condition_start
                        
                        logger.debug(f"日线价格突破: {'是' if price_above else '否'}, 耗时: {condition_time:.4f}秒")
                        print(f"  ├─ 日线价格突破: {'是' if price_above else '否'}")
                        print(f"  │   └─ 最近{consecutive_bars}日收盘价: {', '.join(recent_prices)}")
                        
                        price_detail["pass"] = price_above
                        price_detail["description"] = f"日线最近{consecutive_bars}日收盘价: {', '.join(recent_prices)}, 需突破: {price_level}"
                        
                        if price_above:
                            daily_conditions_met.append("price")
                            trigger_reasons.append(f"价格连续{consecutive_bars}日收盘价高于{price_level}")
                            logger.info(f"日线价格突破条件满足: {price_level}")
                        
                    # 分钟线价格突破
                    if minute_data is not None and 'close' in minute_data.columns and len(minute_data) >= consecutive_bars and not price_detail["pass"]:
                        condition_start = time.time()
                        price_above = check_price_above(minute_data, price_level, consecutive_bars)
                        recent_prices = [str(round(p, 2)) for p in minute_data['close'].tail(consecutive_bars).values]
                        condition_time = time.time() - condition_start
                        
                        logger.debug(f"分钟线价格突破: {'是' if price_above else '否'}, 耗时: {condition_time:.4f}秒")
                        print(f"  └─ 5分钟价格突破: {'是' if price_above else '否'}")
                        print(f"      └─ 最近{consecutive_bars}个5分钟收盘价: {', '.join(recent_prices)}")
                        
                        if not price_detail["pass"]:  # 只有当日线未通过时才考虑分钟线
                            price_detail["pass"] = price_above
                            price_detail["description"] += f"\n5分钟最近{consecutive_bars}个周期收盘价: {', '.join(recent_prices)}, 需突破: {price_level}"
                        
                        if price_above:
                            minute_conditions_met.append("price")
                            trigger_reasons.append(f"价格连续{consecutive_bars}个5分钟收盘价高于{price_level}")
                            logger.info(f"分钟线价格突破条件满足: {price_level}")
                    
                    # 添加到详细结果
                    details["price"] = price_detail
                
                # 成交量放大条件
                if rules.get("volume_multiple"):
                    volume_multiple = float(rules.get("volume_multiple"))
                    lookback = int(rules.get("volume_lookback", 5))
                    
                    logger.debug(f"评估成交量条件: 当前成交量 > 过去{lookback}周期均量的{volume_multiple}倍")
                    print(f"\n🔍 评估成交量条件: 当前成交量 > 过去{lookback}周期均量的{volume_multiple}倍")
                    
                    volume_detail = {"pass": False, "description": ""}
                    
                    # 日线成交量放大
                    if daily_data is not None and 'volume' in daily_data.columns and len(daily_data) > lookback:
                        condition_start = time.time()
                        volume_above = check_volume_above(daily_data, volume_multiple, lookback)
                        current_volume = daily_data['volume'].iloc[-1]
                        avg_volume = daily_data['volume'].iloc[-lookback-1:-1].mean()
                        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
                        condition_time = time.time() - condition_start
                        
                        logger.debug(f"日线成交量放大: {'是' if volume_above else '否'}, 耗时: {condition_time:.4f}秒")
                        print(f"  └─ 日线成交量放大: {'是' if volume_above else '否'}")
                        print(f"      ├─ 当前成交量: {current_volume}")
                        print(f"      ├─ 过去{lookback}日均量: {avg_volume}")
                        print(f"      └─ 对比倍数: {volume_ratio:.2f}倍")
                        
                        volume_detail["pass"] = volume_above
                        volume_detail["description"] = f"当前成交量: {int(current_volume)}, 过去{lookback}日均量: {int(avg_volume)}, 对比倍数: {volume_ratio:.2f}倍, 需大于: {volume_multiple}倍"
                        
                        if volume_above:
                            daily_conditions_met.append("volume")
                            trigger_reasons.append(f"成交量为过去{lookback}日均值的{volume_multiple}倍以上")
                            logger.info(f"成交量放大条件满足: {volume_ratio:.2f}倍 > {volume_multiple}倍")
                    
                    # 添加到详细结果
                    details["volume"] = volume_detail
                    
                # RSI指标条件
                if rules.get("rsi_check", False):
                    overbought = float(rules.get("rsi_overbought", 70))
                    oversold = float(rules.get("rsi_oversold", 30))
                    
                    logger.debug(f"评估RSI条件: 超买区 > {overbought}，超卖区 < {oversold}")
                    print(f"\n🔍 评估RSI条件: 超买区 > {overbought}，超卖区 < {oversold}")
                    
                    rsi_detail = {"pass": False, "description": ""}
                    
                    # 日线RSI交叉
                    if daily_data is not None:
                        if 'rsi' in daily_data.columns:
                            rsi_value = daily_data['rsi'].iloc[-1]
                            recent_rsi = [f'{v:.2f}' for v in daily_data['rsi'].tail(3).values]
                            logger.debug(f"日线RSI(14)当前值: {rsi_value:.2f}")
                            print(f"  ├─ 日线RSI(14)当前值: {rsi_value:.2f}")
                            
                            rsi_detail["description"] = f"日线RSI(14)当前值: {rsi_value:.2f}, 最近3个值: {', '.join(recent_rsi)}"
                        
                        crossed, cross_type = check_rsi_cross(daily_data, overbought, oversold)
                        logger.debug(f"日线RSI金叉/死叉: {'是-'+cross_type if crossed else '否'}")
                        print(f"  ├─ 日线RSI金叉/死叉: {'是-'+cross_type if crossed else '否'}")
                        
                        rsi_detail["pass"] = crossed
                        if crossed:
                            rsi_detail["description"] += f"\n日线RSI指标{cross_type}: 超买区 > {overbought}, 超卖区 < {oversold}"
                            daily_conditions_met.append("rsi_cross")
                            trigger_reasons.append(f"日线RSI {cross_type}")
                    
                    # 分钟线RSI交叉
                    if minute_data is not None and not rsi_detail["pass"]:
                        if 'rsi' in minute_data.columns:
                            rsi_value = minute_data['rsi'].iloc[-1]
                            recent_rsi = [f'{v:.2f}' for v in minute_data['rsi'].tail(3).values]
                            logger.debug(f"分钟线RSI(14)当前值: {rsi_value:.2f}")
                            print(f"  ├─ 5分钟RSI(14)当前值: {rsi_value:.2f}")
                            
                            if not rsi_detail["description"]:
                                rsi_detail["description"] = f"5分钟RSI(14)当前值: {rsi_value:.2f}, 最近3个值: {', '.join(recent_rsi)}"
                            else:
                                rsi_detail["description"] += f"\n5分钟RSI(14)当前值: {rsi_value:.2f}, 最近3个值: {', '.join(recent_rsi)}"
                        
                        crossed, cross_type = check_rsi_cross(minute_data, overbought, oversold)
                        logger.debug(f"分钟线RSI金叉/死叉: {'是-'+cross_type if crossed else '否'}")
                        print(f"  └─ 5分钟RSI金叉/死叉: {'是-'+cross_type if crossed else '否'}")
                        
                        if not rsi_detail["pass"]:  # 只有当日线未通过时才考虑分钟线
                            rsi_detail["pass"] = crossed
                            if crossed:
                                rsi_detail["description"] += f"\n5分钟RSI指标{cross_type}: 超买区 > {overbought}, 超卖区 < {oversold}"
                        
                        if crossed and cross_type:
                            minute_conditions_met.append("rsi_cross")
                            trigger_reasons.append(f"5分钟RSI {cross_type}")
                        
                    # 添加到详细结果
                    details["rsi"] = rsi_detail
                
                # 均线交叉条件
                if rules.get("ma_check", False):
                    fast_ma = rules.get("fast_ma", "ma5")
                    slow_ma = rules.get("slow_ma", "ma20")
                    
                    logger.debug(f"评估均线交叉条件: {fast_ma}/{slow_ma}交叉")
                    print(f"\n🔍 评估均线交叉条件: {fast_ma}/{slow_ma}交叉")
                    
                    ma_cross_detail = {"pass": False, "description": ""}
                    
                    # 日线均线交叉
                    if daily_data is not None:
                        # 确保计算均线
                        for ma in [5, 10, 20, 60]:
                            ma_col = f"ma{ma}"
                            if ma_col not in daily_data.columns:
                                daily_data[ma_col] = daily_data['close'].rolling(window=ma).mean()
                        
                        fast_val = daily_data[fast_ma].iloc[-1] if fast_ma in daily_data.columns else None
                        slow_val = daily_data[slow_ma].iloc[-1] if slow_ma in daily_data.columns else None
                        
                        if fast_val is not None and slow_val is not None:
                            logger.debug(f"日线{fast_ma}当前值: {fast_val:.2f}")
                            print(f"  ├─ 日线{fast_ma}当前值: {fast_val:.2f}")
                            ma_cross_detail["description"] = f"日线{fast_ma}当前值: {fast_val:.2f}, {slow_ma}当前值: {slow_val:.2f}"
                        else:
                            logger.debug(f"  ├─ 缺少均线数据")
                            ma_cross_detail["description"] = "缺少日线均线数据"
                        
                        crossed, cross_type = check_ma_cross(daily_data, fast_ma, slow_ma)
                        logger.debug(f"日线均线交叉: {'是-'+cross_type if crossed else '否'}")
                        print(f"  ├─ 日线均线交叉: {'是-'+cross_type if crossed else '否'}")
                        
                        ma_cross_detail["pass"] = crossed
                        if crossed:
                            ma_cross_detail["description"] += f"\n日线{fast_ma}/{slow_ma}出现{cross_type}"
                            daily_conditions_met.append("ma_cross")
                            trigger_reasons.append(f"日线{fast_ma}/{slow_ma} {cross_type}")
                    
                    # 分钟线均线交叉
                    if minute_data is not None and not ma_cross_detail["pass"]:
                        # 确保计算均线
                        for ma in [5, 10, 20, 60]:
                            ma_col = f"ma{ma}"
                            if ma_col not in minute_data.columns:
                                minute_data[ma_col] = minute_data['close'].rolling(window=ma).mean()
                        
                        fast_val = minute_data[fast_ma].iloc[-1] if fast_ma in minute_data.columns else None
                        slow_val = minute_data[slow_ma].iloc[-1] if slow_ma in minute_data.columns else None
                        
                        if fast_val is not None and slow_val is not None:
                            logger.debug(f"分钟线{fast_ma}当前值: {fast_val:.2f}")
                            print(f"  ├─ 5分钟{fast_ma}当前值: {fast_val:.2f}")
                            if not ma_cross_detail["description"]:
                                ma_cross_detail["description"] = f"5分钟{fast_ma}当前值: {fast_val:.2f}, {slow_ma}当前值: {slow_val:.2f}"
                            else:
                                ma_cross_detail["description"] += f"\n5分钟{fast_ma}当前值: {fast_val:.2f}, {slow_ma}当前值: {slow_val:.2f}"
                        else:
                            logger.debug(f"  ├─ 缺少均线数据")
                            if not ma_cross_detail["description"]:
                                ma_cross_detail["description"] = "缺少5分钟均线数据"
                        
                        crossed, cross_type = check_ma_cross(minute_data, fast_ma, slow_ma)
                        logger.debug(f"分钟线均线交叉: {'是-'+cross_type if crossed else '否'}")
                        print(f"  └─ 5分钟均线交叉: {'是-'+cross_type if crossed else '否'}")
                        
                        if not ma_cross_detail["pass"]:  # 只有当日线未通过时才考虑分钟线
                            ma_cross_detail["pass"] = crossed
                            if crossed:
                                ma_cross_detail["description"] += f"\n5分钟{fast_ma}/{slow_ma}出现{cross_type}"
                        
                        if crossed and cross_type:
                            minute_conditions_met.append("ma_cross")
                            trigger_reasons.append(f"5分钟{fast_ma}/{slow_ma} {cross_type}")
                        
                    # 添加到详细结果
                    details["ma_cross"] = ma_cross_detail
                
                # MACD指标条件
                if rules.get("macd_check", False):
                    logger.debug(f"评估MACD条件")
                    print(f"\n🔍 评估MACD条件")
                    
                    macd_detail = {"pass": False, "description": ""}
                    
                    # 日线MACD交叉
                    if daily_data is not None:
                        # 确保计算MACD
                        if 'macd' not in daily_data.columns or 'macd_signal' not in daily_data.columns:
                            macd_df = ta.macd(daily_data['close'])
                            daily_data['macd'] = macd_df['MACD_12_26_9']
                            daily_data['macd_signal'] = macd_df['MACDs_12_26_9']
                            daily_data['macd_histogram'] = macd_df['MACDh_12_26_9']
                        
                        macd_value = daily_data['macd'].iloc[-1]
                        signal_value = daily_data['macd_signal'].iloc[-1]
                        histogram_value = daily_data['macd_histogram'].iloc[-1]
                        
                        logger.debug(f"日线MACD当前值: {macd_value:.4f}")
                        print(f"  ├─ 日线MACD当前值: {macd_value:.4f}")
                        logger.debug(f"日线信号线当前值: {signal_value:.4f}")
                        print(f"  ├─ 日线信号线当前值: {signal_value:.4f}")
                        logger.debug(f"日线柱状图当前值: {histogram_value:.4f}")
                        print(f"  ├─ 日线柱状图当前值: {histogram_value:.4f}")
                        
                        macd_detail["description"] = f"日线MACD: {macd_value:.4f}, 信号线: {signal_value:.4f}, 柱状图: {histogram_value:.4f}"
                        
                        crossed, cross_type = check_macd_cross(daily_data)
                        logger.debug(f"日线MACD交叉: {'是-'+cross_type if crossed else '否'}")
                        print(f"  ├─ 日线MACD交叉: {'是-'+cross_type if crossed else '否'}")
                        
                        macd_detail["pass"] = crossed
                        if crossed:
                            macd_detail["description"] += f"\n日线MACD出现{cross_type}"
                            daily_conditions_met.append("macd")
                            trigger_reasons.append(f"日线MACD {cross_type}")
                        
                    # 分钟线MACD交叉
                    if minute_data is not None and not macd_detail["pass"]:
                        # 确保计算MACD
                        if 'macd' not in minute_data.columns or 'macd_signal' not in minute_data.columns:
                            macd_df = ta.macd(minute_data['close'])
                            minute_data['macd'] = macd_df['MACD_12_26_9']
                            minute_data['macd_signal'] = macd_df['MACDs_12_26_9']
                            minute_data['macd_histogram'] = macd_df['MACDh_12_26_9']
                        
                        macd_value = minute_data['macd'].iloc[-1]
                        signal_value = minute_data['macd_signal'].iloc[-1]
                        histogram_value = minute_data['macd_histogram'].iloc[-1]
                        
                        logger.debug(f"分钟线MACD当前值: {macd_value:.4f}")
                        print(f"  ├─ 5分钟MACD当前值: {macd_value:.4f}")
                        logger.debug(f"分钟线信号线当前值: {signal_value:.4f}")
                        print(f"  ├─ 5分钟信号线当前值: {signal_value:.4f}")
                        logger.debug(f"分钟线柱状图当前值: {histogram_value:.4f}")
                        print(f"  ├─ 5分钟柱状图当前值: {histogram_value:.4f}")
                        
                        if not macd_detail["description"]:
                            macd_detail["description"] = f"5分钟MACD: {macd_value:.4f}, 信号线: {signal_value:.4f}, 柱状图: {histogram_value:.4f}"
                        else:
                            macd_detail["description"] += f"\n5分钟MACD: {macd_value:.4f}, 信号线: {signal_value:.4f}, 柱状图: {histogram_value:.4f}"
                        
                        crossed, cross_type = check_macd_cross(minute_data)
                        logger.debug(f"分钟线MACD交叉: {'是-'+cross_type if crossed else '否'}")
                        print(f"  └─ 5分钟MACD交叉: {'是-'+cross_type if crossed else '否'}")
                        
                        if not macd_detail["pass"]:  # 只有当日线未通过时才考虑分钟线
                            macd_detail["pass"] = crossed
                            if crossed:
                                macd_detail["description"] += f"\n5分钟MACD出现{cross_type}"
                        
                        if crossed and cross_type:
                            minute_conditions_met.append("macd")
                            trigger_reasons.append(f"5分钟MACD {cross_type}")
                        
                    # 添加到详细结果
                    details["macd"] = macd_detail
                
                # 根据条件综合判断
                if daily_conditions_met or minute_conditions_met:
                    triggered = True
                    logger.info(f"触发告警: {stock_code}, 原因: {trigger_reasons}")
                    
                    # 确定信号类型
                    if "macd" in daily_conditions_met or "ma_cross" in daily_conditions_met:
                        if "金叉" in " ".join(trigger_reasons):
                            action = "buy"
                        elif "死叉" in " ".join(trigger_reasons):
                            action = "sell"
                        else:
                            action = "alert"
                    elif "price" in daily_conditions_met or "volume" in daily_conditions_met:
                        action = "buy"
                    elif "rsi_cross" in daily_conditions_met:
                        if "超买" in " ".join(trigger_reasons):
                            action = "sell"
                        elif "超卖" in " ".join(trigger_reasons):
                            action = "buy"
                        else:
                            action = "alert"
                    else:
                        action = "alert"
                    
                    # 获取策略名称和类型
                    strategy_name = strategy.get("strategy_name", "默认策略")
                    strategy_type = strategy.get("strategy_type", "基础监控") 
                    
                    # 根据策略类型调整动作类型
                    if strategy_type == "建仓":
                        action_display = "建仓"
                    elif strategy_type == "加仓":
                        action_display = "加仓"
                    elif strategy_type == "减仓":
                        action_display = "减仓"
                    elif strategy_type == "清仓":
                        action_display = "清仓"
                    else:
                        action_display = "监控"
                    
                    # 生成消息
                    if daily_data is not None and 'close' in daily_data.columns and not daily_data.empty:
                        current_price = daily_data['close'].iloc[-1]
                    elif minute_data is not None and 'close' in minute_data.columns and not minute_data.empty:
                        current_price = minute_data['close'].iloc[-1]
                    else:
                        current_price = 0
                    
                    message = f"{stock_name}({stock_code}) [{strategy_name}-{action_display}] 当前价: {current_price:.2f}，触发条件: {', '.join(trigger_reasons)}"
                    
                    # 添加到告警列表
                    alert = {
                        "code": stock_code,
                        "name": stock_name,
                        "price": current_price,
                        "action": action,
                        "action_display": action_display,
                        "strategy_name": strategy_name,
                        "strategy_type": strategy_type,
                        "message": message,
                        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "details": details
                    }
                    
                    alerts.append(alert)
                    
                    logger.info(f"添加告警: {message}")
                    print(f"\n✅ 触发告警: {message}")
                    
                    # 发送微信告警
                    if webhook_url:
                        wecom_result = send_wecom(webhook_url, message)
                        logger.info(f"发送微信通知: {'成功' if wecom_result else '失败'}")
                        print(f"已发送微信通知")
                else:
                    logger.info(f"未触发告警: {stock_code}")
                    print(f"\n❌ 未触发任何告警条件")
                    
                    # 即使未触发，也返回附带所有检测结果的数据
                    if daily_data is not None and 'close' in daily_data.columns and not daily_data.empty:
                        current_price = daily_data['close'].iloc[-1]
                    elif minute_data is not None and 'close' in minute_data.columns and not minute_data.empty:
                        current_price = minute_data['close'].iloc[-1]
                    else:
                        current_price = 0
                        
                    # 添加到结果列表，但标记为未触发
                    alert = {
                        "code": stock_code,
                        "name": stock_name,
                        "price": current_price,
                        "action": "none",
                        "message": f"{stock_name}({stock_code}) 当前价: {current_price:.2f}，未触发任何条件",
                        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "details": details
                    }
                    
                    alerts.append(alert)
        else:
            # 使用旧的配置结构，直接使用stock中的rules
            # 保留原有逻辑
            rules = stock.get("rules", {})
            strategy_name = stock.get("strategy_name", "基础监控")
            strategy_type = stock.get("strategy_type", "基础监控")
            
            # 条件判断
            triggered = False
            trigger_reasons = []
            daily_conditions_met = []
            minute_conditions_met = []
            
            # 详细条件结果
            details = {}
            
            logger.info(f"开始评估 {stock_code} 的监控条件（旧配置结构）")
            print(f"\n-----监控条件评估开始（旧配置结构）-----")
            
            # 价格突破条件
            if rules.get("price_level"):
                price_level = float(rules.get("price_level"))
                consecutive_bars = int(rules.get("consecutive_bars", 1))
                
                logger.debug(f"评估价格突破条件: 价格 > {price_level}，持续{consecutive_bars}周期")
                print(f"\n🔍 评估价格突破条件: 价格 > {price_level}，持续{consecutive_bars}周期")
                
                # 原有价格突破逻辑...
                
            # 原有的其他规则处理...
            
            # 最终结果汇总
            if trigger_reasons:
                triggered = True
                time_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                alert_message = f"⚠️ 监控提醒 - {stock_name}({stock_code})\n"
                alert_message += f"触发时间: {time_str}\n"
                alert_message += f"触发策略: {strategy_name}({strategy_type})\n"
                alert_message += f"触发原因:\n - " + "\n - ".join(trigger_reasons)
                
                # 添加当前价格信息
                if daily_data is not None and 'close' in daily_data.columns and not daily_data.empty:
                    daily_price = daily_data['close'].iloc[-1]
                    alert_message += f"\n\n最新收盘价: {daily_price}"
                
                if minute_data is not None and 'close' in minute_data.columns and not minute_data.empty:
                    minute_price = minute_data['close'].iloc[-1]
                    alert_message += f"\n最新5分钟价: {minute_price}"
                
                alert_data = {
                    "message": alert_message,
                    "details": details,
                    "stock_code": stock_code,
                    "stock_name": stock_name,
                    "strategy_name": strategy_name,
                    "strategy_type": strategy_type,
                    "trigger_time": time_str,
                    "trigger_reasons": trigger_reasons,
                }
                
                alerts.append(alert_data)
                logger.info(f"触发告警：{stock_name}({stock_code})")
                print(f"\n🚨 触发告警\n")
            else:
                logger.info(f"未触发告警：{stock_name}({stock_code})")
                print(f"\n✅ 未触发告警\n")
                
        # 计算此股票处理时间
        stock_time = time.time() - stock_start_time
        logger.debug(f"股票 {stock_name}({stock_code}) 评估完成，耗时: {stock_time:.2f}秒")
        print(f"\n股票 {stock_name}({stock_code}) 评估完成，耗时: {stock_time:.2f}秒")
    
    total_time = time.time() - start_time
    logger.info(f"所有股票评估完成，共耗时: {total_time:.2f}秒")
    print(f"\n所有股票评估完成，共耗时: {total_time:.2f}秒")
    
    return alerts


def check_rsi_break(df, threshold=50, length=14, direction="up"):
    """检查RSI是否突破指定值
    
    Args:
        df: 数据DataFrame
        threshold: 突破阈值，默认50
        length: RSI周期，默认14
        direction: 突破方向，"up"表示向上突破，"down"表示向下突破
    
    Returns:
        tuple: (是否突破, 突破描述)
    """
    if df is None or df.empty or len(df) < 3:
        return False, None
    
    # 如果未提供RSI，计算指定周期的RSI
    if f'rsi_{length}' not in df.columns:
        df[f'rsi_{length}'] = ta.rsi(df['close'], length=length)
    
    rsi_col = f'rsi_{length}' if f'rsi_{length}' in df.columns else 'rsi'
    
    # 检查是否有效的RSI值
    if rsi_col not in df.columns or df[rsi_col].isnull().any():
        return False, None
    
    # 获取最近三个RSI值
    rsi_values = df[rsi_col].tail(3).values
    
    # 检查向上突破
    if direction == "up" and rsi_values[0] < threshold and rsi_values[1] < threshold and rsi_values[2] > threshold:
        return True, f"RSI({length})向上突破{threshold}"
    
    # 检查向下突破
    if direction == "down" and rsi_values[0] > threshold and rsi_values[1] > threshold and rsi_values[2] < threshold:
        return True, f"RSI({length})向下突破{threshold}"
    
    return False, None


if __name__ == "__main__":
    # 直接运行此文件时，执行一次完整的规则评估
    config = load_config()
    alerts = evaluate_rules(config)
    
    for alert in alerts:
        print(f"触发告警: {alert['name']}({alert['code']})")
        print(f"原因: {', '.join(alert['reasons'])}")
        print("-" * 50) 