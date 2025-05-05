# 股票信号监控系统

股票信号监控系统是一个帮助投资者追踪股票价格和关键技术指标的工具。

## 项目架构

本项目采用前后端分离架构：

- 前端：基于Vue.js 3构建，位于`frontend`目录
- 后端：基于Flask的RESTful API，提供数据和业务逻辑处理，位于`backend`目录

## 目录结构

```
stock-monitor/
├── backend/             # 后端代码
│   ├── api.py           # API服务
│   ├── monitor.py       # 业务逻辑
│   ├── requirements.txt # 后端依赖
│   ├── static/          # 静态资源
│   └── monitor_config.json # 配置文件
├── frontend/            # 前端代码
│   ├── public/          # 静态资源
│   ├── src/             # 源代码
│   └── package.json     # 前端依赖
├── frontend-dist/       # 前端构建输出目录
├── setup.sh             # Linux/Mac安装脚本
├── setup.bat            # Windows安装脚本
├── start_backend.sh     # Linux/Mac后端启动脚本 
├── start_backend.bat    # Windows后端启动脚本
└── README.md            # 项目文档
```

## 安装与运行

### 完整安装（前后端）

1. 克隆或下载项目代码

2. 运行安装脚本

   对于Linux/Mac用户：
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

   对于Windows用户：
   ```
   setup.bat
   ```

   安装脚本会自动检查环境、安装依赖，并启动后端服务。

### 仅启动后端

如果已经完成安装，只想启动后端服务：

对于Linux/Mac用户：
```bash
chmod +x start_backend.sh
./start_backend.sh
```

对于Windows用户：
```
start_backend.bat
```

### 手动安装

#### 后端安装

1. 创建并激活虚拟环境（推荐）

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows
```

2. 安装依赖

```bash
pip install -r backend/requirements.txt
```

3. 启动后端服务

```bash
cd backend
python api.py
```

后端服务将在 http://localhost:5001 上运行。

### API文档

本项目提供基于Swagger/OpenAPI的在线API文档，方便开发者了解和测试接口。

1. 启动API文档服务器：

```bash
cd backend
python api.py
```

2. 访问API文档页面：

在浏览器中打开 http://localhost:5001/api/docs

API文档提供以下功能：
- 所有API端点的详细说明
- 请求参数和响应格式的详细文档
- 在线测试API的功能
- 可下载的OpenAPI规范

更多信息请参考 [API文档说明](/backend/API_DOCS_README.md)

#### 前端安装与构建

1. 进入前端目录

```bash
cd frontend
```

2. 安装依赖

```bash
npm install
```

3. 开发模式运行

```bash
npm run serve
```

4. 构建生产版本

```bash
npm run build
```

构建后的文件将生成在`frontend-dist`目录中，后端服务会自动提供这些文件。

## 主要功能

- 股票价格和技术指标监控
- 多种监控规则：RSI交叉、均线交叉、MACD交叉、价格突破、量价背离等
- 告警通知（企业微信推送）
- 股票数据可视化展示

## 数据来源

- 优先使用AKshare库获取行情数据
- 备选方案：新浪财经API

## 配置文件

系统配置存储在`backend/monitor_config.json`文件中，包含：

- 监控的股票列表
- 监控规则和参数
- 企业微信Webhook配置

## 项目简介

一款面向个人用户的轻量级股票交易信号监控工具，基于 Python、AKshare 与 Streamlit 实现。通过本地 Web 界面灵活配置监控条件，定时获取行情并评估技术指标，满足条件时自动向企业微信机器人推送告警。

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

启动后访问 http://localhost:5001 即可打开监控系统。

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

# 股票监控系统重构文档

## 重构说明

原系统是一个单文件的股票监控系统，所有功能都放在一个大文件中。通过本次重构，我们采用了面向对象和接口实现的方式，将各个规则提取到单独的文件中，使系统更加模块化，更容易扩展和维护。

## 重构结构

重构后的系统结构如下：

```
backend/
├── monitor.py               # 原始监控模块
├── monitor_refactored.py    # 重构后的入口文件
└── rules/                   # 规则包
    ├── __init__.py          # 包初始化文件
    ├── base_rule.py         # 规则基类
    ├── price_rule.py        # 价格相关规则
    ├── volume_rule.py       # 成交量相关规则
    ├── indicator_rule.py    # 技术指标相关规则
    ├── rule_factory.py      # 规则工厂
    └── rule_evaluator.py    # 规则评估器
```

## 主要改进

1. **接口设计**：创建了`BaseRule`抽象基类，定义了规则实现的接口标准
2. **规则模块化**：将各种不同类型的规则分离到不同文件中，便于维护
3. **工厂模式**：实现了`RuleFactory`工厂类，用于创建具体规则实例
4. **评估器**：实现了`RuleEvaluator`类，用于评估规则并生成报告
5. **兼容性**：保持与原有系统的兼容性，不影响已有功能

## 实现细节

### 规则接口 (`BaseRule`)

所有规则都实现了统一的接口，包括:
- `check()` - 检查规则是否满足
- `get_rule_name()` - 获取规则名称
- `validate_params()` - 验证参数是否有效

### 具体规则实现

1. **价格规则**:
   - `PriceAboveRule` - 价格连续高于指定水平
   - `PriceBreakoutRule` - 价格突破指定高点或低点

2. **成交量规则**:
   - `VolumeAboveRule` - 成交量放大规则
   - `VolumeThresholdRule` - 成交量阈值规则

3. **技术指标规则**:
   - `RSICrossRule` - RSI交叉规则
   - `MACrossRule` - 均线交叉规则
   - `MACDRule` - MACD指标规则

### 规则工厂 (`RuleFactory`)

`RuleFactory`负责根据规则类型和参数创建相应的规则实例，支持新旧配置格式。

### 规则评估器 (`RuleEvaluator`)

`RuleEvaluator`负责评估一组规则，并生成告警信息。

## 使用方法

新系统使用方法基本与原系统一致，但提供了更灵活的配置方式：

```python
from monitor_refactored import evaluate_rules

# 加载并评估配置
alerts = evaluate_rules()
```

## 未来扩展

该重构为系统提供了更好的扩展性，可以轻松添加新的规则类型：

1. 创建新的规则类，继承自`BaseRule`
2. 实现必要的接口方法
3. 在`RuleFactory`中注册新规则类

## 参考

- [原始监控模块](backend/monitor.py)
- [重构后的入口](backend/monitor_refactored.py)

