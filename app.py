import streamlit as st
import pandas as pd
import datetime
import json
from monitor import (
    load_config, 
    save_config, 
    evaluate_rules, 
    fetch_data,
    AKSHARE_AVAILABLE
)

# 页面配置
st.set_page_config(
    page_title="股票信号监控系统",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 页面标题
st.title("📈 股票信号监控系统")

# 显示akshare状态
if not AKSHARE_AVAILABLE:
    st.warning("⚠️ AKshare库未安装或版本不兼容，将使用备选数据源（新浪财经API）。部分功能可能受限。")

# 加载配置
config = load_config()

# 初始化会话状态
if 'alert_history' not in st.session_state:
    st.session_state.alert_history = []

# 侧边栏配置部分
st.sidebar.header("⚙️ 系统配置")

# 企业微信Webhook设置
webhook_url = st.sidebar.text_input(
    "企业微信机器人Webhook", 
    value=config.get("wecom_webhook", ""),
    help="填入企业微信机器人的Webhook地址，用于接收告警通知",
    type="password"
)

# 更新配置中的webhook
if webhook_url != config.get("wecom_webhook", ""):
    config["wecom_webhook"] = webhook_url
    save_config(config)

# 添加股票监控配置
st.sidebar.header("📋 添加监控")

with st.sidebar.form("add_stock_form"):
    st.header("添加股票监控")
    
    # 股票基本信息
    st.subheader("股票信息")
    stock_code = st.text_input("股票代码（如: 000001）")
    stock_name = st.text_input("股票名称（可选）", help="留空将使用股票代码作为名称")
    
    # 添加策略名称和类型
    st.subheader("策略设置")
    strategy_name = st.text_input("策略名称", help="给这个监控策略起个名字，例如：建仓策略、加仓策略、清仓策略等")
    strategy_type = st.selectbox(
        "策略类型",
        options=["建仓", "加仓", "减仓", "清仓", "基础监控"],
        index=4,
        help="选择策略类型，不同类型会使用不同的颜色标记"
    )
    
    # 分页显示各种监控条件
    st.subheader("监控条件")
    tabs = st.tabs(["基本条件", "均线交叉", "MACD", "高低点突破", "量价背离", "价格回调"])
    
    # Tab 1: 基本条件
    with tabs[0]:
        # 价格条件
        price_col1, price_col2 = st.columns(2)
        with price_col1:
            price_level = st.number_input(
                "价格突破", 
                min_value=0.0, 
                step=0.01, 
                help="价格突破此水平将触发告警"
            )
        with price_col2:
            consecutive_bars = st.number_input(
                "持续K线数", 
                min_value=1, 
                value=1, 
                help="价格需要连续n个周期站稳才触发"
            )
        
        # 成交量条件
        volume_col1, volume_col2 = st.columns(2)
        with volume_col1:
            volume_multiple = st.number_input(
                "成交量倍数", 
                min_value=0.0, 
                step=0.1, 
                help="当前成交量超过均值的倍数"
            )
        with volume_col2:
            volume_lookback = st.number_input(
                "参考周期数", 
                min_value=1, 
                value=5, 
                help="计算成交量均值的周期数"
            )
        
        # RSI条件
        rsi_check = st.checkbox("启用RSI指标监控", value=False)
        if rsi_check:
            rsi_col1, rsi_col2 = st.columns(2)
            with rsi_col1:
                rsi_overbought = st.number_input(
                    "超买区域", 
                    min_value=50.0, 
                    max_value=100.0, 
                    value=70.0
                )
            with rsi_col2:
                rsi_oversold = st.number_input(
                    "超卖区域", 
                    min_value=0.0, 
                    max_value=50.0, 
                    value=30.0
                )
            
            # 添加RSI突破特定值的选项
            rsi_threshold_check = st.checkbox("启用RSI突破特定值监控", value=False)
            if rsi_threshold_check:
                rsi_threshold_col1, rsi_threshold_col2 = st.columns(2)
                with rsi_threshold_col1:
                    rsi_threshold = st.number_input(
                        "突破值",
                        min_value=0.0,
                        max_value=100.0,
                        value=50.0,
                        help="当RSI从下方突破此值时触发信号"
                    )
                with rsi_threshold_col2:
                    rsi_length = st.number_input(
                        "RSI周期",
                        min_value=1,
                        max_value=50,
                        value=6,
                        help="计算RSI的周期长度"
                    )

    # Tab 2: 均线交叉
    with tabs[1]:
        ma_check = st.checkbox("启用均线交叉监控", value=False)
        if ma_check:
            st.markdown("##### 均线参数设置")
            ma_col1, ma_col2 = st.columns(2)
            with ma_col1:
                fast_ma = st.selectbox(
                    "快速均线",
                    options=["ma5", "ma10", "ma20", "ma60"],
                    index=0,
                    help="选择快速均线（短期均线）"
                )
                st.caption("通常选择周期较短的均线作为快线")
            with ma_col2:
                slow_ma = st.selectbox(
                    "慢速均线",
                    options=["ma5", "ma10", "ma20", "ma60"],
                    index=2,
                    help="选择慢速均线（长期均线）"
                )
                st.caption("通常选择周期较长的均线作为慢线")
            
            # 添加图示说明    
            st.markdown("##### 交叉信号说明")
            col1, col2 = st.columns(2)
            with col1:
                st.info("**金叉信号**：快线从下方穿过慢线，表示可能进入上升趋势")
            with col2:
                st.warning("**死叉信号**：快线从上方穿过慢线，表示可能进入下降趋势")
            
            # 添加常用组合建议
            st.markdown("##### 常用均线组合")
            with st.expander("查看常用均线组合示例"):
                st.markdown("""
                - **短线交易**：MA5 与 MA10
                - **中线交易**：MA10 与 MA20 
                - **长线交易**：MA20 与 MA60
                - **黄金交叉**：MA5 与 MA20（短期和中期的交叉）
                - **经典配置**：MA5, MA10, MA20, MA60 的多重确认
                """)

    # Tab 3: MACD
    with tabs[2]:
        macd_check = st.checkbox("启用MACD指标监控", value=False)
        if macd_check:
            st.markdown("##### MACD指标说明")
            col1, col2 = st.columns(2)
            with col1:
                st.info("**金叉信号**：MACD线从下方穿过信号线，可能预示上涨")
            with col2:
                st.warning("**死叉信号**：MACD线从上方穿过信号线，可能预示下跌")
            
            st.caption("使用默认参数：快线=12，慢线=26，信号线=9")
            
            # 添加MACD指标解释
            with st.expander("MACD指标详细说明"):
                st.markdown("""
                **MACD指标**（Moving Average Convergence/Divergence，移动平均收敛/发散）是由Gerald Appel发明的技术分析指标，用于识别移动平均值之间的变化趋势。
                
                **计算方法：**
                - DIF线：12日EMA减去26日EMA
                - MACD线(DEA线)：DIF线的9日EMA
                - 柱状图：DIF线减去DEA线
                
                **交易信号：**
                - 当DIF线从下向上穿过MACD线时形成金叉（看涨信号）
                - 当DIF线从上向下穿过MACD线时形成死叉（看跌信号）
                - 当柱状图由负变正，表示由空头转为多头
                - 当柱状图由正变负，表示由多头转为空头
                """)

    # Tab 4: 高低点突破
    with tabs[3]:
        breakout_check = st.checkbox("启用价格突破监控", value=False)
        if breakout_check:
            st.markdown("#### 选择突破监控类型")
            breakout_type = st.radio(
                "监控类型",
                ["相对高低点", "指定价格"],
                captions=["监控价格突破前N周期的高低点", "监控价格突破指定的具体价格"],
                horizontal=True
            )
            
            if breakout_type == "相对高低点":
                breakout_periods = st.slider(
                    "回看周期数",
                    min_value=5,
                    max_value=60,
                    value=20,
                    help="在多少个周期内寻找高点和低点"
                )
                st.info("当价格突破指定周期内的最高点或最低点时触发信号")
            else:
                st.markdown("##### 突破价格设置")
                col1, col2 = st.columns(2)
                with col1:
                    high_level = st.number_input(
                        "指定高点价格",
                        min_value=0.0,
                        step=0.01,
                        value=0.0,
                        help="当价格突破此高点时触发信号，设为0表示不监控"
                    )
                    st.caption("价格高于此点位将触发上涨突破信号")
                    
                with col2:
                    low_level = st.number_input(
                        "指定低点价格",
                        min_value=0.0,
                        step=0.01,
                        value=0.0,
                        help="当价格跌破此低点时触发信号，设为0表示不监控"
                    )
                    st.caption("价格低于此点位将触发下跌突破信号")
                
                st.markdown("##### 突破确认设置")
                breakout_consecutive_bars = st.number_input(
                    "连续K线数",
                    min_value=1,
                    value=1,
                    help="价格需要连续突破指定价格多少个周期才触发"
                )
                st.info("至少需要设置一个高点或低点价格。价格需要连续多根K线突破设定价位才会触发提醒。")

    # Tab 5: 量价背离
    with tabs[4]:
        divergence_check = st.checkbox("启用量价背离监控", value=False)
        if divergence_check:
            divergence_window = st.slider(
                "观察窗口",
                min_value=3,
                max_value=20,
                value=5,
                help="量价背离观察窗口大小"
            )
            st.info("当价格上涨但成交量萎缩，或价格下跌但成交量放大时触发背离信号")

    # Tab 6: 价格回调
    with tabs[5]:
        st.write("开始渲染价格回调选项卡")
        
        # 使用会话状态来跟踪复选框状态，但不使用回调函数
        if 'pullback_check_state' not in st.session_state:
            st.session_state.pullback_check_state = False
        
        # 简单的复选框，不使用on_change
        pullback_check = st.checkbox(
            "检查价格回调点", 
            value=st.session_state.pullback_check_state,
            key="pullback_check_debug"
        )
        
        # 手动更新会话状态
        st.session_state.pullback_check_state = pullback_check
        
        st.write(f"pullback_check值: {pullback_check}")
        
        # 使用复选框的值来决定是否显示输入框
        if pullback_check:
            st.write("复选框已选中，正在渲染输入框")
            pullback_price = st.number_input(
                "回调目标价格",
                min_value=0.0,
                step=0.01,
                value=0.0,
                help="价格从高位回调至特定水平且成交量放大",
                key="pullback_price_debug"
            )
            st.write(f"回调价格设置为: {pullback_price}")
            
            pullback_volume_multiple = st.number_input(
                "回调放量倍数",
                min_value=1.0,
                step=0.1,
                value=1.2,
                help="回调时成交量超过过去N日均量的M倍",
                key="pullback_volume_multiple_debug"
            )
            pullback_lookback = st.number_input(
                "回调比较周期数",
                min_value=1,
                value=5,
                help="回调比较的周期数",
                key="pullback_lookback_debug"
            )

    # 添加条件组合方式选项
    st.divider()
    require_all_conditions = st.checkbox(
        "需要全部条件同时满足才触发告警", 
        value=False, 
        help="启用此选项后，只有当所有选中的条件都满足时才会触发告警，否则满足任一条件即触发"
    )
    
    submitted = st.form_submit_button("添加监控")
    
    if submitted and stock_code:
        # 创建股票监控配置项
        stock_config = {
            "code": stock_code,
            "name": stock_name if stock_name else stock_code,
            "strategy_name": strategy_name if strategy_name else "默认策略",
            "strategy_type": strategy_type,
        }
        
        # 添加基本条件配置
        if price_level > 0:
            stock_config["price_level"] = price_level
            stock_config["consecutive_bars"] = consecutive_bars
        
        if volume_multiple > 0:
            stock_config["volume_multiple"] = volume_multiple
            stock_config["volume_lookback"] = volume_lookback
        
        if rsi_check:
            stock_config["check_rsi"] = True
            stock_config["rsi_overbought"] = rsi_overbought
            stock_config["rsi_oversold"] = rsi_oversold
            
            # 添加RSI突破特定值的配置
            if rsi_threshold_check:
                stock_config["check_rsi_threshold"] = True
                stock_config["rsi_threshold"] = rsi_threshold
                stock_config["rsi_length"] = rsi_length
            
        # 添加均线交叉条件
        if ma_check:
            stock_config["check_ma_cross"] = True
            stock_config["fast_ma"] = fast_ma
            stock_config["slow_ma"] = slow_ma
            
        # 添加MACD条件
        if macd_check:
            stock_config["check_macd"] = True
            
        # 添加价格突破条件
        if breakout_check:
            if breakout_type == "相对高低点":
                stock_config["check_price_breakout"] = True
                stock_config["breakout_periods"] = breakout_periods
            else:
                stock_config["check_specific_breakout"] = True
                if high_level > 0:
                    stock_config["high_level"] = high_level
                if low_level > 0:
                    stock_config["low_level"] = low_level
                stock_config["breakout_consecutive_bars"] = breakout_consecutive_bars
        
        # 添加量价背离条件
        if divergence_check:
            stock_config["check_divergence"] = True
            stock_config["divergence_window"] = divergence_window
        
        # 添加价格回调条件
        if pullback_check:
            stock_config["check_pullback"] = True
            stock_config["pullback_price"] = pullback_price
            stock_config["pullback_volume_multiple"] = pullback_volume_multiple
            stock_config["pullback_lookback"] = pullback_lookback
        
        # 添加条件组合方式
        if require_all_conditions:
            stock_config["require_all_conditions"] = True
        
        # 添加到配置并保存
        if "stocks" not in config:
            config["stocks"] = []
        
        # 不再检查是否存在相同代码的配置，允许添加多个
        config["stocks"].append(stock_config)
        st.sidebar.success(f"已添加 {stock_name if stock_name else stock_code} 的 {strategy_name} 策略到监控列表")
        
        save_config(config)

# 主页面 - 当前监控列表
st.header("📊 当前监控列表")

if not config.get("stocks"):
    st.info("还没有添加监控的股票，请在左侧添加")
else:
    # 创建监控列表表格
    stocks_data = []
    for stock in config.get("stocks", []):
        conditions = []
        if stock.get("price_level"):
            conditions.append(
                f"价格 > {stock.get('price_level')} ({stock.get('consecutive_bars', 1)}周期)"
            )
        if stock.get("volume_multiple"):
            conditions.append(f"成交量 > {stock.get('volume_multiple')}倍")
        if stock.get("check_rsi"):
            conditions.append(
                f"RSI超买{stock.get('rsi_overbought', 70)}/超卖{stock.get('rsi_oversold', 30)}"
            )
            # 添加RSI突破特定值的显示
            if stock.get("check_rsi_threshold"):
                conditions.append(
                    f"RSI({stock.get('rsi_length', 14)})突破{stock.get('rsi_threshold', 50)}"
                )
        if stock.get("check_ma_cross"):
            conditions.append(
                f"均线交叉({stock.get('fast_ma', 'ma5')}/{stock.get('slow_ma', 'ma20')})"
            )
        if stock.get("check_macd"):
            conditions.append("MACD金叉/死叉")
        if stock.get("check_price_breakout"):
            conditions.append(f"价格突破({stock.get('breakout_periods', 20)}周期高低点)")
        if stock.get("check_specific_breakout"):
            high_level = stock.get("high_level")
            low_level = stock.get("low_level")
            high_str = f"高点{high_level}" if high_level else ""
            low_str = f"低点{low_level}" if low_level else ""
            both_str = " 和 " if high_level and low_level else ""
            conditions.append(f"价格突破{high_str}{both_str}{low_str}")
        if stock.get("check_divergence"):
            conditions.append(f"量价背离(窗口={stock.get('divergence_window', 5)})")
        if stock.get("check_pullback"):
            conditions.append(f"价格回调至{stock.get('pullback_price', 0)}并放量")
        
        # 显示条件组合方式
        condition_mode = ""
        if stock.get("require_all_conditions", False):
            condition_mode = "【全部条件同时满足】"
        
        # 获取策略名称和类型
        strategy_name = stock.get("strategy_name", "默认策略")
        strategy_type = stock.get("strategy_type", "基础监控")
        
        stocks_data.append({
            "股票代码": stock.get("code"),
            "股票名称": stock.get("name", stock.get("code")),
            "策略类型": strategy_type,
            "策略名称": strategy_name,
            "监控条件": condition_mode + "、".join(conditions),
            "操作": f"{stock.get('code')}_{strategy_name}"  # 修改操作标识，使用代码和策略名组合
        })
    
    stocks_df = pd.DataFrame(stocks_data)
    
    # 自定义渲染删除按钮，使用代码和策略名的组合作为唯一标识
    def make_delete_button(code_strategy):
        code, strategy_name = code_strategy.split("_", 1)
        button_id = f"delete_{code}_{strategy_name}"
        if st.button("❌ 删除", key=button_id):
            # 从配置中删除特定代码和策略名称匹配的项
            code_parts = code_strategy.split("_", 1)
            stock_code = code_parts[0]
            strategy_name = code_parts[1] if len(code_parts) > 1 else ""
            
            # 保留不匹配的项
            new_stocks = []
            for s in config["stocks"]:
                if s.get("code") == stock_code and s.get("strategy_name") == strategy_name:
                    continue  # 跳过要删除的项
                new_stocks.append(s)
            
            config["stocks"] = new_stocks
            save_config(config)
            st.rerun()
    
    # 为不同策略类型定义颜色
    strategy_colors = {
        "建仓": "green",
        "加仓": "blue", 
        "减仓": "orange",
        "清仓": "red",
        "基础监控": "gray"
    }
    
    # 显示表格
    for i, row in stocks_df.iterrows():
        with st.container():
            cols = st.columns([1, 1, 1, 1, 3, 1])
            cols[0].write(row["股票代码"])
            cols[1].write(row["股票名称"])
            
            # 策略类型使用颜色标记
            strategy_type = row["策略类型"]
            color = strategy_colors.get(strategy_type, "gray")
            cols[2].markdown(f"<span style='color:{color};font-weight:bold;'>{strategy_type}</span>", unsafe_allow_html=True)
            
            cols[3].write(row["策略名称"])
            cols[4].write(row["监控条件"])
            make_delete_button(row["操作"])
            st.divider()

# 手动检测按钮
st.header("🔍 手动检测")
check_col1, check_col2 = st.columns([1, 3])
with check_col1:
    if st.button("执行检测", use_container_width=True):
        with st.spinner("正在检测中..."):
            alerts = evaluate_rules(config)
            
            if alerts:
                for alert in alerts:
                    # 构建完整的告警记录
                    alert_record = {
                        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "stock_code": alert["code"],
                        "stock_name": alert["name"],
                        "strategy_name": alert.get("strategy_name", "默认策略"),
                        "strategy_type": alert.get("strategy_type", "基础监控"),
                        "action_display": alert.get("action_display", "监控"),
                        "content": alert["message"]
                    }
                    st.session_state.alert_history.append(alert_record)
                st.success(f"检测完成，发现 {len(alerts)} 个告警")
            else:
                st.info("检测完成，未触发任何告警")

# 修改告警历史显示部分
# 展示告警历史
st.header("📝 告警历史")

if not st.session_state.alert_history:
    st.info("暂无告警记录")
else:
    # 为不同策略类型定义颜色
    alert_colors = {
        "建仓": "green",
        "加仓": "blue", 
        "减仓": "orange",
        "清仓": "red",
        "监控": "gray"
    }
    
    # 倒序显示，最新的在前面
    for alert in reversed(st.session_state.alert_history):
        # 获取策略类型和名称
        strategy_type = alert.get('strategy_type', '基础监控')
        strategy_name = alert.get('strategy_name', '默认策略')
        action_display = alert.get('action_display', '监控')
        color = alert_colors.get(action_display, "gray")
        
        # 创建标题，包含策略信息
        title = f"{alert['time']} - {alert['stock_name']}({alert['stock_code']}) "
        title += f"[<span style='color:{color};font-weight:bold;'>{strategy_name}-{action_display}</span>]"
        
        with st.expander(title, format_func=lambda x: x):
            st.markdown(alert["content"], unsafe_allow_html=True)

# 添加自动检测定时器
st.sidebar.header("⏱️ 自动检测设置")
auto_check = st.sidebar.checkbox("启用自动检测", value=False)
if auto_check:
    check_interval = st.sidebar.slider("检测间隔(分钟)", min_value=1, max_value=60, value=5)
    
    # 显示下次检测时间
    if "last_check_time" not in st.session_state:
        st.session_state.last_check_time = datetime.datetime.now()
    
    next_check_time = st.session_state.last_check_time + datetime.timedelta(minutes=check_interval)
    st.sidebar.write(f"下次检测时间: {next_check_time.strftime('%H:%M:%S')}")
    
    # 检查是否需要执行检测
    current_time = datetime.datetime.now()
    if current_time >= next_check_time:
        with st.spinner("正在执行自动检测..."):
            alerts = evaluate_rules(config)
            if alerts:
                for alert in alerts:
                    st.session_state.alert_history.append(alert)
            
            st.session_state.last_check_time = current_time
            st.rerun()

# 底部数据源说明
st.divider()
data_source = "AKshare" if AKSHARE_AVAILABLE else "新浪财经API(备选数据源)"
st.caption(f"股票信号监控系统 | 数据来源: {data_source} | 刷新时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}") 