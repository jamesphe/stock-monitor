# 股票信号监控系统

## 项目简介

一款面向个人用户的轻量级股票交易信号监控工具，基于 Python、AKshare 与 Streamlit 实现。通过本地 Web 界面灵活配置监控条件，定时获取行情并评估技术指标，满足条件时自动向企业微信机器人推送告警。

## 目录结构

```
├── app.py                 # Streamlit Web 界面入口
├── monitor.py             # 核心逻辑：行情获取、指标计算、告警推送
├── monitor_config.json    # 配置文件：企业微信 Webhook 与监控规则
├── requirements.txt       # 项目依赖
├── .gitignore             # Git 忽略配置
└── README.md              # 项目文档
```

## 功能特性

- **配置灵活**：Web 界面侧边栏管理 Webhook 与监控任务
- **实时行情监控**：定时或手动使用 AKshare 拉取分钟线、日线数据
- **备选数据源**：当 AKshare 不可用时，自动切换至新浪财经 API
- **多条件组合**：支持多种技术指标和条件组合：
  - 价格突破并持稳
  - 日成交量放大
  - RSI 金叉/死叉
  - 均线交叉（支持MA5/10/20/60任意组合）
  - MACD金叉/死叉
  - 突破前期高点/低点
  - 量价背离（价升量缩/价跌量增）
- **即时告警**：满足条件后自动向企业微信机器人发送通知
- **触发日志**：页面展示最近触发记录，便于回溯与分析

## 环境与依赖

- Python 3.7+
- 依赖库：
  ```bash
  pip install -r requirements.txt
  ```

### 依赖兼容性说明

由于 AKshare 版本更新频繁，如果安装时遇到依赖兼容性问题（如 aiohttp 版本冲突），系统会自动切换到备选数据源（新浪财经 API）。这不会影响基本功能，但可能在股票代码格式和数据量方面有所限制。

## 配置说明

1. 在项目根目录创建或编辑 `monitor_config.json`：
   ```json
   {
     "wecom_webhook": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY",
     "stocks": []
   }
   ```
2. 启动后在侧边栏填入 Webhook 地址，并通过表单添加监控规则，配置会自动保存。

## 快速启动

```bash
git clone <仓库地址>
cd <项目目录>
pip install -r requirements.txt
streamlit run app.py
```

浏览器访问 `http://localhost:8501`，即可开始配置与监控。

## 模块概览

### monitor.py
- **load_config / save_config**：读取与存储 JSON 配置
- **fetch_data / fetch_data_alternative**：使用 AKshare 或新浪财经 API 获取行情
- **条件判断函数**：
  - `check_price_above`：价格突破判断
  - `check_volume_above`：成交量放大判断
  - `check_rsi_cross`：RSI指标金叉/死叉判断
  - `check_ma_cross`：均线交叉判断
  - `check_macd_cross`：MACD金叉/死叉判断
  - `check_price_breakout`：价格突破前期高低点判断
  - `check_volume_price_divergence`：量价背离判断
- **evaluate_rules**：遍历并评估所有监控规则
- **send_wecom**：调用企业微信 Webhook 推送告警消息

### app.py
- 基于 Streamlit 构建的本地 Web 界面
- 侧边栏：全局设置与监控任务表单（使用标签页组织不同类型的监控条件）
- 主区域：当前监控列表、手动检测按钮与触发日志展示

## 部署方式

- **本地运行**：按照快速启动步骤执行
- **VPS 部署**：可结合 `cron` 或 Supervisor 定时调用 `monitor.py`
- **Docker（可选）**：
  ```dockerfile
  FROM python:3.9-slim
  WORKDIR /app
  COPY . .
  RUN pip install -r requirements.txt
  EXPOSE 8501
  CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.enableCORS=false"]
  ```

## 常见问题

### AKshare 安装失败
如果 AKshare 安装失败或版本不兼容，系统会自动使用新浪财经 API 作为备选数据源。在 Web 界面上会显示相应提示。

### 股票代码格式
- 支持带市场前缀的股票代码，如 `sh600000`
- 也支持不带前缀的代码，如 `600000`（系统会自动识别上交所/深交所）

## 监控条件详解

### 基本条件
- **价格突破**：股票价格突破设定价格，并可设置需要持续多少个周期
- **成交量放大**：当前成交量超过过去N日均量的M倍
- **RSI指标**：支持检测RSI从超卖区上穿或从超买区下穿

### 技术分析条件
- **均线交叉**：支持MA5/10/20/60任意两条均线的金叉或死叉信号
- **MACD指标**：检测MACD线与信号线的金叉或死叉
- **价格突破**：检测价格是否突破前N周期的最高点或最低点
- **量价背离**：检测价格上涨但成交量萎缩，或价格下跌但成交量放大的背离信号

## 后续迭代规划

- 引入历史回测功能以评估监控配置效果
- 支持多渠道通知（短信、邮件、钉钉等）
- 持久化日志至数据库并完善异常处理
- 添加权限管理与团队协作功能

